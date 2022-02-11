import requests

def getRepoInfo(ownerName, newRepoName, queryURL, headers):
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
            'owner': ownerName,
            'name': newRepoName
        }
    # TODO: use authenticated sessions
    r = requests.post(queryURL, json={'query': query, 'variables': variables}, headers=headers)
    return r
