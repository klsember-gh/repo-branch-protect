import requests

def createBranchProtectionRule(repositoryId, defaultBranch, queryURL, headers):
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
    bprotectRules = {
        'repositoryId': repositoryId,
        'defaultBranch': defaultBranch
    }

    # Call API to Create Branch Protection Policy for Default Branch
    response = requests.post(queryURL, json={'query': createBranchProtection, 'variables': bprotectRules}, headers=headers)
    return response