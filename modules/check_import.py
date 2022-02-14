#!/usr/bin/env python
import requests

def check_import_repo(owner, repo_name, headers):
    """
    Query REST API and determine if Repository is imported, using the following parameters:
        owner: organization name where the repository was created
        repo_name: Name of the newly created repository
        headers: Necessary headers to call GitHub API
    """

    import_url = 'https://api.github.com/repos/{}/{}/import'.format(owner, repo_name)

    response=requests.get(import_url, headers=headers)

    return response
