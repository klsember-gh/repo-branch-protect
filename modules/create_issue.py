import logging
import requests

def create_issue(repository_id, title, message_body, query_url, headers):
    issue_mutate = """mutation ($repositoryId: ID!, $title: String!, $body: String) {
        createIssue(input: {repositoryId: $repositoryId, title: $title, body: $body}) {
            issue {
                number
                body
            }
        }
        }"""

    issue_variables = {
            'repositoryId': repository_id,
            'title': title,
            'body': message_body
        }

    # Call API to Create Issue After Successful Branch Policy Creation
    issue_response = requests.post(query_url, json={'query': issue_mutate, 'variables': issue_variables}, headers=headers)

    if issue_response.status_code == 200:
        logging.info(f'Successfully created new issue with status code: {issue_response.status_code}')
    else:
        logging.error(f'There was a problem creating a new issue, received status code {issue_response.status_code}')

    return issue_response
