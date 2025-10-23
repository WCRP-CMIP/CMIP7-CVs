
import os
import json
import subprocess
import glob
import pprint
import os



def shell(cmd,print_result=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Error running '{cmd}': {result.stderr}")
    stdout = result.stdout.strip()
    if print_result:
        print(stdout)
    return stdout

def json_read(file):
    """Read JSON file"""
    with open(file, 'r') as f:
        return json.load(f)


jr = json_read
read_jsn=json_read
rjsn = json_read

def json_write(data, file):
    """Write JSON file"""
    with open(file, 'w') as f:
        json.dump(data, f, indent=4,ensure_ascii=False)
    return file

jw = json_write

def getfile(fileend):
    """Get files with specific ending"""
    return glob.glob(f'*{fileend}.json')

def pp(js):
    """Pretty print"""
    pprint.pprint(js)

def ldpath(path=''):
    """Get location path"""
    from .git import toplevel
    loc = os.path.abspath(f"{toplevel()}/src-data/{path}/")
    if loc[-1] != '/':
        loc += '/'
    return loc




def read_url(url):
    import urllib
    import urllib.request
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
            json_data = json.loads(data)
            return json_data
    except urllib.error.HTTPError as e:
        err = f"Error: {e.code} - {e.reason}"
        # print(err)
        return None
    except urllib.error.URLError as e:
        err = f"Error: {e.reason}"
        # print(err)
        return None


def wjsn(data, f):
    with open(f, 'w') as file:
        json.dump(data, file, indent=4)


# git reset --hard miptables/jsonld && git clean -fd
