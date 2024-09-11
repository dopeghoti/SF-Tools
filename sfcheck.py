#!/usr/bin/env python3
import argparse, socket, sys
import time
import numpy as np
import struct

messageTypes = {
    'PollServerState':      0,
    'ServerStateResponse':  1
}

serverStates = {
    0: 'Offline',           # This should never actually be sent as a running server will not send this state, but it is defined.
    1: 'Idle',              # The server is running, but no save is currently loaded.
    2: 'Preparing world',   # The server is running, and currently loading a map.  The HTTPS API will not respond in this state.
    3: 'Live'               # The server is running, and a save is loaded.  The server is joinable by players.
}

serverSubStates = {
    0: 'ServerGameState',   # Game state.  Maps to REST API QueryServerState function.
    1: 'ServerOptions',     # Global options set on the server.  Maps to REST API GetServerOptions function.
    2: 'AdvancedGameSettings', # AGS is currently enabled in the loaded session.  Maps to REST API GetAdvancedGameSettings function.
    3: 'SaveCollection',    # List of saves available on the server for loading/downloading.  Maps to REST API EnimarateSessions.
    4: 'Custom1',           # A value that can be used by mods or custom servers.  Not used on Vanilla servers.
    5: 'Custom2',           # A value that can be used by mods or custom servers.  Not used on Vanilla servers.
    6: 'Custom3',           # A value that can be used by mods or custom servers.  Not used on Vanilla servers.
    7: 'Custom4'            # A value that can be used by mods or custom servers.  Not used on Vanilla servers.
}

serverFlags = {
    0: 'Modded',            # The server self-identifies as being Modded.  Vanilla (i. e. un-modded) clients will not attempt to connect.
    1: 'Custom1',           # A flag with server-specific or context-specific meaning, currently undefined.
    2: 'Custom2',           # A flag with server-specific or context-specific meaning, currently undefined.
    3: 'Custom3',           # A flag with server-specific or context-specific meaning, currently undefined.
    4: 'Custom4'            # A flag with server-specific or context-specific meaning, currently undefined.
}

protocolVersion = 1         # The current protocol version

def probeServer( address = 'test.example.com', port = 7777 ):
    msgID       = bytes.fromhex( 'D5F6' )                       # Protocol Magic identifying the UDP Protocol
    msgType     = np.uint8(messageTypes['PollServerState'])     # Identifier for 'Poll Server State' message
    msgProtocol = np.uint8(protocolVersion)                     # Identifier for protocol version identification
    msgData     = np.uint64( time.perf_counter() )              # "Cookie" payload for server state query. Can be anything.
    msgEnds     = np.uint8(1)                                   # End of Message marker

    srvAddress = address
    srvPort = int( port )
    bufferSize = 1024
    msgToServer = ( msgID + msgType + msgProtocol + msgData + msgEnds )
    msgFromServer = None

    time_sent = time.perf_counter()
    with socket.socket( family=socket.AF_INET, type=socket.SOCK_DGRAM ) as UDPClientSocket:
        UDPClientSocket.sendto( msgToServer, ( srvAddress, srvPort ) )
        UDPClientSocket.settimeout( 2 )
        try:
            msgFromServer = UDPClientSocket.recvfrom( bufferSize )
        except socket.timeout:
            print( f'Connection timed out.' )
            exit( 1 )
    time_recv = time.perf_counter()
    return msgFromServer[0], time_recv - time_sent

def parseResponse( data = None ):
    if not data:
        raise ValueError( 'parseResponse() called with empty response.' )
    # Validate the envelope
    validFingerprint = (b'\xd5\xf6', messageTypes['ServerStateResponse'], protocolVersion )
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


def main( address, port, verbose ):
    response = probeServer( address, port )
    responseTime = response[1]*1000
    serverData = parseResponse( response[0] )
    # Turn encoded responde data into usable output
    serverState = serverStates[ serverData['ServerState'] ]
    serverStateCode = serverData['ServerState']
    serverVersion = serverData['ServerNetCL']
    serverName = serverData['ServerName']
    if not verbose:
        print( f'{responseTime:04.2f},{serverStateCode},{serverVersion}')
    else:
        print( f'\tServer Name\t{serverName}' )
        print( f'\tResponse Time\t{responseTime:04.2f}msec' )
        print( f'\tServer Status:\t{serverState}' )
        print( f'\tServer Version\t{serverVersion}' )
    return None

if __name__ == '__main__':
    proceed=False

    parser = argparse.ArgumentParser()

    parser.add_argument("ipAddress", help="Server IP Address or hostname to probe")
    parser.add_argument("-p", "--port", help="Server port to check status.  Defaults to 7777.", default=7777, type=int)
    parser.add_argument("-v", "--verbose", help="Use more verbose, human-readable output format.", action="store_true")

    args = parser.parse_args()
    host = args.ipAddress
    port = args.port
    verbose = args.verbose

    if (host and port):
        proceed = True

    if (proceed == True):
        main(host, port, verbose)

    else:
        print( f'Please invoke {sys.argv[0]} with a host to probe, followed optionally by a port.' )
