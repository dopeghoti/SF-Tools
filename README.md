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
        Server Status:  Live
        Server Version  174005
```

```bash
> $ python sfcheck.py 192.168.10.25 -p 7777 -v
        Server Name     My Very Satisfactory Server
        Response Time   1.54msec
        Server Status:  Live
        Server Version  174005
```

```bash
> $ python sfcheck.py 192.168.10.25 -p 7777
26.55,3,174005
```
