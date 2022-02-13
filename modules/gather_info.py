import logging
import requests

def get_repo_info(owner_name, new_repo_name, query_url, headers):
    """
    Query GraphQL API to get new repository information:
        owner_name: organization name where the new repository was created
        new_repo_name: Name of the new repository created
        query_url: The GitHub API to POST to
        headers: Necessary headers to call GitHub API
    """
    query = """query ($owner: String!, $name: String!) {
            repository(owner: $owner, name: $name) {
                id
                hasIssuesEnabled
                isPrivate
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
            'owner': owner_name,
            'name': new_repo_name
        }
    response = requests.post(query_url, json={'query': query, 'variables': variables}, headers=headers)

    if response.ok:
        logging.info(f'Successfully able to query GraphQL API with status code: {response.status_code}. (URL: {query_url})')
    else:
        logging.error(f'Error searching for newly created repository, received status code: {response.status_code}. (URL: {query_url})')

    return response
