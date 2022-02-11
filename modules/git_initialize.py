#!/usr/bin/env python3

from secrets import token_hex
import requests
import base64
import json


def initializeNewRep(owner, repo, branch, filename, contents, headers):
    encodedContents = base64.b64encode(contents.encode())

    # Then add intial file to empty trepository to initialize
    createFileUrl='https://api.github.com/repos/{}/{}/contents/{}'.format(owner, repo, filename)
    
    message = {
        'path': 'README.md',
        'message': 'Auto Create README',
        'branch': branch,
        'content': 'IyBBdXRvIEdlbmVyYXRlZCBSRUFETUU='
        }
    messageDump = json.dumps(message)
    resp=requests.put(createFileUrl, data = messageDump, headers = headers)
    
    return resp