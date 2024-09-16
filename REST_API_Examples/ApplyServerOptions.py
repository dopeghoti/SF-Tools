#!/usr/bin/env python3
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# We don't care that we're almost definitely hitting a self-signed certificate
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

myServer = 'satisfactory.example.com'
myPort = 7777
myAPIVersion = 1
myToken = None # Replace with an exact string copy of your Bearer Token.  Do not include the 'Bearer: ' prefix.

try:
    r = requests.post (
        f'https://{myServer}:{myPort}/api/v{myAPIVersion}',
        headers = {
            "Content-Type": "application/json",
            "Authorization": f'Bearer {myToken}',
        },
        json = {
            "function": "ApplyServerOptions",
            "data": {
                "UpdatedServerOptions": {
                    "FG.DSAutoPause": "True"
                }
            }
        },
        verify = False # If assuming self-signed certificates
    )
    try:
        print( r.json()['data'] )
    except:
        print( r.status_code )
        print( r.text )
except requests.exceptions.RequestException as e:
    print( f'Error: {e}' ) 
