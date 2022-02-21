#!/usr/bin/env python3
import argparse
import browser_cookie3
import json
import requests
import sys
import urllib.parse


def auth(url):
    temp = urllib.parse.urlsplit(url)
    url = temp.path.split('/')[0]
    browser = browser_cookie3.firefox(domain_name=url)
    auth_token = ""

    for cookie in browser:
        if cookie.name == "grafana_session" and cookie.domain == url:
            auth_token = cookie.value
    return auth_token


def request(target, scheme, method="get", body={}):
    api_key = auth(target)
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json'
    }

    cookies = {
        'grafana_session': api_key
    }

    if method == "get":
        print(f"Making GET request to {scheme}://{target}")
        response = requests.get(
            f"{scheme}://" + target,
            headers=headers
        )
        json_profile = response.json()
    elif method == "post":
        print(f"Making POST request to {scheme}://{target}")
        response = requests.post(
            f"{scheme}://" + target,
            headers=headers,
            cookies=cookies,
            json=body
        )
        print(response)
        print(response.content)
        json_profile = response.json()
    if method == "delete":
        print(f"Making DELETE request to {scheme}://{target}")
        response = requests.delete(
            f"{scheme}://" + target,
            headers=headers,
            cookies=cookies
        )
        json_profile = response.json()

    if response:
        return json.dumps(json_profile)


def dashboard_uid_get(host, scheme, uid):
    print("Attempting to retrieve dashboard by UID")
    api_path = "/api/dashboards/uid/"
    full_path = host + api_path + uid
    data = request(full_path, scheme, "get")
    return data


def dashboard_folder_get_list(host, scheme, folderid):
    api_path = "/api/search?folderUids=" + folderid + "&query="
    full_path = host + api_path
    data = request(full_path, scheme, "get")
    parsed = json.loads(data)
    folder_list = []

    for i in parsed:
        if "folderUid" in i and i["folderUid"] == folderid:
            folder_list.append(f"{scheme}://" + host + i["url"])
    return folder_list


def extract_params(fqdn):
    obj = urllib.parse.urlsplit(fqdn)
    params = {}

    params["url"] = obj.netloc
    params["scheme"] = obj.scheme
    path = obj.path.split('/')
    path.pop(0)

    if path[0] == 'd':
        params["uid"] = path[1]
        params["name"] = path[2]
    elif path[0] == "dashboards":
        params["folderid"] = path[2]
        params["foldername"] = path[3]

    return params


def test_get(url, scheme, path):
    obj = urllib.parse.urlsplit(url)
    full_path = obj.netloc + path
    data = request(full_path, scheme, "get")
    return data


def test_post(url, scheme, path, body={}):
    obj = urllib.parse.urlsplit(url)
    full_path = obj.netloc + path
    data = request(full_path, scheme, "post", body)
    return data


def test_delete(url, scheme, path):
    obj = urllib.parse.urlsplit(url)
    full_path = obj.netloc + path
    data = request(full_path, scheme, "delete")
    return data


mode = '-h'
sys.argv.pop(0)
if len(sys.argv) > 0:
    if sys.argv[0] == 'single':
        mode = "single"
    elif sys.argv[0] == 'batch':
        mode = "batch"
    elif sys.argv[0] == 'get':
        mode = "get"
    elif sys.argv[0] == 'post':
        mode = "post"
    elif sys.argv[0] == 'delete':
        mode = "delete"

if mode == '-h':
    print("=== Grafana Exporter ===\n")
    help = open("README.md", "r")
    print(help.read())
    help.close()
    exit(0)

elif mode == "single":
    fqdn = ""
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--fqdn', help="full url of the dashboard", action='store', dest="fqdn")
    parser.add_argument('-n', '--set-null', help="Set this to true if you want to create a dashboard, instead of updating an existing dashboard", action='store_true', dest="setnull", default=False)
    parser.add_argument('-o', '--outfile', help="Output to file. If this is omitted, will output to screen", action='store', dest="outfile", default=False)
    opts = parser.parse_args()

    params = extract_params(opts.fqdn)

    dashboard = dashboard_uid_get(params["url"], params["uid"])
    parsed = json.loads(dashboard)
    parsed = parsed["dashboard"]
    if opts.setnull is True:
        parsed['id'] = None

    if opts.outfile is False:
        print(json.dumps(parsed, indent=2, sort_keys=True))
    else:
        print("Writing " + params["name"] + " to file " + opts.outfile)
        filename = opts.outfile
        f = open(filename, "w")
        f.write(json.dumps(parsed, indent=2, sort_keys=True))
        f.close()

elif mode == "batch":
    fqdn = ""
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--fqdn', help="full url of the dashboard", action='store', dest="fqdn")
    parser.add_argument('-n', '--set-null', help="Set this to true if you want to create a dashboard, instead of updating an existing dashboard", action='store_true', dest="setnull", default=False)
    parser.add_argument('-o', '--outdir', help="Output to directory/[dashboard_name]. If this is omitted, will output to screen", action='store', dest="outdir", default=False)
    opts = parser.parse_args()

    params = extract_params(opts.fqdn)
    print(params)
    dashlist = dashboard_folder_get_list(params["url"], params["scheme"], params["folderid"])
    for dashboard in dashlist:
        dash_params = extract_params(dashboard)
        dash = dashboard_uid_get(dash_params["url"], params["scheme"], dash_params["uid"])
        parsed = json.loads(dash)
        parsed = parsed["dashboard"]
        if opts.setnull is True:
            parsed['id'] = None

        if opts.outdir is False:
            print(json.dumps(parsed, indent=2, sort_keys=True))
        else:
            print("Writing " + dash_params["name"] + " to file " + opts.outdir + "/" + dash_params["name"] + ".json")
            filename = opts.outdir + "/" + dash_params["name"] + ".json"
            f = open(filename, "w")
            f.write(json.dumps(parsed, indent=2, sort_keys=True))
            f.close()

elif mode == "get":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', help="Server Address", action='store', dest="server")
    parser.add_argument('-p', '--path', help="API Path", action='store', dest="path")
    parser.add_argument('-f', '--file', help="File output", action='store', dest="file", default=False)
    parser.add_argument('-j', '--pretty-json', help="Print output in pretty JSON", action='store_true', dest="prettyprint", default=False)
    opts = parser.parse_args()

    obj = urllib.parse.urlsplit(opts.server)
    
    output = test_get(opts.server, obj.scheme, opts.path)

    if opts.file is False:
        if opts.prettyprint is True:
            parsed = json.loads(output)
            print(json.dumps(parsed, indent=2, sort_keys=True))
        else:
            print(output)
    else:
        filename = opts.file
        f = open(filename, "w")
        if opts.prettyprint is True:
            parsed = json.loads(output)

            if opts.setnull == True:
                parsed['id'] = None

            f.write(json.dumps(parsed, indent=2, sort_keys=True))
        else:
            f.write(output)
        f.close()

elif mode == "post":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', help="Server Address", action='store', dest="server")
    parser.add_argument('-p', '--path', help="API Path", action='store', dest="path")
    parser.add_argument('-f', '--file', help="File to post as body", action='store', dest="file", required=True)
    parser.add_argument('-j', '--pretty-json', help="Print output in pretty JSON", action='store_true', dest="prettyprint", default=False)
    opts = parser.parse_args()

    body = json.loads(open(opts.file, "r").read())
    
    obj = urllib.parse.urlsplit(opts.server)

    output = test_post(opts.server, obj.scheme, opts.path, body)

    if opts.prettyprint is True:
        parsed = json.loads(output)
        print(json.dumps(parsed, indent=2, sort_keys=True))
    else:
        print(output)

elif mode == "delete":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', help="Server Address", action='store', dest="server")
    parser.add_argument('-p', '--path', help="API Path", action='store', dest="path")
    parser.add_argument('-j', '--pretty-json', help="Print output in pretty JSON", action='store_true', dest="prettyprint", default=False)
    opts = parser.parse_args()

    obj = urllib.parse.urlsplit(opts.server)

    output = test_delete(opts.server, obj.scheme, opts.path)

    if opts.prettyprint is True:
        parsed = json.loads(output)
        print(json.dumps(parsed, indent=2, sort_keys=True))
    else:
        print(output)
