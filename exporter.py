#!/usr/bin/env python3

import requests
import json
import time
import os
import sys
import logging
import configparser
import argparse
import jwt
import datetime

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

## Read config from file
if not os.path.exists('exporter.conf'):
    print(bcolors.FAIL + "exporter.conf does not exist. Please see README" + bcolors.ENDC)
    raise Exception("EXPORTER_MISSING_CONFIG")

config = configparser.ConfigParser()
config.read("exporter.conf")
email = config.get("auth", "email")
password = config.get("auth", "password")
host="https://api.warframe.market/v1/"

### BASH EXAMPLE
#
#set -o errexit
#set -o pipefail
#
#HOST="grafana.tools.connected.dyson.cloud"
#FULLURL="https://<username>:<password>@$HOST"
#
#set -o nounset
#
#echo "Exporting Grafana dashboards from $HOST"
#rm -rf dashboards
#mkdir -p dashboards
#for dash in $(curl -s "$FULLURL/api/search?query=&" | jq -r '.[] | select(.type == "dash-db") | .uid'); do
#        curl -s "$FULLURL/api/dashboards/uid/$dash" | jq -r . > dashboards/${dash}.json
#        slug=$(cat dashboards/${dash}.json | jq -r '.meta.slug')
#        mv dashboards/${dash}.json dashboards/${dash}-${slug}.json
#done
