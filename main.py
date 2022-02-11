from flask import Flask, request, Response
import os
import json
import requests


# TODO: Remove the test variables
TOKEN = os.environ.get("GH_AUTH_TOKEN")
# ownerName = 'circleci-ksember'
# newRepoName = 'test-android'

# Default variables to connect to GitHub GraphQL API
headers = {
        'Authorization': 'Bearer %s' % TOKEN ,
        'Accept': 'application/vnd.github.v3+json'
    }
queryURL = 'https://api.github.com/graphql'

app = Flask(__name__)


@app.route('/webhookReceived', methods=['POST'])
def webhookReceived():
    webhookEvent = request.headers.get('X-GitHub-Event')
    payloadData = request.json;
    if webhookEvent == 'repository' and payloadData['action'] == 'created':
        newRepoName = payloadData['repository']['name']
        ownerName = payloadData['repository']['owner']['login']
        
        print('A new repository ', newRepoName, ' has been added to ', ownerName)
        
        ## Querying for necessary information from newly created repo
        query = """query ($owner: String!, $name: String!) {
                repository(owner: $owner, name: $name) {
                    id
                    nameWithOwner
                    description
                    url
                    owner {
                        login
                    }
                    name
                    defaultBranchRef {
                        id
                        name
                    }
                    branchProtectionRules(first: 10) {
                        nodes {
                            id
                            pattern
                            restrictsPushes
                            requiresStatusChecks
                            requiresLinearHistory
                            requiresCodeOwnerReviews
                            requiresApprovingReviews
                            requiresCommitSignatures
                            restrictsReviewDismissals
                            requiresStrictStatusChecks
                            allowsForcePushes
                            isAdminEnforced
                            requiresConversationResolution
                            dismissesStaleReviews
                            allowsDeletions
                            requiredApprovingReviewCount
                        }
                    }
                }
            }"""
        variables = {
                'owner': ownerName,
                'name': newRepoName
            }
        r = requests.post(queryURL, json={'query': query, 'variables': variables}, headers=headers)
        
        if r.status_code == 200:
            print('Successfully able to query GraphQL API with status code: ', r.status_code)
        else:
            print('Error searching for newly created respository, received status code: ', r.status_code)
        
        apiResults = r.json()
        
        # Identify necessary values from API results to create branch 
        # protection rules if the default branch exists
        repositoryId = apiResults.get('data').get('repository').get('id')
        
        defaultBranchRef = apiResults.get('data').get('repository').get('defaultBranchRef')
        if defaultBranchRef is not None:
            defaultBranch = defaultBranchRef['name']
            print('The default branch for the repository is ' + defaultBranch)
        else:
            defaultBranch = defaultBranchRef
            print('No default branch exists for the new repository and needs to be initialized.')

        # Create Branch Protection rule for default branch
        createBranchProtection = """mutation ($repositoryId: ID!, $defaultBranch: String!) {
            createBranchProtectionRule(input: {repositoryId: $repositoryId, 
                allowsDeletions: false, 
                pattern: $defaultBranch,
                isAdminEnforced: true, 
                requiresCodeOwnerReviews: true, 
                requiresConversationResolution: true, 
                requiresApprovingReviews: true,
                allowsForcePushes: false,
                requiresCommitSignatures: true,
                requiresStatusChecks: true}) {
                branchProtectionRule{
                    id
                    pattern
                    restrictsPushes
                    requiresStatusChecks
                    requiresLinearHistory
                    requiresCodeOwnerReviews
                    requiresApprovingReviews
                    requiresCommitSignatures
                    restrictsReviewDismissals
                    requiresStrictStatusChecks
                    allowsForcePushes
                    isAdminEnforced
                    requiresConversationResolution
                    dismissesStaleReviews
                    allowsDeletions
                    requiredApprovingReviewCount
                    }
                }
            }"""
        bprotectRules = {
                'repositoryId': repositoryId,
                'defaultBranch': defaultBranch
            }
        
        # Call API to Create Branch Protection Policy for Default Branch
        branchprotection_response = requests.post(queryURL, json={'query': createBranchProtection, 'variables': bprotectRules}, headers=headers)
        
        if branchprotection_response.status_code == 200:
            print('Branch Protection Policy for ', defaultBranch, ' successfully created with status code ', branchprotection_response.status_code)
            
            # Create new Issue in Assigned Repository, with branch protection rules created for 
            # the default branch, and notified user with a @mention
            createIssue = """mutation ($repositoryId: ID!, $title: String!, $body: String) {
                createIssue(input: {repositoryId: $repositoryId, title: $title, body: $body}) {
                    issue {
                        number
                        body
                    }
                }
                }"""
            issueVariables = {
                    'repositoryId': repositoryId,
                    'title': 'Branch Protection Rules Created for Default Branch ' + defaultBranch,
                    'body': '@klsember created a new branch policy for' + defaultBranch + 'with the following'
                }
            
            # Call API to Create Issue After Successful Branch Policy Creation
            issue_response = requests.post(queryURL, json={'query': createIssue, 'variables': issueVariables}, headers=headers)
            
            if issue_response.status_code == 200:
                print('Successfully created new issue with status code ', issue_response.status_code)
            else:
                print('There was a problem creating a new issue, received status code ', issue_response.status_code)
                print(issue_response.json())
        
        else:
            print('Branch Policy creation was unsuccessful and failed with status code ', branchprotection_response.status_code)
            print(branchprotection_response.json())
        
    return json.dumps(payloadData)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
