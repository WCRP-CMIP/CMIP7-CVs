

'''
This file starts the server runs all the files in the repository
'''

# %%
import cmipld
import importlib
import json
from collections import OrderedDict
import glob
import os
import sys
import re
# from p_tqdm import p_map
import tqdm

relpath = __file__.replace('__main__.py', '')

repo_url = cmipld.utils.git.url()
io_url = cmipld.utils.git.url2io(repo_url)

branch = cmipld.utils.git.getbranch()
repopath = cmipld.utils.git.toplevel()
reponame = cmipld.utils.git.getreponame()

whoami = cmipld.reverse_mapping()[io_url]

print('-'*50)
print(f'Parsing repo: {whoami}')
print(f'Location: {repo_url}')
print(f'Github IO link: {io_url}')
print('-'*50)


def run(file):
    if file == __file__:
        return

    cmipld.utils.git.update_summary(f'Executing: {file}')

    try:
        # this = importlib.import_module(os.path.abspath(file))

        spec = importlib.util.spec_from_file_location("module.name", file)
        this = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(this)  # Load the module

        this.run(localhost, whoami, repopath, reponame)

    except Exception as e:
        cmipld.utils.git.update_summary(f"Error in {file} : {e}")

    return


if __name__ == '__main__':
    from cmipld.utils.offline import LD_server

    ldpath = cmipld.utils.git.ldpath()

    repos = {
        'https://wcrp-cmip.github.io/WCRP-universe/': 'universal',
        # 'https://wcrp-cmip.github.io/MIP-variables/': 'variables',
        # 'https://wcrp-cmip.github.io/CMIP6Plus_CVs/': 'cmip6plus'
    }

    localserver = LD_server(repos=repos.items(), copy=[
                            [ldpath, whoami]], override='y')

    localhost = localserver.start_server(8084)
    cmipld.processor.replace_loader(
        localhost, [list(i) for i in repos.items()])

    files = glob.glob(relpath+'*.py')

    # p_map(run,files)
    for file in tqdm.tqdm(files):
        run(file)
