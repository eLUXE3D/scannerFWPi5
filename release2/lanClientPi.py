import socket
import io
import numpy as np
import constants
import json
import osCommands
import uuid
import time

class lanClientPi():
    # variable shared over all classes

    def __init__(self):
        # variable for this instance - self..
        self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connectionFail=False

    def sendCommand(self, TCP_IP, TCP_PORT, commandJSON):
        retries=3
        for i in range(retries):
            success=self.sendCommandNoRetry(TCP_IP, TCP_PORT, commandJSON)
            #print(commandJSON, self.sock.getsockname())
            if success:
                break
            print('Retrying LAN connection')
            time.sleep(0.5)
            self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return success
    
    def sendCommandNoRetry(self, TCP_IP, TCP_PORT, commandJSON):
        try:
            self.sock.settimeout(constants.Scanning.TIMEOUT_CONNECT)
            self.sock.connect((TCP_IP, TCP_PORT))
            self.sock.settimeout(constants.Scanning.TIMEOUT_DATA)
            self.sock.sendall(commandJSON.encode(encoding='ascii', errors="ignore"))
            self.connectionFail = False
        except Exception as e:
            print('connection error', e)
            self.connectionFail = True
            self.gracefullClose()
            self.sock=0
            return False
        #print('SENT: ', commandJSON)
        return True

    def gracefullClose(self):
        try:
            self.sock.shutdown(socket.SHUT_WR) #I've finished writing
            check = self.sock.recv(constants.Protocol.FILE_BUFFER_SIZE)  # have you finished sending? should be 0 length received if so
            while (check):
                print('Waiting for graceful close', self.sock.getsockname())
                check = self.sock.recv(constants.Protocol.FILE_BUFFER_SIZE)
            self.sock.close()
        except Exception as e:
            print('ERROR: gracefullClose ', e)
        

    def pingScanner(self, IP, PORT):
        commandDict={ "header":constants.Protocol.HEADER,
                      "command":constants.Protocol.CMD_PING}
        commandJSON=json.dumps(commandDict)

        if not self.sendCommand(IP, PORT, commandJSON):
            return False#if time out return

        try:
            data=''
            data = self.sock.recv(constants.Protocol.FILE_BUFFER_SIZE).decode()
            print(data)
        except Exception as e:
            print('ERROR pingScanner', e)
        finally:
            self.gracefullClose()
        return data

    def sendCalibPointsToPi1(self, printCoordsSet, cameraCoordsSet, undistortedcameraPrintCoordsSet):
        commandDict={ "header":constants.Protocol.HEADER,
                      "command":constants.Protocol.CMD_CALIB_POINTS_FROM_PI2_TO_PI1}
        commandJSON=json.dumps(commandDict)

        if not self.sendCommand(constants.Protocol.IP_PI1, constants.Protocol.TCP_PORT, commandJSON):
            return#if time out return

        # PUT NUMPY IMAGE INTO A FILE IN MEMORY
        f = io.BytesIO()
        #np.savez_compressed(f, printCoordsSet=printCoordsSet, cameraCoordsSet=cameraCoordsSet, undistortedcameraPrintCoordsSet=undistortedcameraPrintCoordsSet)
        np.savez(f, printCoordsSet=printCoordsSet, cameraCoordsSet=cameraCoordsSet, undistortedcameraPrintCoordsSet=undistortedcameraPrintCoordsSet)
        # SEND IMAGE TO SERVER
        f.seek(0, 0)
        try:
            self.sock.sendfile(f, 0)
        except Exception as e:
            print('ERROR: sendCalibPointsToPi1 ', e)
            traceback.print_exc()
        finally:
            self.gracefullClose()
        f.close()

    def getCalibDataFromPi1(self):
        commandDict={ "header":constants.Protocol.HEADER,
                      "command":constants.Protocol.CMD_CALIB_DATA_FROM_PI1_TO_PI2}
        commandJSON=json.dumps(commandDict)

        if not self.sendCommand(constants.Protocol.IP_PI1, constants.Protocol.TCP_PORT, commandJSON):
            return#if time out return

        # RECEIVE THE NPZ
        osCommands.setRW()
        f = open('calibrationData.npz', 'wb')
        data = self.sock.recv(constants.Protocol.FILE_BUFFER_SIZE)
        while (data):
            f.write(data)
            data = self.sock.recv(constants.Protocol.FILE_BUFFER_SIZE)
        f.close()

        osCommands.setRO()
        self.gracefullClose()

        return

    def sendCameraSyncInfo(self, clockPi1, captureTimePi1):
        commandDict = {"header": constants.Protocol.HEADER,
                       "command": constants.Protocol.CMD_SYNC_CAMERA,
                       "clockPi1": clockPi1,
                       "captureTimePi1": captureTimePi1}
        commandJSON = json.dumps(commandDict)

        if not self.sendCommand(constants.Protocol.IP_PI2, constants.Protocol.TCP_PORT_PI2, commandJSON):
            return False  # if time out return
        #not doing graceful close - doesn't seem to cause a problem? and I don't want to slow it down.
        return


    def setPi2mode(self, PI2_MODE, EXPOSURE_TIME_SCAN=None, EXPOSURE_TIME_CALIB=None, IMAGE_NUMBER=None, idealCaptureTimeMinPi1=None, PLATE_NUMBER=None, SHOT_NUMBER=None, CAPTURE_TIME_LIST=None, SCAN_IMAGE_LIST=None, RETRY=None, IMAGE_ORDER=None, PROJ_ERROR_LIST=None, SCAN_ID=None):#'scan', 'calib', 'reset'
        CMD_ID=str(uuid.uuid4())
        commandDict={ "header":constants.Protocol.HEADER,
                      "command":constants.Protocol.CMD_SET_PI2_MODE,
                      "PI2_MODE":PI2_MODE,
                      "CMD_ID": CMD_ID}
        if EXPOSURE_TIME_SCAN is not None:
            commandDict["EXPOSURE_TIME_SCAN"]=EXPOSURE_TIME_SCAN
        if EXPOSURE_TIME_CALIB is not None:
            commandDict["EXPOSURE_TIME_CALIB"] = EXPOSURE_TIME_CALIB
        if IMAGE_NUMBER is not None:
            commandDict["IMAGE_NUMBER"] = IMAGE_NUMBER
        if idealCaptureTimeMinPi1 is not None:
            commandDict["idealCaptureTimeMinPi1"] = idealCaptureTimeMinPi1
        if PLATE_NUMBER is not None:
            commandDict["PLATE_NUMBER"] = PLATE_NUMBER
        if SHOT_NUMBER is not None:
            commandDict["SHOT_NUMBER"] = SHOT_NUMBER
        if CAPTURE_TIME_LIST is not None:
            commandDict["CAPTURE_TIME_LIST"] = CAPTURE_TIME_LIST
        if SCAN_IMAGE_LIST is not None:
            commandDict["SCAN_IMAGE_LIST"] = SCAN_IMAGE_LIST
        if RETRY is not None:
            commandDict["RETRY"] = RETRY
        commandDict["IMAGE_ORDER"] = IMAGE_ORDER
        if PROJ_ERROR_LIST is not None:
            commandDict["PROJ_ERROR_LIST"] = PROJ_ERROR_LIST
        if SCAN_ID is not None:
            commandDict["SCAN_ID"] = SCAN_ID
            
        commandJSON=json.dumps(commandDict)

        if not self.sendCommand(constants.Protocol.IP_PI2, constants.Protocol.TCP_PORT_PI2, commandJSON):
            return False#if time out return

        self.gracefullClose()
        return CMD_ID

    def captureRequestPi2(self, idealCaptureTimeMin, imageNumber='0'):
        commandDict = {"header": constants.Protocol.HEADER,
                       "command": constants.Protocol.CMD_CAPTURE_REQUEST,
                       "idealCaptureTimeMinPi1": idealCaptureTimeMin,
                       "imageNumber": imageNumber}
        commandJSON = json.dumps(commandDict)

        if not self.sendCommand(constants.Protocol.IP_PI2, constants.Protocol.TCP_PORT_PI2, commandJSON):
            return False  # if time out return
        self.gracefullClose()
        return

    def commandDone(self, CMD_ID, msgDict={}):
        commandDict = {"header": constants.Protocol.HEADER,
                       "command": constants.Protocol.CMD_DONE,
                       "CMD_ID": CMD_ID}
        #merge message Dict with commandDict because data passing protocol can't handle nested dict.
        commandDict = {**commandDict, **msgDict}
        commandJSON = json.dumps(commandDict)

        if not self.sendCommand(constants.Protocol.IP_PI1, constants.Protocol.TCP_PORT, commandJSON):
            return False  # if time out return
        self.gracefullClose()
        return


if __name__ == "__main__":
    pass
    mLanClient=lanClientPi()
    mLanClient.pingScanner('169.254.30.155', 5005)
    

    
