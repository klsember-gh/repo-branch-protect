"""A dummy docstring."""

import logging
import os
import json
from types import SimpleNamespace
from flask import Flask, request

from modules.create_issue import create_issue
from modules.gather_info import get_repo_info
from modules.git_initialize import initialize_new_repo
from modules.create_branchrules import create_branch_protection_rule


app = Flask(__name__)

# Necessary Variables That Can Be Modified
gh_token = os.environ.get('GH_AUTH_TOKEN')
README_FILE_ADD = 'README.md'
CONTENTS_OF_README = '# Auto Generated README'
ASSIGNED_USER = 'klsember'
LOG_FILENAME = 'auto-create-branch-rules.log'

# Listen to organization events from GitHub
@app.route('/webhookReceived', methods=['POST'])
def webhook_received():
    """Listen for Org Events and create branch protection rules for new repos"""

    # Create log file
    logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    # Default variables to connect to GitHub GraphQL API
    headers = {
            'Authorization': 'Bearer {}'.format( gh_token ),
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type' : 'application/json'
        }
    query_url = 'https://api.github.com/graphql'

    webhook_event = request.headers.get('X-GitHub-Event')
    payload_data = request.json

    # Confirm the request has a json value
    if payload_data is None:
        logging.warning('There was an issue accessing the Payload from the GitHub event.')

    try:
        if webhook_event == 'repository' and payload_data['action'] == 'created':

            new_repo_name = payload_data.get('repository').get('name')
            owner_name = payload_data.get('repository').get('owner').get('login')

            logging.info(f'A new repository {new_repo_name} has been added to {owner_name}.')

            ## Querying for necessary information from newly created repo
            repo_response = get_repo_info(owner_name, new_repo_name, query_url, headers)
            if repo_response.status_code == 200:
                logging.info(f'Successfully able to query GraphQL API with status code: {repo_response.status_code}')
            else:
                logging.error(f'Error searching for newly created respository, received status code: {repo_response.status_code}')

            # Identify necessary values from API results to create branch
            # protection rules if the default branch exists
            api_results = json.dumps(repo_response.json())
            results_object = json.loads(api_results, object_hook=lambda d: SimpleNamespace(**d))\
                                .data.repository
            repo_id = results_object.id

            if results_object.defaultBranchRef is not None:
                default_branch = results_object.defaultBranchRef.name
                logging.info(f'The default branch for the repository is {default_branch}')
            else:
                default_branch = 'main'
                logging.info('No default branch exists for the new repository and needs to be initialized.')
                # Assuming that all new initialized repos will create a README from main as default branch
                new_response = initialize_new_repo(owner_name, new_repo_name, default_branch, README_FILE_ADD, CONTENTS_OF_README, headers)
                if repo_response.status_code == 201:
                    logging.info(f'Successfully created a new commit and file with status code: {new_response.status_code}')
                else:
                    logging.error(f'Error when committing to repository, received status code: {new_response.status_code}')

            # Create Branch Protection rule for default branch
            pbresponse = create_branch_protection_rule(repo_id, default_branch, query_url, headers)
            if pbresponse.status_code == 200:
                logging.info(f'Branch Protection Policy for {default_branch} successfully created with status code: {pbresponse.status_code}')

                # Assign Necessary Variables to pass to Issue's Body and hacky way to clean up the message
                bp_results = json.dumps(pbresponse.json())
                bp_objects = json.loads(bp_results, object_hook=lambda d: SimpleNamespace(**d))
                rules = str(bp_objects.data.createBranchProtectionRule.branchProtectionRule)\
                    .replace(', ','| \r\n| `')\
                    .replace('=','` | ')
                message_brules = rules[rules.find("(")+1:rules.find(")")]

                # Confirm that hasIssuesEnabled is set to true before proceeding
                if results_object.hasIssuesEnabled:

                    # Create new Issue in Assigned Repository, with branch protection rules created for
                    # the default branch, and notified user with a @mention
                    issue_response = create_issue(repo_id, default_branch, ASSIGNED_USER, message_brules, query_url, headers)
                    if issue_response.status_code == 200:
                        logging.info(f'Successfully created new issue with status code: {issue_response.status_code}')
                    else:
                        logging.error(f'There was a problem creating a new issue, received status code {issue_response.status_code}')
                else:
                    logging.warning('Unable to create issue because the feature "Issues" has been disabled for the repository.')
            else:
                logging.error(f'Branch Policy creation was unsuccessful and failed with status code {pbresponse.status_code}')
    except KeyError as err:
        logging.info(f'Received KeyError, with reason {str(err)}')

    return json.dumps(payload_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
