#!/usr/bin/env python
import logging
import requests

def create_issue(repository_id, title, message_body, query_url, headers):
    """
    Query GraphQL API to create issue in repository:
        repository_id: id of the newly created repository
        title: Title of new issue
        message_body: Body text to add to new issue
        query_url: The GitHub API to POST to
        headers: Necessary headers to call GitHub API
    """
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

    # Call API to Create Issue in Newly Created Repository
    issue_response = requests.post(query_url, json={'query': issue_mutate, 'variables': issue_variables}, headers=headers)

    if issue_response.ok:
        logging.info(f'Successfully created new issue with status code: {issue_response.status_code}. (URL: {query_url})')
    else:
        logging.error(f'There was a problem creating a new issue, received status code {issue_response.status_code}. (URL: {query_url})')

    return issue_response
