#!/usr/bin/env python3


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
