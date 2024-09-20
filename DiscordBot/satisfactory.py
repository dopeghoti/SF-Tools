#!/usr/bin/env python3
import argparse, socket, sys
import time
import numpy as np
import struct
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from bot_config import ConfigManager

class API():
    def __init__(self):
        self.currentRESTAPIVersion = 1
        self.messageTypes = {
            'PollServerState':      0,
            'ServerStateResponse':  1
        }
        self.serverStates = {
            0: 'Offline',           # This should never actually be sent as a running server will not send this state, but it is defined.
            1: 'Idle',              # The server is running, but no save is currently loaded.
            2: 'Preparing world',   # The server is running, and currently loading a map.  The HTTPS API will not respond in this state.
            3: 'Live'               # The server is running, and a save is loaded.  The server is joinable by players.
        }
        self.serverSubStates = {
            0: 'ServerGameState',   # Game state.  Maps to REST API QueryServerState function.
            1: 'ServerOptions',     # Global options set on the server.  Maps to REST API GetServerOptions function.
            2: 'AdvancedGameSettings', # AGS is currently enabled in the loaded session.  Maps to REST API GetAdvancedGameSettings function.
            3: 'SaveCollection',    # List of saves available on the server for loading/downloading.  Maps to REST API EnimarateSessions.
            4: 'Custom1',           # A value that can be used by mods or custom servers.  Not used on Vanilla servers.
            5: 'Custom2',           # A value that can be used by mods or custom servers.  Not used on Vanilla servers.
            6: 'Custom3',           # A value that can be used by mods or custom servers.  Not used on Vanilla servers.
            7: 'Custom4'            # A value that can be used by mods or custom servers.  Not used on Vanilla servers.
        }
        self.serverFlags = {
            0: 'Modded',            # The server self-identifies as being Modded.  Vanilla (i. e. un-modded) clients will not attempt to connect.
            1: 'Custom1',           # A flag with server-specific or context-specific meaning, currently undefined.
            2: 'Custom2',           # A flag with server-specific or context-specific meaning, currently undefined.
            3: 'Custom3',           # A flag with server-specific or context-specific meaning, currently undefined.
            4: 'Custom4'            # A flag with server-specific or context-specific meaning, currently undefined.
        }
        self.protocolVersion = 1         # The current protocol version

    def probeLightAPI( self, conf: ConfigManager ):
        msgID       = bytes.fromhex( 'D5F6' )                       # Protocol Magic identifying the UDP Protocol
        msgType     = np.uint8(self.messageTypes['PollServerState'])     # Identifier for 'Poll Server State' message
        msgProtocol = np.uint8(self.protocolVersion)                     # Identifier for protocol version identification
        msgData     = np.uint64( time.perf_counter() )              # "Cookie" payload for server state query. Can be anything.
        msgEnds     = np.uint8(1)                                   # End of Message marker

        srvAddress = conf.get( 'SATISFACTORY_HOST' )
        srvPort = int( conf.get( 'SATISFACTORY_PORT' ) )
        bufferSize = 1024
        msgToServer = ( msgID + msgType + msgProtocol + msgData + msgEnds )
        msgFromServer = None

        time_sent = time.perf_counter()
        with socket.socket( family=socket.AF_INET, type=socket.SOCK_DGRAM ) as UDPClientSocket:
            UDPClientSocket.sendto( msgToServer, ( srvAddress, srvPort ) )
            UDPClientSocket.settimeout( 0.7 )
            try:
                msgFromServer = UDPClientSocket.recvfrom( bufferSize )
            except socket.timeout:
                return( None, None )
        time_recv = time.perf_counter()
        return msgFromServer[0], time_recv - time_sent

    def parseLightAPIResponse( self, data = None ):
        if not data:
            raise ValueError( 'parseLightAPIResponse() called with empty response.' )
        # Validate the envelope
        validFingerprint = (b'\xd5\xf6', self.messageTypes['ServerStateResponse'], self.protocolVersion )
        packetFingerprint = struct.unpack( '<2s B B', data[:4])
        if not packetFingerprint == validFingerprint:
            raise ValueError( f'Unknown packet type received.  Expected {validFingerprint}; received {packetFingerprint}. ')
        packetTerminator = struct.unpack( '<B', data[-1:])
        validTerminator = ( 1, )
        if not packetTerminator == validTerminator:
            raise ValueError( f'Unknown packet terminator.  Expected {validTerminator}; received {packetTerminator}. ')
        payload = data[4:-1] # strip the envelope from the datagram
        response = {}
        response['Cookie'] = struct.unpack( "<Q", payload[:8])[0]
        response['ServerState'] = struct.unpack( "B", payload[8:9])[0]
        response['ServerNetCL'] = struct.unpack("<I", payload[9:13])[0]
        response['ServerFlags'] = struct.unpack("<Q", payload[13:21])[0]
        response['NumSubStates'] = int(struct.unpack("B", payload[21:22])[0])
        response['SubStates'] = []
        sub_states_offset = 22
        if response['NumSubStates'] > 0:
            offset_cursor = sub_states_offset
            for _ in range(response['NumSubStates']):
                sub_state = {}
                sub_state["SubStateId"] = struct.unpack("B", payload[offset_cursor:offset_cursor + 1])[0]
                offset_cursor += 1
                sub_state["SubStateVersion"] = struct.unpack("<H", payload[offset_cursor:offset_cursor + 2])[0]
                offset_cursor += 2
                response["SubStates"].append(sub_state)
                sub_states_offset += 3  # Adjust based on actual sub state size
        # Calculate server name offset once
        server_name_length_offset = sub_states_offset
        server_name_offset = server_name_length_offset + 2
        response["ServerNameLength"] = struct.unpack( "<H", payload[server_name_length_offset:server_name_length_offset+2])[0]
        raw_name = struct.unpack( f'{response["ServerNameLength"]}s', payload[server_name_offset:server_name_offset + response["ServerNameLength"]] )[0]
        response['ServerName'] = raw_name.decode('utf-8')
        return response

    def probeRESTAPI( self, conf: ConfigManager ):
        try:
            # We don't care that we're almost definitely hitting a self-signed certificate
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            address = conf.get( 'SATISFACTORY_HOST' )
            port = int( conf.get( 'SATISFACTORY_PORT' ) )
            time_sent = time.perf_counter()
            http_response = requests.post (
                    f'https://{address}:{port}/api/v{self.currentRESTAPIVersion}',
                    headers = { "Content-Type": "application/json" },
                    json = {
                        "function": "HealthCheck",
                        "data": {
                            "ClientCustomData": ""
                        }
                    },
                    verify = False
            )
            time_recv = time.perf_counter()
            transit_time = time_recv - time_sent
            api_response = http_response.json()['data']
            api_response['tx_time'] = transit_time
            return api_response
        except requests.exceptions.RequestException as e:
            print( f'Error accessing REST API: {e}' )

    def probe_udp( self, conf: ConfigManager ):
        host = conf.get( 'SATISFACTORY_HOST' )
        port = conf.get( 'SATISFACTORY_PORT' )
        # TODO: Implement IPv6 checking and support
        #  def probeLightAPI( address = 'test.example.com', port = 7777 ):
        udp_probe = self.probeLightAPI( conf )
        if udp_probe == ( None, None ):
            return ( { 'ServerState': 0, 'ServerName': 'X', 'ServerNetCL' : 'None' } )
        else:
            udp_result = self.parseLightAPIResponse( udp_probe[0] )
            return udp_result

def main() -> None:
    import sys
    try:
        raise NotImplementedError( 'bot_config.py should not be executed directly.' )
    except NotImplementedError as e:
        print( f'{e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
