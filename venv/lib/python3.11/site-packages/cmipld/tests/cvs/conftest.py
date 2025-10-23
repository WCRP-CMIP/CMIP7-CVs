import pytest
import json

'''
!cd ../tests/;
!pytest -v --file-location='/Users/daniel.ellis/WIPwork/CMIP-LD/cmipld/cvs/CV.json' /Users/daniel.ellis/WIPwork/CMIP-LD/cmipld/tests/cvs
'''


def pytest_addoption(parser):
    parser.addoption("--file-location", action="store",
                     default=".CV.json", help="Path to the CV file")


@pytest.fixture(scope='session')
def file_location(request):
    return request.config.getoption("--file-location")


@pytest.fixture(scope='session')
def cv_data(file_location):
    with open(file_location, 'r') as f:
        content = json.load(f)
    return content
