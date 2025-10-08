import sys
import json, os
import cmipld
from cmipld.utils import git
from cmipld.tests import jsonld as tests
from cmipld.utils.jsontools import sorted_json, validate_and_fix_json, sort_json_keys
from collections import OrderedDict
from cmipld import reverse_mapping

# --- Initialize Reverse Mapping and Prefix ---
rmap = reverse_mapping()
prefix = rmap[git.url2io(git.url())]

# --- Main Processing Function ---
def run(issue, packet):
    # --- Issue Summary ---
    git.update_summary(f"### Issue content\n```json\n{json.dumps(issue, indent=4)}\n```")

    # Define output path and file name
    path = f'./src-data/{issue["issue-type"]}/'
    acronym = issue['experiment-id']
    id = acronym.lower()
    outfile = path + id + '.json'

    # --- Check if File Already Exists in Main Branch ---
    mainfiles = git.getfilenames('main')
    if outfile in mainfiles:
        git.close_issue(f'File {outfile} already exists, please check and correct.')
        sys.exit('File already exists on main')

    # --- Branch Setup ---
    title = f'New {issue["issue-type"].capitalize()} {acronym}'
    branch = title.replace(' ', '_').lower()
    git.update_issue_title(title)
    git.newbranch(branch)
    os.popen(f"git checkout {branch}")
    git.update_summary(f"### Branch created: {branch}, {os.popen('git branch').read()}")
    gb = git.getbranch()
    assert gb == branch, f'The branch was not created properly: "{gb}" != "{branch}"'

    # --- Activity Validation ---
    
    alist = set([i['name'].replace('.json','') for i in cmipld.utils.git.list_repo_files('WCRP-CMIP','WCRP-universe','production','src-data/activity') if 'json' in i['name']])
    
    activity = issue['mip-/-activity-id-(registered)']
    
    if activity == "Custom Activity: specify below":
        if issue['mip-/-activity-id-(unregistered)'] == "-No response-":
            git.update_issue("### Please edit the issue (from the top) and enter the custom activity where it states `-No response-`", err=False)
        
        elif issue['mip-/-activity-id-(unregistered)'] != "-No response-":
            git.update_issue(
                f"### Custom Activity {issue['mip-/-activity-id-(unregistered)']} \n"
                "Please register this using [universal](https://github.com/WCRP-CMIP/WCRP-universe/issues/new?template=add_activity.yml) "
                ". Once approved, edit the issue title with `-added` to rerun the checks.",
                err=False
            )
            activity = issue['mip-/-activity-id-(unregistered)']
        else:
            
            git.update_issue("### Custom activity specified along with an existing one. Please correct!", err=False)
            sys.exit('Incorrect activity specified')
            
            
    # sanitize activity name
    activity = activity.strip().lower().replace(' ', '-').replace('_', '-')        
    # ensure activity is in the list
    if activity not in alist:
        git.update_issue(f"Activity {activity} is not registered in the WCRP universe. Please register it first.", err=True)
    
    # also check if it is in the list of activities, otherwise add it. 
    aclist = f'./src-data/project/{activity}.json'
    proj_activity = cmipld.json_read(aclist, 'r')
    if not activity in proj_activity['activity']:
        proj_activity['activity'].append(activity)
        proj_activity['activity'] = sorted(proj_activity['activity'])
        cmipld.json_write(proj_activity, aclist)
        git.update_issue(f"### Added activity {activity} to project file: {aclist}.", err=False)
    

    # --- Parent Experiment Validation ---
    parent = issue['parent-experiment']
    if parent == 'no-parent':
        parent = "none"

    if parent == "Custom Parent: specify below":
        if issue['custom-parent-experiment'] != "-No response-":
            git.update_issue(
                f"### Custom Parent {issue['custom-parent-experiment']} \n"
                "Please register the parent experiment. If there is none, write 'none' as per the form instructions.",
                err=False
            )
            parent = issue['custom-parent-experiment']
        else:
            git.update_issue("### Custom parent specified along with an existing one. Please correct!")
            sys.exit('Incorrect parent experiment specified')

    # --- Component Realms ---
    realms = []
    for mr in issue['source-type-codes-for-required-model-components'].split(', '):
        realms.append({'id': mr.lower(), 'is-required': True})
    for ma in issue['source-type-codes-for-additional-allowed-model-components'].split(', '):
        if ma != "_No response_":
            realms.append({'id': ma.lower(), 'is-required': False})

    # Set default for missing start date
    if issue['start-date'] == "_No response_":
        issue['start-date'] = 'none'

    # --- Construct File Content ---
    data = {
        "id": id,
        "type": [f'wcrp:{issue["issue-type"]}', prefix],
        "label": acronym,
        "long-label": issue['experiment-title'],
        "description": issue['description'].replace("'", ""),
        "activity": [activity.lower()],
        "parent-experiment": [parent],
        "sub-experiment": issue['sub-experiment'],
        "tier": issue['priority-tier'],
        "model-realms": realms,
        "start-date": issue['start-date'],
        "alias": [],
        "minimum-number-of-years": issue['(minimum)-number-of-years'],
    }

    # --- Sort Keys and Display Data Summary ---
    data = sorted_json(data)
    git.update_summary(f"### Data content\n```json\n{json.dumps(data, indent=4)}\n```")

    # --- Run Schema Tests ---
    tests.run_checks(tests.experiment.experiment_model, data)
    git.update_summary("### Content has no errors. \n```")

    # --- Write JSON to File ---
    print('writing to', outfile)
    cmipld.json_write(data, outfile)

    # --- Validate JSON File ---
    status, msg = validate_and_fix_json(outfile)
    if not status:
        git.update_issue(f"### JSON validation error: {msg}", err=True)
        sys.exit(f'JSON validation failed: {msg}')

    print('done')

    # --- Commit and Push to Branch ---
    if 'submitter' in issue:
        author = {'name': issue['submitter'], 'login': f"{issue['submitter']}@users.noreply.github.com"}
    else:
        author = git.issue_author(os.environ['ISSUE_NUMBER'])

    print('Author', author)
    git.commit_one(outfile, author, comment=f'New entry {acronym} in {issue["issue-type"]} files.', branch=branch)

    print('CREATING PULL\n', branch, author, title, os.environ['ISSUE_NUMBER'])
    git.newpull(branch, author, json.dumps(data, indent=4), title, os.environ['ISSUE_NUMBER'])
