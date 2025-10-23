import os
import subprocess
from ..io import shell  # assuming your shell() prints output and handles errors


def gen_author_str(author):
    
    print(f"🔸 Generating author string for {author}")
    # Normalize author
    if isinstance(author, str):
        author = {'login': author, 'name': author}
        
    author.setdefault('name', author['login'])  # Use login if name is missing
    
    author['name'] = author['name'].replace('-', ' ')  # Remove dashes from name
    if author['name'] == '': author['name'] = author['login']  # Use login if name is empty
    
    # Use provided email if available, otherwise use GitHub noreply email
    if 'email' in author and author['email']:
        email = author['email']
    else:
        email = f"{author['login']}@users.noreply.github.com"
    
    return f"{author.get('name',author['login'])} <{email}>"



def commit_one(location, author, comment, branch=None):
    """Commit changes with specific author and optional branch"""

    author_str = gen_author_str(author)


    # Normalize author for git config commands
    if isinstance(author, str):
        author_login = author
        author_email = f"{author}@users.noreply.github.com"
    else:
        author_login = author.get('login', author.get('name', 'unknown'))
        author_email = author.get('email', f"{author_login}@users.noreply.github.com")

    cmds = [
        f'git config user.name "{author_login}";'
        f'git config user.email "{author_email}";',
        f'git add {location};',
        f'git commit --author="{author_str}" -m "{comment}";'
    ]

    if branch:
        cmds.append(f'git push origin {branch} --force;')
        print(f'🚀 Pushing commit to branch "{branch}" as {author_str}')
        
        cmds.append('git push origin HEAD -f;')
        # cmds.append('git push -f;')


    for cmd in cmds:
        print(f">> {cmd}")
        shell(cmd)
        # os.popen(cmd).read()

def commit(message):
    """Commit all changes with a message"""
    shell(f'git commit -a -m "{message}";')

def addfile(file):
    """Stage a specific file"""
    shell(f'git add {file}')

def addall():
    """Stage all changes"""
    shell('git add -A')

def push(branch='HEAD'):
    """Push changes to the specified branch"""
    shell(f'git push -u origin {branch}')

def recommit_file(path, author, message=None):
    """Recommit a file with a new author and message"""

    author_str = gen_author_str(author)

    # Default commit message
    if not message:
        message = f"Re-adding {path}."

    print(f"🔸 Untracking {path}...")
    output = os.popen(f'git rm --cached "{path}"').read()
    print(output)

    print(f"🔸 Committing removal of {path}...")
    output = os.popen(f'git commit -m "Stop tracking {path}"').read()
    print(output)

    print(f"🔸 Re-adding {path} as {author_str}...")
    output = os.popen(f'git add "{path}"').read()
    print(output)

    print(f"🔸 Committing {path} with new author...")
    output = os.popen(f'git commit --author="{author_str}" -m "{message}"').read()
    print(output)

    print(f"✅ {path} recommitted with author {author_str}.")


def get_last_committer(filepath):
    """Get the last committer (author) of a file using git log
    
    Args:
        filepath: Path to the file to check
        
    Returns:
        dict: Dictionary with 'name' and 'email' keys, or just username string, or None if error
    """
    try:
        # Get the last commit author name and email
        result = subprocess.run(
            ['git', 'log', '-1', '--pretty=format:%an|%ae', filepath],
            capture_output=True,
            text=True,
            check=True
        )
        
        output = result.stdout.strip()
        if '|' in output:
            author_name, author_email = output.split('|', 1)
            
            # Extract GitHub username from email if it's a GitHub noreply email
            if '@users.noreply.github.com' in author_email:
                github_username = author_email.split('@')[0]
                # Remove any numeric prefix (like 12345+username)
                if '+' in github_username:
                    github_username = github_username.split('+')[1]
                
                # Return dict format for use with gen_author_str
                return {
                    'login': github_username,
                    'name': author_name,
                    'email': author_email
                }
            else:
                # For non-GitHub emails, return full author info
                return {
                    'name': author_name,
                    'email': author_email,
                    'login': author_name  # Use name as login fallback
                }
        else:
            # Fallback if format parsing fails
            return output
            
    except subprocess.CalledProcessError as e:
        print(f"Error getting committer for {filepath}: {e}")
        return None