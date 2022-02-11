import requests


def createIssue(repositoryId, defaultbranch, branchrules, queryURL, headers):
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
            'title': 'Branch Protection Rules Created for Default Branch {}'.format(defaultbranch),
            'body': '@klsember created a new branch policy for {} with the following rules: {}'.format(defaultbranch, branchrules)
        }
    
    # Call API to Create Issue After Successful Branch Policy Creation
    issue_response = requests.post(queryURL, json={'query': createIssue, 'variables': issueVariables}, headers=headers)
    return issue_response
