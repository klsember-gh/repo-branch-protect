import base64
import json
import logging
import requests

def initialize_new_repo(branch, contents_url, filename, contents, headers):
    """
    Query GraphQL API to commit to empty newly created repository:
        branch: Branch name to PUT commit to
        contents_url: Associated REST API to PUT to
        filename: Name of the file and path that are to be committed to the branch
        contents: Contents of the file to be converted to base64 and committed
        headers: Necessary headers to call GitHub API
    """
    encoded_contents = base64.b64encode(contents.encode()).decode('utf-8')
    query_url = contents_url.format_map({'+path' : filename})

    message = {
        'message': 'Auto Create README',
        'branch': branch,
        'content': encoded_contents
        }
    message_dump = json.dumps(message)
    response=requests.put(query_url, data = message_dump, headers=headers)

    if response.ok:
        logging.info(f'Successfully created a new commit and file with status code: {response.status_code}. (URL: {query_url})')
    else:
        logging.error(f'Error when committing to repository, received status code: {response.status_code}. (URL: {query_url})')

    return response
