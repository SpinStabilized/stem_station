import socket
import sys

import apt_rx

import ctypes
if sys.platform.startswith('linux'):
	try:
		x11 = ctypes.cdll.LoadLibrary('libX11.so')
		x11.XInitThreads()
	except:
		print "Warning: failed to XInitThreads()"

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 4532)
print 'starting up on {} port {}'.format(server_address[0], server_address[1])
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

frequency = 0

while True:
    # Wait for a connection
    print 'waiting for a connection'
    connection, client_address = sock.accept()
    tb = apt_rx.apt_rx()

    tb.Start(True)
    tb.Wait()
    
    try:
        print 'connection from {}'.format(client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(100)

            if data:
                msg = data.split()
                if msg[0] == b'F':
                    print 'Setting Frequency To: {} Hz'.format(int(msg[1]))
                    tb.set_satellite_frequency(int(msg[1]))
                    response = bytes('RPRT 0') # , 'utf-8'
                elif msg[0] == b'f':
                    response = bytes('{} RPRT 0'.format(tb.get_satellite_frequency())) #, 'utf-8')
                elif msg[0] == b'q':
                    print 'Disconnect Request'
                    break
                else:
                    print 'Unknown Command: {}'.format(msg)
                    response = bytes('RPRT 0') #, 'utf-8')
                connection.sendall(response)
            else:
                print 'no more data from {}'.format(client_address)
                break
            
    finally:
        # Clean up the connection
        connection.close()

