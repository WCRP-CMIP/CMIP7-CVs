import os
import sys


def runread(cmd):
    print(os.popen(cmd).read())


runread('git pull')
cmd = r'''
    cd ../../../
    git filter-branch -f --commit-filter \'
	if [ "$GIT_AUTHOR_EMAIL" = "actions@wcrp-cmip.org" ] || [ "$GIT_COMMITTER_EMAIL" = "actions@wcrp-cmip.org" ];
	then
		skip_commit "$@";
	else
		git commit-tree "$@";
	fi\' HEAD
'''
runread(cmd)


def forcepush():
    runread('git push -f origin main')


try:
    if sys.argv[1].strip() == '-f':
        forcepush()
except:
    pass
