import os,re
import subprocess
import json
from .git_actions_management import update_summary
from ..io import shell

def update_issue_title(what):
    """Update the title of a GitHub issue"""
    if 'ISSUE_NUMBER' in os.environ:
        issue_number = os.environ['ISSUE_NUMBER']
        shell(f'gh issue edit {issue_number} --title "{what}"')
    update_summary(f"#### Title Updated:\n `{what}`")

def update_issue(comment, err=True, summarize=True):
    """Add a comment to a GitHub issue"""
    if 'ISSUE_NUMBER' in os.environ:
        issue_number = os.environ['ISSUE_NUMBER']
        cmd = f'gh issue comment {issue_number} --body \'{comment}\' '
        print(cmd)
        out = shell(cmd, print_result=False)

        if summarize:
            update_summary(comment)
        if err:
            print(out)
            raise ValueError(comment)

    print(comment)

def close_issue(comment, err=True):
    """Close a GitHub issue"""
    if 'ISSUE_NUMBER' in os.environ:
        issue_number = os.environ['ISSUE_NUMBER']
        shell(f'gh issue close {issue_number} -c "{comment}"')
        if err:
            raise ValueError(comment)

    print(comment)

def issue_author(issue_number):
    """Get the author of a GitHub issue"""
    # return os.popen(f"gh issue view '{issue_number}' --json author --jq '.author.name <.author.login'>").read().strip()
    author = json.loads(shell(f"gh issue view '{issue_number}' --json author", print_result=False))
    # return f"{author['author']} <{author['login']}>"
    return author.get('author', author)
    

def issue_list(state='open', tags=None,limit = 1000):
    
    cmd = f'gh issue list --state {state} --limit {limit} --json "author,body,title,number"'
    if tags:
        # filter by tags
        cmd += f' --label {tags}'
        
    out = shell(cmd, print_result=False)
    
    clean = re.sub(r'\x1b\[[0-9;]*m', '', out)
        
    return json.loads(clean)
