from flask import Flask, request
from types import SimpleNamespace
import logging
import os
import json

from modules.create_issue import createIssue
from modules.gather_info import getRepoInfo
from modules.git_initialize import initializeNewRep
from modules.create_branchrules import createBranchProtectionRule


app = Flask(__name__)

# Listen to organization events from GitHub
@app.route('/webhookReceived', methods=['POST'])
def webhookReceived():
    # Necessary Variables That Can Be Modified
    TOKEN = os.environ.get("GH_AUTH_TOKEN")
    readMeFileToAdd = 'README.md'
    contentsOfReadMe = '# Auto Generated README'
    assignedUser = 'klsember'
    logFileName = 'auto-create-branch-rules.log'

    # Create log file
    logging.basicConfig(filename=logFileName,level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    
    # Default variables to connect to GitHub GraphQL API
    headers = {
            'Authorization': 'Bearer {}'.format( TOKEN ),
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type' : 'application/json'
        }
    queryURL = 'https://api.github.com/graphql'
    
    webhookEvent = request.headers.get('X-GitHub-Event')
    payloadData = request.json;
    
    # Confirm the request has a json value
    if payloadData is None:
        logging.warning('There was an issue accessing the Payload from the GitHub event.')
    # 
    try:    
        if webhookEvent == 'repository' and payloadData['action'] == 'created':
            
            newRepoName = payloadData.get('repository').get('name')
            ownerName = payloadData.get('repository').get('owner').get('login')
            
            logging.info('A new repository {} has been added to {}.'.format(newRepoName, ownerName))
            
            ## Querying for necessary information from newly created repo
            repoResponse = getRepoInfo(ownerName, newRepoName, queryURL, headers)
            if repoResponse.status_code == 200:
                logging.info('Successfully able to query GraphQL API with status code: {}'.format(repoResponse.status_code))
            else:
                logging.error('Error searching for newly created respository, received status code: {}'.format(repoResponse.status_code))
            

            # Identify necessary values from API results to create branch 
            # protection rules if the default branch exists
            apiResults = json.dumps(repoResponse.json())
            resultsObject = json.loads(apiResults, object_hook=lambda d: SimpleNamespace(**d)).data.repository
            repositoryId = resultsObject.id
                    
            if resultsObject.defaultBranchRef is not None:
                defaultBranch = resultsObject.defaultBranchRef.name
                logging.info('The default branch for the repository is {}'.format(defaultBranch))
            else:
                defaultBranch = 'main'
                logging.info('No default branch exists for the new repository and needs to be initialized.')
                # Assuming that all new initialized repos will create a README from main as default branch
                repoResponse = initializeNewRep(ownerName, newRepoName, defaultBranch,readMeFileToAdd, contentsOfReadMe, headers)
                if repoResponse.status_code == 201:
                    logging.info('Successfully created a new commit and file with status code: {}'.format(repoResponse.status_code))
                else:
                    logging.error('Error when committing to repository, received status code: {}'.format(repoResponse.status_code))
                
            # Create Branch Protection rule for default branch
            pbresponse = createBranchProtectionRule(repositoryId, defaultBranch, queryURL, headers)
            if pbresponse.status_code == 200:
                logging.info('Branch Protection Policy for {} successfully created with status code: {}'.format(defaultBranch, pbresponse.status_code))
                
                # Assign Necessary Variables to pass to Issue's Body and hacky way to clean up the message
                bpResults = json.dumps(pbresponse.json())
                bpObjects = json.loads(bpResults, object_hook=lambda d: SimpleNamespace(**d))
                rules = str(bpObjects.data.createBranchProtectionRule.branchProtectionRule)\
                    .replace(', ','| \r\n| `')\
                    .replace('=','` | ')
                messageBR = rules[rules.find("(")+1:rules.find(")")]

                # Confirm that hasIssuesEnabled is set to true before proceeding
                if resultsObject.hasIssuesEnabled:                    
                
                    # Create new Issue in Assigned Repository, with branch protection rules created for 
                    # the default branch, and notified user with a @mention
                    issueResponse = createIssue(repositoryId, defaultBranch, assignedUser, messageBR, queryURL, headers)
                    if issueResponse.status_code == 200:
                        logging.info('Successfully created new issue with status code: {}'.format(issueResponse.status_code))
                    else:
                        logging.error('There was a problem creating a new issue, received status code {}'.format(issueResponse.status_code))
                else:
                    logging.warning('Unable to create issue because the feature "Issues" has been disabled for the repository.')
            else:
                logging.error('Branch Policy creation was unsuccessful and failed with status code {}'.format(pbresponse.status_code))
    except KeyError as e:
        logging.info('Received KeyError, with reason {}'.str(e))

    return json.dumps(payloadData)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
