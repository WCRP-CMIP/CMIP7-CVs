import os
import subprocess
import sys
from . import reset_branch, branchinfo, update_summary, update_issue,branch_pull_requests
from ..io import shell 

def prepare_pull(feature_branch):
    """Prepare a pull request branch"""
    issue_number = os.environ.get('ISSUE_NUMBER')
    if issue_number:
        feature_branch = f"{feature_branch}-{issue_number}"
        reset_branch(feature_branch)
        return feature_branch
    return False

def newpull(feature_branch, author, content, title, issue, base_branch='main', update=None):
    """Create or update a pull request"""
    
    prs = branch_pull_requests(head=feature_branch,)
    
    if prs:
        update = prs[0]['number']
        update_summary(f"++ Found existing PR: {update}. Will be updating this. ")
    
    # Get current branch name
    current_branch = shell("git rev-parse --abbrev-ref HEAD").strip()

    # Set upstream branch for feature branch
    shell(f"git branch --set-upstream-to=origin/{base_branch} {current_branch}")

    # Check for commits between the base branch and the current branch
    commits = shell(f"git log origin/{base_branch}..HEAD --oneline").strip()
    if not commits:
        raise ValueError(f"No commits between {base_branch} and {current_branch}. Cannot create pull request.")

    # If updating an existing PR, use the comment command
    if update is not None:
        where = f"gh pr comment {update}"
    else:
        where = f"gh pr create --base '{base_branch}' --head '{current_branch}' --title '{title}'"

    # Escape backticks in the content for safety
    content = content.replace('`', r'\`')

    # Construct PR body (same body for both new and existing PR)
    pr_body = f"""
This pull request was automatically created by a GitHub Actions workflow.

Adding the following new data:

```js
{content}
```

Resolves #{issue}
    """

    # If updating, just comment on the existing PR
    if update:
        print(f"++ Updating PR {update} with new comment")
        cmds = f"gh pr comment {update} --body '{pr_body}' ;"
    else:
        print(f"++ Creating a new PR")
        cmds = f"""
        nohup git pull -v > /dev/null 2>&1 ;
        {where} --body '{pr_body}' ;
        """

    # Execute the command
    output = shell(cmds).strip()
    # output = os.popen(cmds).read().strip()

    # Update issue with PR info
    update_issue(f"Updating Pull Request: {output}", False)
    
    # Add "pull_req" label to the issue (if it's a new PR)
    if update is None:
        shell(f'gh issue edit "{issue}" --add-label "pull_req"')



def pull_req(feature_branch, author, content, title):
    """Handle pull request creation"""

    # Check if the branch exists
    if not branchinfo(feature_branch):
        sys.exit(f"❌ Branch {feature_branch} not found")

    # Configure Git user details
    print(f"🔸 Setting git author to: {author}")
    shell(f'git config --global user.email "{author}@users.noreply.github.com";')
    shell(f'git config --global user.name "{author}";')

    # Check if the pull request already exists for the feature branch
    curl_command = f"gh pr list --head {feature_branch} --state all --json url --jq '.[].url';"
    pr_url = shell(curl_command).strip()
    update = None

    # If the PR exists, extract the PR number
    if pr_url:
        try:
            update = int(pr_url.strip('/').split('/')[-1])
        except ValueError:
            pass

    issue_number = os.environ.get("ISSUE_NUMBER")
    if not issue_number:
        sys.exit("❌ ISSUE_NUMBER environment variable not set")

    # Proceed to create or update the pull request
    newpull(feature_branch, author, content, title, issue_number, update=update)
