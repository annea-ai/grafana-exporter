#!/usr/bin/env python3
import urllib.parse
import requests
import json
import time
import os
import sys
import logging
import argparse
import browser_cookie3
import urllib3

class bcolors:
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

debug = os.environ.get("CLI_DEBUG")
if debug is True:
    try:
        import http.client as http_client
    except ImportError:
        import httplib as http_client
    http_client.HTTPConnection.debuglevel = 1
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

def request(target, method="get", body={}):
    api_key = 'Bearer ' + auth(target)
    headers = {'Authorization': api_key, 'accept': 'application/json', 'content_type': 'application/json', "X-Grafana-Org-Id": "1"}
    time.sleep(0.35)
    if method == "get":
        print("requests.get(\"https://\" + " + str(target) + ", headers=" + str(headers) + ")")
        response = requests.get("https://" + target, headers=headers)
        json_profile = response.json()
    elif method == "post":
        response = requests.post("https://" + target, headers=headers, json=body)
        json_profile = response.json()

    if response:
        return response
    else:
        print(response)
        print(json.dumps(json_profile, indent=4, sort_keys=True))
        exit()

def dashboard_uid_get(host, uid):
    api_path = "/api/dashboards/uid/"
    full_path = host + api_path + uid
    data = request(full_path, "get")
    print(data)

def extract_params(fqdn):
    obj = urllib.parse.urlsplit(fqdn)
    params = {}

    params["url"] = obj.netloc
    path = obj.path.split('/')
    path.pop(0)

    if path[0] == 'd':
        params["uid"] = path[1]
        params["name"] = path[2]

    return params

def auth(url):
    temp = urllib.parse.urlsplit(url)
    url = temp.path.split('/')[0]

    browser = browser_cookie3.firefox(domain_name=url)
    auth_token = ""

    for cookie in browser:
        if cookie.name == "grafana_session" and cookie.domain == url:
            auth_token = cookie.value

    return auth_token

mode = '-h'
sys.argv.pop(0)
if len(sys.argv)>0:
    if sys.argv[0] == 'single':
        mode = "single"
    elif sys.argv[0] == 'batch':
        mode = "batch"

if mode == '-h':
    print("=== Grafana Exporter ===\n")
    exit(0)

elif mode == "single":
    fqdn=""
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--fqdn', help="full url of the dashboard", action='store', dest="fqdn")
    opts = parser.parse_args()

    params = extract_params(opts.fqdn)

    dashboard_uid_get(params["url"], params["uid"])

elif mode == "batch":
    print("Do something")