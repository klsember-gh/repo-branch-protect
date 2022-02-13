import requests

def get_repo_info(owner_name, new_repo_name, query_url, headers):
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
    return response
