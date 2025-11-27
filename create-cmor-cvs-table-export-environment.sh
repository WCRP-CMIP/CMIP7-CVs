#!/bin/bash
#
# If you're on windows, sorry.
# You should be able to more or less copy these commands out
python3.13 -m venv venv

ESGVOC_FORK="znichollscr"
ESGVOC_REVISION="2bd33c2633580799c874bbaaebfe0bde6f9369e5"
UNIVERSE_CVS_FORK="znichollscr"
UNIVERSE_CVS_BRANCH="dunne-et-al-experiments"
CMIP7_CVS_FORK="znichollscr"
CMIP7_CVS_BRANCH="dunne-et-al-experiments"

venv/bin/pip install -r requirements-cmor-cvs-table.txt
venv/bin/pip install --no-deps "git+https://github.com/$ESGVOC_FORK/esgf-vocab.git@$ESGVOC_REVISION"
venv/bin/esgvoc config create cmip7-cvs-ci-export
venv/bin/esgvoc config switch cmip7-cvs-ci-export

venv/bin/esgvoc config set "universe:github_repo=https://github.com/$UNIVERSE_CVS_FORK/WCRP-universe" "universe:branch=$UNIVERSE_CVS_BRANCH"
venv/bin/esgvoc config add-project cmip7 --custom --repo "https://github.com/$CMIP7_CVS_FORK/CMIP7-CVs" --branch "$CMIP7_CVS_BRANCH"

venv/bin/esgvoc config remove-project -f cmip6
venv/bin/esgvoc config remove-project -f cmip6plus
venv/bin/esgvoc install
