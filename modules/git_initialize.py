import requests
import base64
import json


def initializeNewRep(owner, repo, branch, filename, contents, headers):
    encodedContents = base64.b64encode(contents.encode()).decode('utf-8')

    # Then add intial file to empty trepository to initialize
    createFileUrl='https://api.github.com/repos/{}/{}/contents/{}'.format(owner, repo, filename)
    
    message = {
        'message': 'Auto Create README',
        'branch': branch,
        'content': encodedContents
        }
    messageDump = json.dumps(message)
    resp=requests.put(createFileUrl, data = messageDump, headers=headers)
    
    return resp