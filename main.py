from flask import Flask, request
from types import SimpleNamespace
import os
import json

from modules.create_issue import createIssue
from modules.gather_info import getRepoInfo
from modules.git_initialize import initializeNewRep
from modules.create_branchrules import createBranchProtectionRule


# Necessary Variables That Can Be Modified
TOKEN = os.environ.get("GH_AUTH_TOKEN")
readMeFileToAdd = 'README.md'
contentsOfReadMe = '# Auto Generated README'
assignedUser = 'klsember'


# Default variables to connect to GitHub GraphQL API
headers = {
        'Authorization': 'Bearer {}'.format( TOKEN ),
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type' : 'application/json'
    }
queryURL = 'https://api.github.com/graphql'

app = Flask(__name__)


@app.route('/webhookReceived', methods=['POST'])
def webhookReceived():
    webhookEvent = request.headers.get('X-GitHub-Event')
    payloadData = request.json;
    if webhookEvent == 'repository' and payloadData['action'] == 'created':
        
        newRepoName = payloadData.get('repository').get('name')
        ownerName = payloadData.get('repository').get('owner').get('login')
        
        print('A new repository ', newRepoName, ' has been added to ', ownerName)
        
        ## Querying for necessary information from newly created repo
        repoResponse = getRepoInfo(ownerName, newRepoName, queryURL, headers)
        if repoResponse.status_code == 200:
            print('Successfully able to query GraphQL API with status code: ', repoResponse.status_code)
        else:
            print('Error searching for newly created respository, received status code: ', repoResponse.status_code)
        

        # Identify necessary values from API results to create branch 
        # protection rules if the default branch exists
        apiResults = json.dumps(repoResponse.json())
        resultsObject = json.loads(apiResults, object_hook=lambda d: SimpleNamespace(**d))
        repositoryId = resultsObject.data.repository.id
        
        #defaultBranchRef = resultsObject.data.repository.defaultBranchRef
        
        if resultsObject.data.repository.defaultBranchRef is not None:
            defaultBranch = resultsObject.data.repository.defaultBranchRef.name
            print('The default branch for the repository is ', defaultBranch)
        else:
            defaultBranch = 'main'
            print('No default branch exists for the new repository and needs to be initialized.')
            # Assuming that all new initialized repos will create a README from main as default branch
            repoResponse = initializeNewRep(ownerName, newRepoName, defaultBranch,readMeFileToAdd, contentsOfReadMe, headers)
            if repoResponse.status_code == 201:
                print('Successfully created a new commit and file with status code: ', repoResponse.status_code)
            else:
                print('Error when committing to repository, received status code: ', repoResponse.status_code)
            
        # Create Branch Protection rule for default branch
        pbresponse = createBranchProtectionRule(repositoryId, defaultBranch, queryURL, headers)
        if pbresponse.status_code == 200:
            print('Branch Protection Policy for ', defaultBranch, ' successfully created with status code ', pbresponse.status_code)
            
            # Assign Necessary Variables to pass to Issue's Body
            bpResults = json.dumps(pbresponse.json())
            bpObjects = json.loads(bpResults, object_hook=lambda d: SimpleNamespace(**d))
            
            # Create new Issue in Assigned Repository, with branch protection rules created for 
            # the default branch, and notified user with a @mention
            issueResponse = createIssue(repositoryId, defaultBranch, assignedUser, "Thisis a placeholder", queryURL, headers)
            if issueResponse.status_code == 200:
                print('Successfully created new issue with status code ', issueResponse.status_code)
            else:
                print('There was a problem creating a new issue, received status code ', issueResponse.status_code)
                print(issueResponse.json())
        else:
            print('Branch Policy creation was unsuccessful and failed with status code ', pbresponse.status_code)
            print(pbresponse.json())
        
    return json.dumps(payloadData)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
