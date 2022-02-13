import requests


def create_issue(repositoryid, defaultbranch, user, branchrules, query_url, headers):
    issue_mutate = """mutation ($repositoryId: ID!, $title: String!, $body: String) {
        createIssue(input: {repositoryId: $repositoryId, title: $title, body: $body}) {
            issue {
                number
                body
            }
        }
        }"""
    issue_variables = {
            'repositoryId': repositoryid,
            'title': 'Branch Protection Rules Created for Default Branch {}'.format(defaultbranch),
            'body': '@{} created a new branch policy for `{}` with the following rules: \r\n | Branch Protection Rule | Value |\r\n |----------|-------| \r\n |`{}|'.format(user, defaultbranch, branchrules)
        }

    # Call API to Create Issue After Successful Branch Policy Creation
    issue_response = requests.post(query_url, json={'query': issue_mutate, 'variables': issue_variables}, headers=headers)
    return issue_response
