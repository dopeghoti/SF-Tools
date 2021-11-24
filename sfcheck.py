import socket, sys
from time import time

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

def main( address, port ):
    response = probeServer( address, port )
    print( f'\tResponse Time\t{ response[ 2 ] * 1000:04.2f }msec' )
    print( f'\tServer Status:\t{ serverStates[ response[ 0 ] ] }' )
    print( f'\tServer Version\t{ int.from_bytes( response[1], "little" ) }' )
    return None

if __name__ == '__main__':
    proceed=False
    if len( sys.argv ) == 3:
        host = sys.argv[ 1 ]
        port = sys.argv[ 2 ]
        proceed = True
    elif len( sys.argv ) == 2:
        host = sys.argv[ 1 ]
        port = 15777
        proceed = True
    if proceed:
        main( host, port )
    else:
        print( f'Please invoke {sys.argv[0]} with a host to probe, followed optionally by a port.' )
