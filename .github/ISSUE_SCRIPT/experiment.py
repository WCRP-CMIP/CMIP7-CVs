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
    
    # also breaks the issue updates for the same reason 
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
        sys.exit('File already exists on main')
    
    # update the issue title and create an issue branch
    title = f'New {issue["issue-type"].capitalize()}  {acronym}'
    branch = title.replace(' ','_').lower()
    
    git.update_issue_title(title)
    git.newbranch(branch)
    os.popen(f"git checkout {branch}")
    
    git.update_summary(f"### Branch created: {branch}, {os.popen('git branch').read()}")
    
    gb = git.getbranch()
    assert gb == branch, f'the branch is not the same (not created) "{gb}" != "{branch}"'
    
    
    # activity
    activity = issue['mip-/-activity-id-(registered)'] 
    
    if issue['mip-/-activity-id-(registered)'] == "Custom Activity: specify below":
        if issue['mip-/-activity-id-(unregistered)'] != "-No response-":
            
            git.update_issue(f"### Custom Activity {issue['mip-/-activity-id-(unregistered)']} \n Please register this in both the [universal](https://github.com/WCRP-CMIP/WCRP-universe/issues/new?template=add_activity.yml) and current repo.Once this has been approved, edit the title of this issue with `-added` to rerun the checks.",err=False)
            
            print('check activity exists in universal and project?')
            
            activity = issue['mip-/-activity-id-(unregistered)']
        else:
            git.update_issue(f"### Custom activity given, in addition to the selection of an existing one. Please correct! ",err=False)
            sys.exit('Incorrect activity specified')
        
    
    
    # parent
    parent = issue['parent-experiment']
    if parent == 'no-parent':
        parent = "none"
    
    if issue['parent-experiment'] == "Custom Parent: specify below":
        if issue['custom-parent-experiment'] != "-No response-":
            
            git.update_issue(f"### Custom Parent {issue['custom-parent-experiment']} \n Please register the parent experiment, if there is none, write none as per the form instructions.",err=False)
            
            parent = issue['custom-parent-experiment']
        
        else: 
            git.update_issue(f"### Custom parent given, in addition to the selection of an existing one. Please correct! ")
            sys.exit('Incorrect parent experiment specified')
        
    # components
    realms = []
    for mr in issue['source-type-codes-for-required-model-components'].split(', '):
        realms.append({'id':mr.lower(),'is-required':True})
    for ma in issue['source-type-codes-for-additional-allowed-model-components'].split(', '):
        if ma != "_No response_":
            realms.append({'id':ma.lower(),'is-required':False})
    
    if issue['start-date'] == "_No response_":
        issue['start-date'] = 'none'
    
    
    
    
    # file content
    data = {
            "id": f"{id}",
            "type": [f'wcrp:{issue['issue-type']}',prefix],
            "label": acronym,    
            "long-label": issue['experiment-title'],
            "description": issue['description'].replace("'", ""),
            
            "activity": [activity.lower()],
            "parent-experiment": [parent],
            "sub-experiment": issue['sub-experiment'],
            
            "tier": issue['priority-tier'],
            
            "model-realms": realms,
            "start-date": issue['start-date'],
            # "branch-date": issue['branch-date'],
            "minimum-number-of-years": issue['(minimum)-number-of-years'],

            
            
        }   
    
    # if data['branch-date'] == "_No response_":
    #     data['branch-date'] = 'none'
    
    
        
    data = sorted_json(data)

    # broken for now    
    # git.update_issue(f"### Data content\n ```json\n{json.dumps(data,indent=4)}\n```")
    git.update_summary(f"### Data content\n ```json\n{json.dumps(data,indent=4)}\n```")
    
    # write the data to a file
    
    
    
    
    # tests
    tests.run_checks(tests.experiment.experiment_model,data)
    
    git.update_summary(f"### Content has no errors. \n```")




    
    print('writing to',outfile)
    json.dump(data,open(outfile,'w'),indent=4)
    print('done')


    # print(os.popen(f"less {outfile}").read())
    
    # git branch commit and push function
    
    # if we are happy, and have gotten this far: 
    
    if 'submitter' in issue:  # override the current author
        author = issue['submitter']
        author = {'name':author,'login':f"{author}@users.noreply.github.com"}
    else:
        author = git.issue_author(os.environ['ISSUE_NUMBER'])

    print('Author',author)
    
    
    # git.commit-override-author(acronym,issue["issue-type"])
    git.commit_one(outfile,author,comment=f'New entry {acronym} in {issue["issue-type"]} files.' ,branch=branch)
    print('CREATING PULL\n',branch, author,title,os.environ['ISSUE_NUMBER'])
    
    git.newpull(branch,author,json.dumps(data,indent=4),title,os.environ['ISSUE_NUMBER'])
    
    
        
    
