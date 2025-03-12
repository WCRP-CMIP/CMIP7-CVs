import sys
# from pathlib import Path
# set the path to read local files 
# sys.path.append(str(Path(--file--).parent))

import json,os
from cmipld.utils import git
from  cmipld.tests import jsonld as tests
from collections import OrderedDict

from cmipld import reverse_mapping

rmap = reverse_mapping()
prefix = rmap[git.url2io(git.url())]



# {
#    "experiment-id": "imaginary",
#    "experiment-title": "none",
#    "description": "some info here",
#    "mip-/-activity-id-(registered)": "Custom Activity: specify below",
#    "mip-/-activity-id-(unregistered)": "superman",
#    "parent-experiment": "Custom Parent: specify below",
#    "custom-parent-experiment": "-No response-",
#    "sub-experiment": "\"none\"",
#    "priority-tier": "3",
#    "source-type-codes-for-required-model-components": "ISM, CHEM",
#    "source-type-codes-for-additional-allowed-model-components": "ISM, AOGCM",
#    "start-date": "1900",
#    "branch-date": "9000",
#    "(minimum)-number-of-years": "0",
#    "issue-type": "experiment",
#    "issue-kind": "new"
# }



def run(issue,packet):
    # print('issue',issue)
    
    git.update_summary(f"### Issue content\n ```json\n{json.dumps(issue,indent=4)}\n```")
    
    path = f'./src-data/{issue['issue-type']}/'
    
    acronym = issue['experiment-id']
    id = acronym.lower()
    
    # update the issue title and create an issue branch
    title = f'{issue["issue-type"].capitalize()}-{acronym}'
    git.update_issue_title(title)
    git.newbranch(title)
    
    # activity
    activity = issue['mip-/-activity-id-(registered)'] 
    if issue['mip-/-activity-id-(unregistered)'] != "-No response-":
        
        git.update_summary(f"### Custom Activity {issue['mip-/-activity-id-(unregistered)']} \n Please register this in both the [universal](https://github.com/WCRP-CMIP/WCRP-universe/issues/new?template=add_institution.yml) and current repo.)")
        
        print('check activity exists in universal and project?')
        
        activity = issue['mip-/-activity-id-(unregistered)']
    
    
    
    # parent
    parent = issue['parent-experiment']
    if issue['custom-parent-experiment'] != "-No response-":
        
        git.update_summary(f"### Custom Parent {issue['custom-parent-experiment']} \n Please the parent experiment as well.")
        
        parent = issue['custom-parent-experiment']
        
    # components
    "source-type-codes-for-required-model-components": issue['source-type-codes-for-required-model-components'],
            "source-type-codes-for-additional-allowed-model-components": issue['source-type-codes-for-additional-allowed-model-components'],
        
    
    realms = []
    for mr in issue['source-type-codes-for-required-model-components'].split(', '):
        realms.append({'id':mr,'is-required':True})
    for mr in issue['source-type-codes-for-additional-allowed-model-components'].split(', '):
        realms.append({'id':mr,'is-required':False})
    
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
            
            
            "start-date": issue['start-date'],
            "branch-date": issue['branch-date'],
            "minimum-number-of-years": issue['(minimum)-number-of-years'],

            
            
        }   
    
    
        
        
     

    git.update_summary(f"### Data content\n ```json\n{json.dumps(data,indent=4)}\n```")
    
    # write the data to a file

    outfile = path+id+'.json'
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

    git.newpull(title,author,json.dumps(issue,indent=4),title,os.environ['ISSUE-NUMBER'])
    
    
        
    
