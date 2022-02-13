import requests

def check_import_repo(owner, repo_name, headers):
    import_url = 'https://api.github.com/repos/{}/{}/import'.format(owner, repo_name)

    response=requests.get(import_url, headers=headers)

    return response
