import threading
import socketserver
import time
import os
import traceback
import io
import socket

#USB LAN SETUP
#https://dev.webonomic.nl/4-ways-to-connect-your-raspberry-pi-4-to-the-internet
#/boot/config.txt
#dtoverlay=dwc2
#/boot/cmdline.txt
#modules-load=dwc2,g_ether

IP_PI1 = '169.254.30.155'
TCP_PORT = 5005
FILE_BUFFER_SIZE=4*1024
TEST_DATA=os.urandom(10000000)

class lanServerMaster():

    def __init__(self):
        self.server = self.ThreadedTCPServer((IP_PI1, TCP_PORT), self.ThreadedTCPRequestHandler)

    class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        allow_reuse_address=True

    class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
        allow_reuse_address=True
        
        def handle(self):
            f = io.BytesIO()
            f.write(TEST_DATA)
            f.seek(0,0)
            try:
                bytesSent = 0
                bytesSent = self.request.sendfile(f, 0)
            except Exception as e:
                print('bytesSent: ',bytesSent)
                print('SEND ERROR: ', e)
                traceback.print_exc()
            gracefullClose(self.request)
            f.close()

    def start(self):
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        print('Pi to pi server running')

    def close(self):
        try:
            self.server.shutdown()
            self.server.server_close()
            print('Server closed')
        except Exception as e:
            print('close error', e)

def gracefullClose(clientPC):
    # https://stackoverflow.com/questions/51281111/python-network-socket-client-freezes-sporadically
    # https://stackoverflow.com/questions/4160347/close-vs-shutdown-socket/23483487#23483487
    try:
        clientPC.shutdown(socket.SHUT_WR)
        msg = b''
        unExpectedData = clientPC.recv(FILE_BUFFER_SIZE)
        while (unExpectedData):
            unExpectedData = clientPC.recv(FILE_BUFFER_SIZE)
            msg = b''.join([msg, unExpectedData])
        if len(msg)>0:
            print('Unexpected data:', len(msg))
        clientPC.close()
    except Exception as e:
        print('ERROR: gracefullClose ', e)

def startServer():
    mServer=lanServerMaster()
    try:
        mServer.start()
        while True:
            time.sleep(99999)
    except Exception as e:
        print('server error',e)
    finally:
        mServer.close()
    
if __name__ == "__main__":
    startServer()
