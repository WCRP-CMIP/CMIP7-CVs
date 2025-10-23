
import os
import sys
import json
import ast
import re
import configparser
from io import StringIO


def parse_md(body):
    # remove comments
    pattern = r'<!---(.*?)--->'

    # Remove comments using re.sub
    body = re.sub(r'/r/n', r'/n', re.sub(pattern, '', body, flags=re.DOTALL))

    config_str = re.search(r'```\sconfigfile(.*?)```',
                           body, re.DOTALL).group(1)
    print(config_str)

    # Create a file-like object from the string
    config_file = StringIO(config_str)

    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Read configuration from the file-like object
    config.read_file(config_file)

    # Initialize an empty dictionary to hold the configuration data
    config_dict = {}

    # Iterate over sections and options
    for section in config.sections():
        config_dict[section] = {}
        for option in config.options(section):
            config_dict[section][option] = ast.literal_eval(
                config.get(section, option))

    return config_dict


def dispatch(token, payload, repo):

    import json
    from urllib import request

    # Construct the request headers
    headers = {
        "Accept": "application/vnd.github.everest-preview+json",
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }

    # Encode the payload
    datapayload = json.dumps(payload).encode('utf-8')

    # Make the POST request
    req = request.Request(f"{repo}/dispatches",
                          data=datapayload, headers=headers, method='POST')

    # Perform the request
    try:
        with request.urlopen(req) as response:
            if response.getcode() == 204:
                print("Dispatch event triggered successfully.")
            else:
                print(
                    f"Failed to trigger dispatch event. Status code: {response.getcode()}")
                print(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error: {e}")
