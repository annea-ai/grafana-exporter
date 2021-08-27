# grafana-exporter
CLI util to batch export grafana dashboards, using the browser's stored grafana-session cookie for authentication.

To use, first log on to the grafana instance of your choosing with firefox (will implement chrome if there is really a need.)

Currently has two modes. Single and Batch.

### Single
This takes the url of a dashboard and exports the JSON of said dashboard for import into a grafana instance.
Optionally takes a file out option to write to file instead of stdout.

`./exporter.py single -f [full dashboard url] -o [outfile]`

```
$ ./exporter.py single -h
usage: single [-h] [-f FQDN] [-n] [-o OUTFILE]

optional arguments:
  -h, --help            show this help message and exit
  -f FQDN, --fqdn FQDN  full url of the dashboard
  -n, --set-null        Set this to true if you want to create a dashboard, instead of updating an existing dashboard
  -o OUTFILE, --outfile OUTFILE
                        Output to file. If this is omitted, will output to screen
```
### Batch
This takes the url of a folder of dashboards and exports the JSON of each dashboard in the folder for import into a grafana instance.
Optionally takes an outdir option to write to outdir/file instead of stdout.

`./exporter.py batch -f [full folder url] -o [outdir]`

```
usage: batch [-h] [-f FQDN] [-n] [-o OUTDIR]

optional arguments:
  -h, --help            show this help message and exit
  -f FQDN, --fqdn FQDN  full url of the dashboard
  -n, --set-null        Set this to true if you want to create a dashboard, instead of updating an existing dashboard
  -o OUTDIR, --outdir OUTDIR
                        Output to directory/[dashboard_name]. If this is omitted, will output to screen
```
