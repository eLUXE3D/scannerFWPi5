import threading
import socketserver
import io
import os
import numpy as np
import time
from multiprocessing import Manager, JoinableQueue
import constants
import scanSlave
import json
import captureVideo
import zipfile
import subprocess
from shutil import copyfile
import osCommands
import raw2 as raw
import cv2
import lanHelpers
import lanSender
import lanClientPi
import lanCamera


class lanServerSlave():
    # variable shared over all classes - gets run even on import


    def __init__(self):
        # variable for this instance - self..
        lanHelpers.setup()
        print('IP: ',constants.Protocol.IP_PI2)
        self.server = self.ThreadedTCPServer((constants.Protocol.IP_PI2, constants.Protocol.TCP_PORT_PI2), self.ThreadedTCPRequestHandler)  # Port 0 means to select an arbitrary unused port
        #constants.Control.decodeImageQ=JoinableQueue(maxsize=12)#clear queue
        with constants.Control.imageLock:
            constants.Control.pcImageList=Manager().list()
        constants.Control.mLanSender=lanSender.lanSender()
        constants.Control.mCapture=captureVideo.capture(preview=False)
        constants.Control.mCapture.closeCamera()
        constants.Control.mScanSlave=scanSlave.ScanSlave()
        constants.Info.STATUS_CODE=constants.Protocol.STATUS_READY


    class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        allow_reuse_address = True

    class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
        allow_reuse_address = True

        # The request handler class for our server. It is instantiated once per connection to the server, and must override the handle() method to implement communication to the client.
        def handle(self):  # NOTE self is not mLanServer, its a handle class, but mLanServeris a global so can still access it.

            #RECEIVE MESSAGE FROM CLIENT
            try:
                data=''
                finished = False
                msg = b''
                while not finished:
                    raw=self.request.recv(constants.Protocol.FILE_BUFFER_SIZE)
                    msg=b''.join([msg,raw])
                    endStop=msg.find(b'}')
                    if endStop !=-1:
                        finished = True
                commandJSON=msg[:endStop+1].decode(encoding='ascii', errors='ignore')
                data=msg[endStop+1:]
            except Exception as e:
                print('server receive error',e)
                return
            commandDict=json.loads(commandJSON)
            #don't log over common commands for speed:
            if commandDict["command"]!=constants.Protocol.CMD_SYNC_CAMERA:
                if commandDict["command"]!=constants.Protocol.CMD_SET_PI2_MODE:
                    print('client IP=', self.client_address[0], commandJSON)
                elif commandDict["PI2_MODE"] != 'captureScanImage':
                    print('client IP=', self.client_address[0], commandJSON)
                    

            #CHECK THE MESSAGE STARTS WITH THE CORRECT CODE
            if commandDict["header"]!=constants.Protocol.HEADER:
                print('header rejected')
                return
            #GET THE COMMAND
            #********************UPDATE/FIX COMMANDS*******************

            if commandDict["command"]==constants.Protocol.CMD_UPDATE_FIRMWARE:
                if constants.Info.STATUS_CODE != constants.Protocol.STATUS_BUSY:
                    constants.Info.STATUS_CODE = constants.Protocol.STATUS_BUSY
                    lanHelpers.updateFirmware(self.request, data, commandDict)
                    constants.Info.STATUS_CODE = constants.Protocol.STATUS_READY
                return
            if commandDict["command"]==constants.Protocol.CMD_FACTORY_RESET:
                if constants.Info.STATUS_CODE != constants.Protocol.STATUS_BUSY:
                    constants.Info.STATUS_CODE = constants.Protocol.STATUS_BUSY
                    lanHelpers.factoryReset()
                    constants.Info.STATUS_CODE = constants.Protocol.STATUS_READY
                return
            if commandDict["command"] == constants.Protocol.CMD_FIX_DISK:
                lanHelpers.fixDisk()
                return
            #********************CONTROL COMMANDS*******************

            if commandDict["command"] == constants.Protocol.CMD_PING:
                lanHelpers.pingReply(self.request, commandDict)
                return
            if commandDict["command"] == constants.Protocol.CMD_DIAGNOSIS_PING:
                lanHelpers.diagnosisReply(self.request)
                return
            if commandDict["command"]==constants.Protocol.CMD_CHANGE_SETTINGS:
                lanHelpers.changeSettings(commandDict)
                lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], success=True)
                return

            #********************CAMERA COMMANDS*******************
            if commandDict["command"] == constants.Protocol.CMD_SYNC_CAMERA:
                lanCamera.getCameraSyncInfo(self.request, commandDict)
                return
            if commandDict["command"]==constants.Protocol.CMD_START_CAMERA:
                lanCamera.startCamera()
                lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], msg='Done')
                return
            if commandDict["command"]==constants.Protocol.CMD_GET_CAMERA_IMAGE:
                lanCamera.getCameraImage(self.request, commandDict)
                return
            if commandDict["command"]==constants.Protocol.CMD_STOP_CAMERA_IMAGE:
                constants.Control.mCapture.closeCamera()
                lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], msg='Done')
                return
            if commandDict["command"] == constants.Protocol.CMD_UPDATE_CAMERA_SETTINGS:
                if constants.Control.mCapture is not None:
                    constants.Control.mCapture.updateCameraSettings()
                lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], msg='Done')
                return
            if commandDict["command"]==constants.Protocol.CMD_AUTO_EXP:
                bestExposure=constants.Control.mCapture.setAutoExposureThenLock()
                lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], success=True, msg=bestExposure)
                return
            #********************SCAN/ CALIBRATION COMMANDS*******************
            if commandDict["command"] == constants.Protocol.CMD_SET_PI2_MODE:
                lanHelpers.gracefullClose(self.request)
                msg=constants.Control.mScanSlave.setPi2Mode(commandDict)
                #set as command done
                mLanClientPi = lanClientPi.lanClientPi()
                mLanClientPi.commandDone(CMD_ID=commandDict["CMD_ID"], msgDict=msg)

            if commandDict["command"]==constants.Protocol.CMD_GET_SHOT_DATA:
                constants.Control.mLanSender.sendNextImageToPC((self.request), commandDict)
                return
            if commandDict["command"]==constants.Protocol.CMD_SET_CALIB_DATA:
                success=lanHelpers.setCalibData(self.request)
                lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], success=success)
                return


            if commandDict["command"]==constants.Protocol.CMD_RESET_SCAN_DATA:
                #constants.Control.decodeImageQ=JoinableQueue(maxsize=12)
                with constants.Control.imageLock:
                    constants.Control.pcImageList = Manager().list()
                lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], success=True, msg='Done')
                return




    def start(self):
        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=self.server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        print('Pi to pi server running')


def startServer():
    osCommands.setRO()
    # The purpose of making mLanServer global is so that the server thread can access all mLanServer variables, and it can pass mLanServer to projScan an triangulatorProcessor threads so they can access the same variables as the server threads to pass data around.
    #global mLanServerSlave
    constants.Control.mServer = lanServerSlave()
    try:
        constants.Control.mServer.start()
        #mLanServerSlave.mScanSlave.readyToScan(mLanServerSlave=mLanServerSlave)#blocking
        while True:
            time.sleep(99999)
    except Exception as e:
        print('server error', e)
    finally:
        lanHelpers.close()  # else can jam and need reboot


if __name__ == "__main__":
    startServer()
