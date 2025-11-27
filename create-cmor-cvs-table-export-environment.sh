#!/bin/bash
#
# If you're on windows, sorry.
# You should be able to more or less copy these commands out
python3.13 -m venv venv

ESGVOC_FORK="znichollscr"
ESGVOC_REVISION="5145b8f6d8b1859c663e63fb7b0bad952e8bc7b5"
UNIVERSE_CVS_FORK="WCRP-CMIP"
UNIVERSE_CVS_BRANCH="esgvoc_dev"
CMIP7_CVS_FORK="znichollscr"
CMIP7_CVS_BRANCH="gha"

venv/bin/pip install -r requirements-cmor-cvs-table.txt
venv/bin/pip install --no-deps "git+https://github.com/$ESGVOC_FORK/esgf-vocab.git@$ESGVOC_REVISION"
venv/bin/esgvoc config create cmip7-cvs-ci-export
venv/bin/esgvoc config switch cmip7-cvs-ci-export

venv/bin/esgvoc config set "universe:github_repo=https://github.com/$UNIVERSE_CVS_FORK/WCRP-universe" "universe:branch=$UNIVERSE_CVS_BRANCH"
venv/bin/esgvoc config add-project cmip7 --custom --repo "https://github.com/$CMIP7_CVS_FORK/CMIP7-CVs" --branch "$CMIP7_CVS_BRANCH"

venv/bin/esgvoc config remove-project -f cmip6
venv/bin/esgvoc config remove-project -f cmip6plus
venv/bin/esgvoc install
