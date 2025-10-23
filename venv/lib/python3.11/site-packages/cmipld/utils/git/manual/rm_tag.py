'''
Remove an already published tag from a repo. 

Author: daniel.ellis@wcrp-cmip.org
'''

import os
import sys

tag = sys.argv[1].strip()


def runread(cmd):
    print(os.popen(cmd).read())


runread(f'git tag -d {tag}')
runread(f'git push origin :refs/tags/{tag}')
