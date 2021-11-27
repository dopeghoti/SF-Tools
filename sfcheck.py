import socket, sys
from time import time
import argparse

serverStates = {
    1: 'Idle',
    2: 'Preparing world',
    3: 'Live'
}

def probeServer( address = 'test.example.com', port = 15777 ):
    msgID       = bytes.fromhex( '00' )
    msgProtocol = bytes.fromhex( '00' )
    msgData     = bytes( 'PingTest'.encode() )
    
    srvAddress = address
    srvPort = int( port )
    bufferSize = 1024
    
    UDPClientSocket = socket.socket( family=socket.AF_INET, type=socket.SOCK_DGRAM )
    time_sent = time()
    UDPClientSocket.sendto( msgID + msgProtocol + msgData, ( srvAddress, srvPort ) )
    UDPClientSocket.settimeout( 5 )
    try:
        msgFromServer = UDPClientSocket.recvfrom( bufferSize )
    except socket.timeout:
        print( f'Connection timed out.' )
        exit( 1 )
    UDPClientSocket.close()
    time_recv = time()
    response = msgFromServer[ 0 ]
    rspState = response[ 10 ]
    rspVer=response[ 11:15 ]
    
    return( ( rspState, rspVer, time_recv - time_sent ) )

def main( address, port, cMode ):
    response = probeServer( address, port )
    responseTime = response[2]*1000
    serverState = serverStates[response[0]]
    serverVersion = int.from_bytes( response[1], "little" )

    if cMode == True:
        print( f'{responseTime:04.2f},{serverState},{serverVersion}')
    else:
        print( f'\tResponse Time\t{responseTime:04.2f}msec' )
        print( f'\tServer Status:\t{serverState}' )
        print( f'\tServer Version\t{serverVersion}' )
    
    return None

if __name__ == '__main__':
    proceed=False

    parser = argparse.ArgumentParser()
    
    parser.add_argument("ipAddress", help="Server IP Address or hostname to check status")
    parser.add_argument("-p", "--port", help="Server port to check status", default=15777, type=int)
    parser.add_argument("-c", "--commaMode", help="Comma delimited output in form of - Response Time, Serer State, Server Version", action="store_true")
    
    args = parser.parse_args()
    host = args.ipAddress
    port = args.port
    cMode = args.commaMode

    if (host and port):
        proceed = True
    
    if (proceed == True):
        main(host, port, cMode)

    else:
        print( f'Please invoke {sys.argv[0]} with a host to probe, followed optionally by a port.' )
