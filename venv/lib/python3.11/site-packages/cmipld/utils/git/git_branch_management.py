import os
import subprocess
import json
from ..io import shell

def getbranch():
    """Get the current git branch name"""
    return subprocess.getoutput('git rev-parse --abbrev-ref HEAD').strip()

def newbranch(branch):
    """Create or switch to a new branch"""
    branch = branch.replace(' ', '-')
    shell(f"git pull;")
    shell(f"git checkout -b {branch} || git checkout {branch};")
    try:
        shell(f"git pull;")
    except Exception as e:
        print("Error pulling branch:", e)
    # Set upstream branch to origin
    # shell(f'git branch --set-upstream-to=origin {branch};')
    shell(f'git branch -u origin {branch};')

def branchinfo(feature_branch):
    """Check if a branch exists and get its info"""
    binfo = subprocess.getoutput(
        f"git rev-parse --verify {feature_branch}").strip()
    if 'fatal' in binfo:
        return False
    return binfo

def reset_branch(feature_branch):
    """Reset a branch to main"""
    binfo = branchinfo(feature_branch)
    print('BINFO:', binfo)

    cmds = [
        'git remote -v',
        'git fetch --all',
        f"git pull",
        f"git checkout {feature_branch}",
        f"git reset --hard origin/main",
        f"git push origin {feature_branch} -f",
    ]
    if not binfo:
        cmds[3] = f"git checkout -b {feature_branch}"
        cmds[5] = f"git push --set-upstream origin {feature_branch} --force"

    for cmd in cmds:
        shell(cmd)


def branch_pull_requests(head = None,base = None):
    # Use GitHub CLI to list PRs
    # base is usually main
    # head is the branch name
    
    
    
    cmd = f"gh pr list --json url,title,headRefName,baseRefName,number"
    if head:
        cmd += f" --head {head}"
    if base:
        cmd += f" --base {base}"
    
    return json.loads(shell(cmd).strip())
    


# gh pr list --base main --head "new_experiment__esm-scen7-h-aer"  --json url,title,headRefName,baseRefName,number