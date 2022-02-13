import requests

def create_branch_protection_rule(repository_id, default_branch, query_url, headers):
    """
    Query GraphQL API to create new branch protection rules:
        repository_id: id of the newly created repository
        default_branch: Name of the default branch the policy pattern will apply to
        query_url: The GitHub API to POST to
        headers: Necessary headers to call GitHub API
    """
    create_branch_protection = """mutation ($repositoryId: ID!, $defaultBranch: String!) {
    createBranchProtectionRule(input: {repositoryId: $repositoryId, 
        allowsDeletions: false, 
        pattern: $defaultBranch,
        isAdminEnforced: true, 
        requiresCodeOwnerReviews: true, 
        requiresConversationResolution: true, 
        requiresApprovingReviews: true,
        allowsForcePushes: false,
        requiresCommitSignatures: true,
        requiresStatusChecks: true,
        requiredApprovingReviewCount: 2,
        dismissesStaleReviews: true}) {
        branchProtectionRule{
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
    bprotect_rules = {
        'repositoryId': repository_id,
        'defaultBranch': default_branch
    }

    # Call API to Create Branch Protection Policy for Default Branch
    response = requests.post(query_url, json={'query': create_branch_protection, 'variables': bprotect_rules}, headers=headers)

    return response
