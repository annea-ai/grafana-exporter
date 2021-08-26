#!/usr/bin/env python3
import argparse
import browser_cookie3
import json
import logging
import os
import requests
import sys
import time
import urllib.parse
import urllib3

def auth(url):
    temp = urllib.parse.urlsplit(url)
    url = temp.path.split('/')[0]

    browser = browser_cookie3.firefox(domain_name=url)
    auth_token = ""

    for cookie in browser:
        if cookie.name == "grafana_session" and cookie.domain == url:
            auth_token = cookie.value

    return auth_token

def request(target, method="get", body={}):
    api_key = auth(target)
    headers = {'accept': 'application/json', 'content-type': 'application/json'}
    cookies = {'grafana_session': api_key}
    time.sleep(0.35)
    if method == "get":
        response = requests.get("https://" + target, headers=headers, cookies=cookies)
        json_profile = response.json()
    elif method == "post":
        response = requests.post("https://" + target, headers=headers, cookies=cookies, json=body)
        json_profile = response.json()

    if response:
        return json.dumps(json_profile)

def dashboard_uid_get(host, uid):
    api_path = "/api/dashboards/uid/"
    full_path = host + api_path + uid
    data = request(full_path, "get")
    return data

def dashboard_folder_get_list(host, folderid):
    api_path = "/api/search?folderUids="+ folderid + "&query="
    full_path = host + api_path
    data = request(full_path, "get")
    parsed = json.loads(data)
    folder_list = []

    for i in parsed:
        if "folderUid" in i and i["folderUid"] == folderid:
            folder_list.append("https://" + host + i["url"])
    return folder_list

def extract_params(fqdn):
    obj = urllib.parse.urlsplit(fqdn)
    params = {}

    params["url"] = obj.netloc
    path = obj.path.split('/')
    path.pop(0)

    if path[0] == 'd':
        params["uid"] = path[1]
        params["name"] = path[2]
    elif path[0] == "dashboards":
        params["folderid"] = path[2]
        params["foldername"] = path[3]

    return params

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
    parser.add_argument('-o', '--outfile', help="Output to file. If this is omitted, will output to screen", action='store', dest="outfile", default=False)
    opts = parser.parse_args()

    params = extract_params(opts.fqdn)

    dashboard = dashboard_uid_get(params["url"], params["uid"])
    parsed = json.loads(dashboard)

    if opts.outfile == False:
        print(json.dumps(parsed, indent=4, sort_keys=True))
    else:
        print("Writing " + params["name"] + " to file " + opts.outfile)
        filename = opts.outfile
        f = open(filename, "w")
        f.write(json.dumps(parsed, indent=4, sort_keys=True))
        f.write("\n")
        f.close()

elif mode == "batch":
    fqdn = ""
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--fqdn', help="full url of the dashboard", action='store', dest="fqdn")
    parser.add_argument('-o', '--outdir', help="Output to directory/[dashboard_name]. If this is omitted, will output to screen", action='store', dest="outdir", default=False)
    opts = parser.parse_args()

    params = extract_params(opts.fqdn)
    dashlist = dashboard_folder_get_list(params["url"], params["folderid"])
    for dashboard in dashlist:
        dash_params = extract_params(dashboard)
        dash = dashboard_uid_get(dash_params["url"], dash_params["uid"])
        parsed = json.loads(dash)

        if opts.outdir == False:
            print(json.dumps(parsed, indent=4, sort_keys=True))
        else:
            print("Writing " + dash_params["name"] + " to file " + opts.outdir + "/" + dash_params["name"] + ".json")
            filename = opts.outdir + "/" + dash_params["name"] + ".json"
            f = open(filename, "w")
            f.write(json.dumps(parsed, indent=4, sort_keys=True))
            f.write("\n")
            f.close()