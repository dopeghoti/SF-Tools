# SF-Tools
## sfcheck.py
A commandline tool to get response time, version, and state of a dedicated server.
# SF-Tools
## sfcheck.py
A commandline tool to get response time, version, and state of a dedicated server.


## How to run
clone the repository or download the sfcheck.py file, then run the `sfcheck.py` script using python. Ensure to provide at the very least an IP address or hostname of the game server, the port will default to `15777` if not provided.

```bash
> $ python sfcheck.py -h 
usage: sfcheck.py [-h] [-p PORT] [-c] ipAddress

positional arguments:
  ipAddress             Server IP Address or hostname to check status

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Server port to check status
  -c, --commaMode       Comma delimited output in form of - Response Time,
                        Serer State, Server Version
```
```bash
> $ python sfcheck.py 192.168.10.25                                                                                                            
        Response Time   1.54msec
        Server Status:  Live
        Server Version  174005
```

```bash
> $ python sfcheck.py 192.168.10.25 -p 15777                                                                                                            
        Response Time   1.54msec
        Server Status:  Live
        Server Version  174005
```

```bash
> $ python sfcheck.py 192.168.10.25 -p 15777 -c                                                                                                               
26.55,Live,174005
```