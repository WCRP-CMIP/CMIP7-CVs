import sys
# from pathlib import Path
# set the path to read local files 
# sys.path.append(str(Path(--file--).parent))

import json,os
from cmipld.utils import git
from  cmipld.tests import jsonld as tests
from cmipld.utils.json import sorted_json
from collections import OrderedDict

from cmipld import reverse_mapping

rmap = reverse_mapping()
prefix = rmap[git.url2io(git.url())]




def run(issue,packet):
    # print('issue',issue)
    
    git.update_summary(f"### Issue content\n ```json\n{json.dumps(issue,indent=4)}\n```")
    
    path = f'./src-data/{issue['issue-type']}/'
    
    acronym = issue['experiment-id']
    id = acronym.lower()
    
    
    outfile = path+id+'.json'
    
    # whilst we are on the main branch, check if the file exists
    # if os.path.exists(outfile):
    mainfiles = git.getfilenames('main')
    if outfile in mainfiles:
        git.close_issue(f'File {outfile} already exists, please check and correct. ')
    
    # update the issue title and create an issue branch
    title = f'New {issue["issue-type"].capitalize()} - {acronym}'
    git.update_issue_title(title)
    git.newbranch(title)
    
    # activity
    activity = issue['mip-/-activity-id-(registered)'] 
    
    if issue['mip-/-activity-id-(registered)'] == "Custom Activity: specify below":
        if issue['mip-/-activity-id-(unregistered)'] != "-No response-":
            
            git.update_summary(f"### Custom Activity {issue['mip-/-activity-id-(unregistered)']} \n Please register this in both the [universal](https://github.com/WCRP-CMIP/WCRP-universe/issues/new?template=add_institution.yml) and current repo.)")
            
            print('check activity exists in universal and project?')
            
            activity = issue['mip-/-activity-id-(unregistered)']
        else:
            git.update_summary(f"### Custom activity given, in addition to the selection of an existing one. Please correct! ")
            sys.exit('Incorrect activity specified')
        
    
    
    # parent
    parent = issue['parent-experiment']
    if parent == 'no-parent':
        parent = "none"
    
    if issue['parent-experiment'] == "Custom Parent: specify below":
        if issue['custom-parent-experiment'] != "-No response-":
            
            git.update_summary(f"### Custom Parent {issue['custom-parent-experiment']} \n Please register the parent experiment.")
            
            parent = issue['custom-parent-experiment']
        
        else: 
            git.update_summary(f"### Custom parent given, in addition to the selection of an existing one. Please correct! ")
            sys.exit('Incorrect parent experiment specified')
        
    # components
    realms = []
    for mr in issue['source-type-codes-for-required-model-components'].split(', '):
        realms.append({'id':mr.lower(),'is-required':True})
    for mr in issue['source-type-codes-for-additional-allowed-model-components'].split(', '):
        realms.append({'id':mr.lower(),'is-required':False})
    
    
    
    
    # file content
    data = {
            "id": f"{id}",
            "type": [f'wcrp:{issue['issue-type']}',prefix],
            "label": acronym,    
            "long-label": issue['experiment-title'],
            "description": issue['description'],
            
            "activity": [activity],
            "parent-experiment": [parent],
            "sub-experiment": issue['sub-experiment'],
            
            "tier": issue['priority-tier'],
            
            "model-realms": realms,
            "start-date": issue['start-date'],
            "branch-date": issue['branch-date'],
            "minimum-number-of-years": issue['(minimum)-number-of-years'],

            
            
        }   
    
    
        
    data = sorted_json(data)


    git.update_summary(f"### Data content\n ```json\n{json.dumps(data,indent=4)}\n```")
    
    # write the data to a file
    
    
    
    
    # tests
    tests.run_checks(tests.experiment.experiment_model,data)
    
    git.update_summary(f"### Content has no errors. \n```")




    
    print('writing to',outfile)
    json.dump(data,open(outfile,'w'),indent=4)
    print('done')


    print(os.popen(f"less {outfile}").read())
    
    # git branch commit and push function
    
    # if we are happy, and have gotten this far: 
    
    if 'submitter' in issue: 
        # override the current author
        os.environ['OVERRIDE-AUTHOR'] = issue['submitter']
    
    author = os.environ.get('OVERRIDE-AUTHOR')
    
    # git.commit-override-author(acronym,issue["issue-type"])
    git.commit_one(outfile,author,comment=f'New entry {acronym} in {issue["issue-type"]} files.' ,branch=title)

    git.newpull(title,author,json.dumps(issue,indent=4),title,os.environ['ISSUE_NUMBER'])
    
    
        
    
