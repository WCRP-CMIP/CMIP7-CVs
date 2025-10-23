import os


def newrelease(owner, repo, version, content, title=''):
    print('release')
    print(os.popen(f'gh repo set-default {owner}/{repo}').read())
    release = f'gh release create "{version}" -n "{content}" -t "{title}"'
    print(os.popen(release).read())


# import json
# import urllib.request

# def trigger_CV(owner,repo,token):

#     repository = "owner/repo"
#     workflow_name = "Generate CV file"
#     branch = "main"


#      # Encode parts of the URL
#     encoded_repository = urllib.parse.quote(repository, safe='')
#     encoded_workflow_name = urllib.parse.quote(workflow_name, safe='')

#     url = f"https://api.github.com/repos/{encoded_repository}/actions/workflows/{encoded_workflow_name}/dispatches"
#     headers = {
#         "Authorization": f"Bearer {token}",
#         "Accept": "application/vnd.github.v3+json",
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "ref": branch
#     }

#     # Encode payload as JSON
#     encoded_payload = json.dumps(payload).encode('utf-8')

#     req = urllib.request.Request(url, data=encoded_payload, headers=headers, method='POST')

#     try:
#         with urllib.request.urlopen(req) as response:
#             if response.getcode() == 204:
#                 print(f"Workflow '{workflow_name}' triggered successfully for branch '{branch}'.")
#             else:
#                 print(f"Failed to trigger workflow. Status code: {response.getcode()}, Response: {response.read()}")
#     except urllib.error.HTTPError as e:
#         print(f"Failed to trigger workflow. HTTPError: {e}")
