import sys
from pathlib import Path
# set the path to read update_ror. 
sys.path.append(str(Path(__file__).parent))

import update_ror
import json,os
from cmipld.utils import git
from  cmipld.tests import jsonld as tests
from cmipld.tests.jsonld.organisation import ror


path = './src-data/experiment/'


def similarity(name1, name2):
    '''
    This function looks at the similarity between two strings and returns a percentage similarity.
    
    NB Difflib should come bundled with the standard python pagages e.g. conda
    '''
    from difflib import SequenceMatcher
    
    matcher = SequenceMatcher(None, name1, name2)
    similarity = matcher.ratio() * 100

    return similarity




def run(issue,packet):
    # print('issue',issue)
    
    git.update_summary(f"### Issue content\n ```json\n{json.dumps(issue,indent=4)}\n```")
    
    ror = issue['ror']
    acronym = issue['acronym']
    id = acronym.lower()
    

    # update the issue title and create an issue branch
    title = f'{issue["issue_type"].capitalize()}_{acronym}'
    git.update_issue_title(title)
    git.newbranch(title)
    
    acronym_test = tests.field_test(tests.components.id.id_field)
    ror_test = tests.field_test(tests.organisation.ror.ror_field)
    # testclass = tests.multi_field_test([tests.organisation.ror.ror_field,tests.components.id.id_field])
    
    if ror != 'pending':
    
        tests.run_checks(acronym_test,{"id" : id})
        tests.run_checks(ror_test,{"ror" : ror})
        

        data = update_ror.get_institution(ror, acronym)

        ranking = similarity(issue['full_name_of_the_organisation'], data['long_label'])
        
        git.update_summary(f"### Similarity\nThe similarity between the full name ({issue['full_name_of_the_organisation']}) of the organisation and the long label ({data['long_label']}) is {ranking}%")
        
        
        if ranking < 80:
            git.update_issue(f"Warning: The similarity between the full name of the organisation and the long label is {ranking}%")
            
    else:

        tests.run_checks(acronym_test,{"id" : id})
        
        data = {
                    "id": f"{id}",
                    "type": ['wcrp:organisation',f'wcrp:{issue['issue_type']}','universal'],
                    "label": acronym,    
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
        os.environ['OVERRIDE_AUTHOR'] = issue['submitter']
    
    
    
    # # add files
    # git.addall()

    # git.addfile(outfile)
    # commmit them

    author = os.environ.get('OVERRIDE_AUTHOR')
    
    # git.commit_override_author(acronym,issue["issue_type"])
    git.commit_one(outfile,author,comment=f'New entry {acronym} in {issue["issue_type"]} files.' ,branch=title)

    
    git.newpull(title,author,json.dumps(issue,indent=4),title,os.environ['ISSUE_NUMBER'])
    
    
        
    
