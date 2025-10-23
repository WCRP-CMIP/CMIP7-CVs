
import json
import sys
import os
import re
import importlib.util


path = '.github/ISSUE_SCRIPT/'


def get_issue():
    return {
        'body': os.environ.get('ISSUE_BODY'),
        "labels_full": os.environ.get('ISSUE_LABELS'),
        'number': os.environ.get('ISSUE_NUMBER'),
        'title': os.environ.get('ISSUE_TITLE'),
        'author': os.environ.get('ISSUE_SUBMITTER')
    }


def parse_issue_body(issue_body):
    lines = issue_body.split('\n')
    issue_data = {}
    current_key = None

    for line in lines:
        if line.startswith('### '):
            current_key = line[4:].strip().replace(' ', '-').lower()
            issue_data[current_key] = ''
        elif current_key:
            issue_data[current_key] += line.strip() + ' '

    # Remove trailing spaces
    for key in issue_data:
        issue_data[key] = issue_data[key].strip()

        if issue_data[key] == "\"none\"":
            issue_data[key] = issue_data[key].replace("\"none\"", "none")

    return issue_data

    # return json.dumps(issue_data, indent=4)


def main():
    issue = get_issue()
    parsed_issue = parse_issue_body(issue['body'])
    issue_type = parsed_issue.get('issue-type', '')
    # print(json.dumps(parsed_issue,indent=4))

    if not issue_type:
        print(json.dumps(parsed_issue, indent=4))
        sys.exit('No issue type selected. Exiting')

    # Define the path to the script based on the issue_type
    script_path = f"{path}{issue_type}.py"

    # Check if the script exists
    if os.path.exists(script_path):
        # Load the script dynamically
        spec = importlib.util.spec_from_file_location(issue_type, script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"Successfully loaded {script_path}")
        # run the processing script
        module.run(parsed_issue, issue)

    else:
        print(f"Script {script_path} does not exist")


'''
# GitHub API URL for the issue
url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{issue_number}'
# https://github.com/WCRP-CMIP/WCRP-universe/issues/2
# Headers for authentication
headers = {
    # 'Authorization': f'token {github_token}',
    'Accept': 'application/vnd.github.v3+json'
}

# Fetch the issue content
response = requests.get(url, headers=headers)
content = response.json()
issue = content.get('body', '')
labels_full = content.get('labels','')

'''
