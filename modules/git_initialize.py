import base64
import json
import requests


def initialize_new_repo(owner, repo, branch, filename, contents, headers):
    encoded_contents = base64.b64encode(contents.encode()).decode('utf-8')

    create_file_url='https://api.github.com/repos/{}/{}/contents/{}'.format(owner, repo, filename)

    message = {
        'message': 'Auto Create README',
        'branch': branch,
        'content': encoded_contents
        }
    message_dump = json.dumps(message)
    resp=requests.put(create_file_url, data = message_dump, headers=headers)

    return resp
