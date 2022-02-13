import base64
import json
import logging
import requests


def initialize_new_repo(branch, contents_url, filename, contents, headers):
    encoded_contents = base64.b64encode(contents.encode()).decode('utf-8')

    message = {
        'message': 'Auto Create README',
        'branch': branch,
        'content': encoded_contents
        }
    message_dump = json.dumps(message)
    response=requests.put(contents_url.format_map({'+path' : filename}), data = message_dump, headers=headers)
    if response.status_code == 201:
        logging.info(f'Successfully created a new commit and file with status code: {response.status_code}')
    else:
        logging.error(f'Error when committing to repository, received status code: {response.status_code}')

    return response
