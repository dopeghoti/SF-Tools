# SF-Tools
## sfcheck.py
A commandline tool to get response time, version, and state of a dedicated server.

## Server States
The current implementation of the query protocol will return one of three possible server states, as a "state code".  In vervose mode, this is translated to simple words (e. g. `Live`), but in CSV or Compact mode (the default), the state code itself is provided in the output.  The possible state codes are:

| State Code | Server Status   |
|------------|-----------------|
| 1          | Idle            |
| 2          | Preparing World |
| 3          | Live            |

## How to run
Clone the repository or download the sfcheck.py file, then run the `sfcheck.py` script using Python. Ensure to provide at the very least an IP address or hostname of the game server, the port will default to `7777` if not provided.

Running in Verbose mode will return data from both the "Light" UDP API endpoint and the REST HTTPS API endpoint.  It will also give data for latency on both protocols.  The terse output mode will retun data only from the Light API endpoint.

```bash
> $ python sfcheck.py -h 
usage: sfcheck.py [-h] [-p PORT] [-c] ipAddress

positional arguments:
  ipAddress             Server IP Address or hostname to probe.

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Server port to check status.
  -v, --verbose         Use more verbose, human-readable output format.
```
```bash
> $ python sfcheck.py 192.168.10.25 -v
        Server Name     My Very Satisfactory Server
        Response Time   1.54msec
        UDP Response Time       34.12msec
        TCP Response Time       202.21msec
        Server Health:          healthy
        Server Status:          Live
        Server Version          365306
```

```bash
> $ python sfcheck.py 192.168.10.25 -p 7777 -v
        Server Name     My Very Satisfactory Server
        UDP Response Time       34.12msec
        TCP Response Time       202.21msec
        Server Health:          healthy
        Server Status:          Live
        Server Version          365306
```

```bash
> $ python sfcheck.py 192.168.10.25 -p 7777
34.12,3,365306
```

== Rest Client CLI ==
a quick and dirty client for interacting with the 1.0 REST API. 

it does not currently implement everything in the api, but it's easy enough to add to

```
$ ./rest-client-cli.py --help
Usage: rest-client-cli.py [OPTIONS]

  CLI tool to authenticate and interact with the Satisfactory Dedicated Server
  API.

Options:
  --host TEXT      host:port to connect to.  [default: localhost:7777]
  --password TEXT  Password for server authentication.
  --status         Display the server status.
  --save TEXT      save game with name
  --shutdown       shutdown the server
  --help           Show this message and exit.
```

