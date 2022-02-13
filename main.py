import logging
import os
import json
from types import SimpleNamespace
from flask import Flask, request

from modules.create_issue import create_issue
from modules.check_import import check_import_repo
from modules.gather_info import get_repo_info
from modules.git_initialize import initialize_new_repo
from modules.create_branchrules import create_branch_protection_rule


app = Flask(__name__)

# Necessary Variables That Can Be Modified
gh_token = os.environ.get('GH_AUTH_TOKEN')
README_FILE_ADD = 'README.md'
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
    webhook_event_delivery =  request.headers.get('X-GitHub-Delivery')
    payload_data = request.json

    # Confirm the request has a json value

    if payload_data is None:
        logging.error('There was an issue accessing the Payload from the GitHub event.')
        raise Exception(f'There was an issue with the the webhook request {webhook_event_delivery}.')

    try:
        if webhook_event == 'repository' and payload_data['action'] == 'created':

            new_repo_name = payload_data.get('repository').get('name')
            owner_name = payload_data.get('repository').get('owner').get('login')
            contents_url = payload_data.get('repository').get('contents_url')
            org_default_branch = payload_data.get('repository').get('default_branch')

            logging.info(f'A new repository {new_repo_name} has been added to {owner_name}.')

            ## Querying for necessary information from newly created repo
            try:
                repo_response = get_repo_info(owner_name, new_repo_name, query_url, headers)

                # Identify necessary values from API results to create branch
                # protection rules if the default branch exists
                api_results = json.dumps(repo_response.json())
                results_object = json.loads(api_results, object_hook=lambda d: SimpleNamespace(**d)).data.repository
                repo_id = results_object.id

                if results_object.defaultBranchRef is not None:
                    default_branch = results_object.defaultBranchRef.name
                    logging.info(f'The default branch for the repository is {default_branch}')
                else:
                    default_branch = org_default_branch
                    logging.info('No default branch exists for the new repository and needs to be initialized.')

                    # Check if missing default branch is because the repository is trying to be imported
                    import_response = check_import_repo(owner_name, new_repo_name, headers)

                    if import_response.status_code == 404:
                        logging.info(f'The repo {new_repo_name} is not being imported, proceeding with committing to the {default_branch} branch.')

                        # Assuming that all new initialized repos will create a README from main as default branch
                        contents_of_readme = '# {} \r\n Auto-generated readme file for empty repository.'.format(new_repo_name)
                        initialize_new_repo(default_branch, contents_url, README_FILE_ADD, contents_of_readme, headers)

                    elif import_response.ok:
                        import_status = import_response.json().get('status')
                        import_from = import_response.json().get('vcs_url')

                        logging.info(f'The repo {new_repo_name} is being imported, with a status of {import_status}.')
                        logging.info('Skipping the initialization of the new repo.')
                        logging.info('Creating issue to confirm that repository import was successful.')
                        if results_object.hasIssuesEnabled:
                            title = 'Imported Repo Notification'
                            message = f"""@{ASSIGNED_USER} - repository was to be imported from {import_from}, please confirm import was successful.
                                    \r\n \r\n **NOTE:** Branch Protection Rules will still be created
                                    for the default branch even if the import is canceled."""
                            create_issue(repo_id, title, message, query_url, headers)
                        else:
                            logging.info('Issues is not enabled for this repository.')
                    else:
                        raise Exception("There was a problem validating if the repository was imported - exited with status code {import_response.status_code}.")

                # Create Branch Protection rule for default branch
                pb_response = create_branch_protection_rule(repo_id, default_branch, query_url, headers)
                if pb_response.ok:
                    logging.info(f'Branch Protection Policy for {default_branch} successfully created with status code: {pb_response.status_code}. (URL: {query_url})')

                    # Assign Necessary Variables to pass to Issue's Body and hacky way to clean up the message
                    bp_results = json.dumps(pb_response.json())
                    bp_objects = json.loads(bp_results, object_hook=lambda d: SimpleNamespace(**d))

                    # Generating markdown table syntax of branch protection rules to include in issue body
                    rules = str(bp_objects.data.createBranchProtectionRule.branchProtectionRule)\
                        .replace(', ','| \r\n| `')\
                        .replace('=','` | ')
                    message_brules = rules[rules.find("(")+1:rules.find(")")]

                    if results_object.hasIssuesEnabled:

                        # Create new Issue in Assigned Repository, with branch protection rules in markdown table format, created for
                        # the default branch, and notified user with a @mention
                        title = f'Branch Protection Rules Created for Default Branch {default_branch}'
                        message = f"""@{ASSIGNED_USER} created a new branch policy for `{default_branch}` with the following rules:
                            \r\n | Branch Protection Rule | Value |\r\n |----------|-------| \r\n |`{message_brules}|"""

                        create_issue(repo_id, title, message, query_url, headers)
                    else:
                        logging.warning('Unable to create issue because the feature "Issues" has been disabled for the repository.')
                else:
                    logging.error(f'Branch Policy creation was unsuccessful and failed with status code {pb_response.status_code}. (URL: {query_url})')

            except KeyError as err:
                logging.error(f'Received KeyError, with reason {str(err)}')

        # Check for repository imports
        else:
            logging.info('The Organization Event was not for a Repository newly created, nothing to change.')

    except KeyError as err:
        logging.error(f'Received KeyError, with reason {str(err)}')

    return json.dumps(payload_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
