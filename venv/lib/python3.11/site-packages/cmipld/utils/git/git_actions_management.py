import os

def update_env(key, value):
    """Update GitHub environment file"""
    github_env_file = os.environ.get("GITHUB_ENV")
    with open(github_env_file, "a") as env_file:
        env_file.write(f"{key}={value}\n")

def update_summary(md):
    """Update GitHub step summary"""
    if "GITHUB_STEP_SUMMARY" in os.environ:
        github_env_file = os.environ.get("GITHUB_STEP_SUMMARY")
        with open(github_env_file, "a") as summary:
            summary.write(f"{md}\n")
    else:
        print(md)
