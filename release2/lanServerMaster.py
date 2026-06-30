import threading
import socketserver
import time
from multiprocessing import Manager, JoinableQueue
import constants
import scanMaster
import os
try:
    if constants.DEBUG.PROJ_SCREEN_DEBUG_MODE:
        import projScreen#pygame based - works in gui
    else:
        import projScreenFB as projScreen#direct screen access from CLI - much faster.
except:
    print('could not import')#happens on pi2, when no display?
import motorsArduino
import json
import playSound
import captureVideo
import osCommands
import netifaces
import lanHelpers
import lanCamera
import lanSender
from threading import Event
import loadStartTarget
import scanSlave


def _is_pi5():
    return os.uname()[1] == constants.Info.PI5_UNAME


POLLING_TIME=0.25#seconds between checking for new images etc. coming in.

class lanServerMaster():
    # variable shared over all classes - gets run even on import : so should not init here else could lose data if re-imported later?

    def __init__(self):
        # variable for this instance - self..
        lanHelpers.setup()

        #GET IP ADDRESS OF THIS MASTER
        ipAddress=None
        while ipAddress is None:
            ipAddress=self.getIPaddressFromPort(ifname='usb0')#PC
            time.sleep(1)
        constants.Protocol.IP_PI1=ipAddress
        print('constants.Protocol.IP_PI1', constants.Protocol.IP_PI1)
        
        self.server = self.ThreadedTCPServer((constants.Protocol.IP_PI1, constants.Protocol.TCP_PORT), self.ThreadedTCPRequestHandler)  # Port 0 means to select an arbitrary unused port
        
        #classes – Camera 0 (left / master camera)
        constants.Control.mCapture=captureVideo.capture(preview=False, camera_id=0)
        constants.Control.mCapture.closeCamera()

        # Pi5: also initialise Camera 1 (right / slave camera)
        if _is_pi5():
            constants.Control.mCaptureRight = captureVideo.capture(preview=False, camera_id=1)
            constants.Control.mCaptureRight.closeCamera()
            constants.Control.mScanSlaveLocal = scanSlave.ScanSlave()
            print('Pi5: right camera and local ScanSlave initialised')

        constants.Control.mProjScreen=projScreen.projScreen()
        constants.Control.mProjScreen.loadImagesAndResize()
        constants.Control.mProjScreen.showImageFromFile('magen')
        constants.Control.mScanMaster=scanMaster.ScanMaster()
        
        #queues and flags
        with constants.Control.imageLock:
            constants.Control.pcImageList=Manager().list()
        constants.Control.mLanSender=lanSender.lanSender()
        constants.Control.requestDoneEvent = Event()
        constants.Control.requestDoneEvent.set()
        constants.Control.doneCommands = Manager().list()
        constants.Control.newCommandDoneFlag = Event()
        constants.Control.newCommandDoneFlag.clear()

        constants.Control.calibPointsData = Manager().list()  # regular list does not allow access from another thread
        constants.Control.calibrationDataReady = Manager().list()  # empty list means false, any entries mean True, so can send calibrationData.npz to pi2
        constants.Control.cancelList = Manager().list()  # empty list means false, any entries mean True, regular list does not allow access from another thread

        print('STARTING MICRO-CONTROLLER...')
        constants.Control.mMotors = motorsArduino.motorsArduino()
        print('MICRO-CONTROLLER FUNCTIONAL')

        constants.Scanning.START_TARGET=loadStartTarget.loadStartTargetFromCalibData()
        print('START_TARGET: ', constants.Scanning.START_TARGET)
        constants.Info.STATUS_CODE = constants.Protocol.STATUS_READY

    def getIPaddressFromPort(self, ifname='usb0'):
        try:
            ipAddresses=netifaces.ifaddresses(ifname)
            ipAddress=ipAddresses[netifaces.AF_INET][0]['addr']#AF_INET if normal ip4 address
            print(ifname, ipAddress)
        except Exception as e:
            print('ERROR getIPaddressFromPort', e)
            return None
        return ipAddress
 
    class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        allow_reuse_address=True

    class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
        allow_reuse_address=True
        
        def handle(self):#NOTE self is not mLanServer, its a handle class, so get variables globally
            #RECEIVE MESSAGE FROM CLIENT
            try:
                data=''
                finished = False
                msg = b''
                while not finished:
                    rawData=self.request.recv(constants.Protocol.FILE_BUFFER_SIZE)
                    msg=b''.join([msg,rawData])
                    endStop=msg.find(b'}')
                    if endStop !=-1:
                        finished = True
                commandJSON=msg[:endStop+1].decode(encoding='ascii', errors='ignore')
                data=msg[endStop+1:]
            except Exception as e:
                print('server receive error',e)
                return

            commandDict=json.loads(commandJSON)
            
            #Don't print over common commands
            if commandDict["command"]!=constants.Protocol.CMD_DONE:
                print('client IP=', self.client_address[0], commandJSON)

            #CHECK THE MESSAGE STARTS WITH THE CORRECT CODE
            if commandDict["header"]!=constants.Protocol.HEADER:
                print('header rejected')
                return
            #GET THE COMMAND
            #********************UPDATE/FIX COMMANDS*******************
            if commandDict["command"]==constants.Protocol.CMD_REBOOT:
                lanHelpers.gracefullClose(self.request)
                lanHelpers.close(reboot=True)
                return
            if commandDict["command"]==constants.Protocol.CMD_UPDATE_FIRMWARE:
                if constants.Info.STATUS_CODE != constants.Protocol.STATUS_BUSY:
                    constants.Info.STATUS_CODE = constants.Protocol.STATUS_BUSY
                    lanHelpers.updateFirmware(self.request, data, commandDict)
                    constants.Info.STATUS_CODE = constants.Protocol.STATUS_READY
                return
            if commandDict["command"]==constants.Protocol.CMD_FACTORY_RESET:
                lanHelpers.gracefullClose(self.request)
                if constants.Info.STATUS_CODE != constants.Protocol.STATUS_BUSY:
                    constants.Info.STATUS_CODE = constants.Protocol.STATUS_BUSY
                    lanHelpers.factoryReset()
                    constants.Info.STATUS_CODE = constants.Protocol.STATUS_READY
                return
            if commandDict["command"] == constants.Protocol.CMD_FIX_DISK:
                lanHelpers.fixDisk()
                return
            if commandDict["command"]==constants.Protocol.CMD_SET_CHARGE_MODE:
                lanHelpers.setChargeMode()
                return
            if commandDict["command"]==constants.Protocol.CMD_ENABLE_WIFI:
                if constants.Info.STATUS_CODE != constants.Protocol.STATUS_BUSY:
                    constants.Info.STATUS_CODE = constants.Protocol.STATUS_BUSY#lock until pi rebooted so can't enable twice
                    lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], msg='Done')
                    lanHelpers.enableWifi(SSID=commandDict["SSID"],pw=commandDict["pw"],countryCode=commandDict["countryCode"])
                    constants.Info.STATUS_CODE = constants.Protocol.STATUS_READY#only used if restart fails
                else:
                    lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], msg='Done')
                return
            if commandDict["command"]==constants.Protocol.CMD_DISABLE_WIFI:
                if constants.Info.STATUS_CODE != constants.Protocol.STATUS_BUSY:
                    constants.Info.STATUS_CODE = constants.Protocol.STATUS_BUSY#lock until pi rebooted so can't enable twice
                    lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], msg='Done')
                    lanHelpers.disableWifi()
                    constants.Info.STATUS_CODE = constants.Protocol.STATUS_READY  # only used if restart fails
                else:
                    lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], msg='Done')
                return
            #********************CONTROL COMMANDS*******************
            if commandDict["command"] == constants.Protocol.CMD_PING:
                lanHelpers.pingReply(self.request, commandDict)
                return
            if commandDict["command"] == constants.Protocol.CMD_DIAGNOSIS_PING:
                lanHelpers.diagnosisReply(self.request)
                return
            if commandDict["command"] == constants.Protocol.CMD_DONE:
                constants.Control.doneCommands.append((commandDict["CMD_ID"], commandDict))
                constants.Control.newCommandDoneFlag.set()
                return
            if commandDict["command"]==constants.Protocol.CMD_SET_MSG:
                success=lanHelpers.setMSG(commandDict)
                lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], success=success)
                return
            if commandDict["command"]==constants.Protocol.CMD_GET_MSG:
                lanHelpers.getMSG(self.request, commandDict)
                return

            #********************CAMERA COMMANDS*******************

            if commandDict["command"]==constants.Protocol.CMD_GET_CAMERA_IMAGE:
                lanCamera.getCameraImage(self.request, commandDict)
                return
            if commandDict["command"]==constants.Protocol.CMD_START_CAMERA:
                lanCamera.startCamera()
                lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], msg='Done')
                return
            if commandDict["command"]==constants.Protocol.CMD_STOP_CAMERA_IMAGE:
                constants.Control.mCapture.closeCamera()
                lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], msg='Done')
                return
            if commandDict["command"] == constants.Protocol.CMD_UPDATE_CAMERA_SETTINGS:
                if constants.Control.mCapture is not None:
                    constants.Control.mCapture.updateCameraSettings()
                lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], success=True)
                return
            if commandDict["command"]==constants.Protocol.CMD_AUTO_EXP:
                bestExposure=constants.Control.mCapture.setAutoExposureThenLock()
                lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], success=True, msg=bestExposure)
                return

            #********************MOTOR COMMANDS*******************
            if commandDict["command"] == constants.Protocol.CMD_MOTOR_POWER:
                constants.Control.mMotors.powerOn(commandDict["motorV"], commandDict["motorH"])
                lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], success=True)
                return
            if commandDict["command"] == constants.Protocol.CMD_MOTOR_TO_ZERO:
                constants.Control.mMotors.moveToZero()
                lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], success=True)
                return
            if commandDict["command"] == constants.Protocol.CMD_MOTOR_MOVE_TO:
                constants.Control.mMotors.moveToTwoAngles(commandDict["motorV"], commandDict["motorH"], shortestRouteH=True)
                lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], success=True)
                return
            if commandDict["command"] == constants.Protocol.CMD_MOTOR_MOVE_BY:
                constants.Control.mMotors.moveByTwoAngles(commandDict["motorV"], commandDict["motorH"])
                lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], success=True)
                return
            if commandDict["command"] == constants.Protocol.CMD_MOTOR_SET_CURRENT_ANGLE_TO_ZERO:
                commandDict["motorNumber"]
                constants.Control.mMotors.setMotorNumber(commandDict["motorNumber"])
                constants.Control.mMotors.setCurrentAngleToZero()
                lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], success=True)
                return
            if commandDict["command"] == constants.Protocol.CMD_MOTOR_CALIB_OPTICAL_ZERO:
                startTarget=constants.Control.mMotors.calibOpticalMarkerZero()
                lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], success=True, msg=startTarget)
                return
            if commandDict["command"] == constants.Protocol.CMD_GET_MAG_READING:
                magReading=constants.Control.mMotors.getMag()
                lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], success=True, msg=magReading)
                return            
            
            
            #********************PROJECTOR COMMANDS*******************
            if commandDict["command"]==constants.Protocol.CMD_PLAY_SOUND:
                playSound.file(soundCode=commandDict["soundCode"])
                return
            if commandDict["command"]==constants.Protocol.CMD_PROJ_IMAGE:
                constants.Control.mProjScreen.showImageFromFile(commandDict["imageName"])
                lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], success=True)
                return
            #********************CALIBRATION COMMANDS*******************
            if commandDict["command"]==constants.Protocol.CMD_GET_CALIB_DATA:
                lanHelpers.getCalibData(self.request, commandDict)
                return
            if commandDict["command"]==constants.Protocol.CMD_SET_CALIB_DATA:
                success=lanHelpers.setCalibData(self.request,data,commandDict)
                lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], success=success)
                return
            if commandDict["command"]==constants.Protocol.CMD_GET_PLATE_FILE:
                lanHelpers.getPlateFile(self.request, commandDict)
                return
            #********************SCAN COMMANDS*******************
            if commandDict["command"]==constants.Protocol.CMD_SCAN:
                lanHelpers.gracefullClose(self.request)
                if constants.Info.SERIAL_PI1 != constants.Info.SERIAL_PI1_ACTUAL:
                    constants.Info.HW_VERSION='Unknown'
                    return
                constants.Control.doneCommands = Manager().list()
                constants.Control.newCommandDoneFlag = Event()
                constants.Control.newCommandDoneFlag.clear()
                #start scan
                if 'SCAN_ID' in commandDict:
                    SCAN_ID= commandDict["SCAN_ID"]
                else:
                    SCAN_ID=None
                constants.Control.mScanMaster.projScan(SCAN_ID=SCAN_ID)
                return
            if commandDict["command"]==constants.Protocol.CMD_GET_SHOT_DATA:
                constants.Control.mLanSender.sendNextImageToPC(self.request, commandDict)
                return

            if commandDict["command"]==constants.Protocol.CMD_CHANGE_SETTINGS:
                lanHelpers.changeSettings(commandDict)
                lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], success=True)
                return

            if commandDict["command"]==constants.Protocol.CMD_CANCEL:
                constants.Control.cancelList.append(True)
                lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], success=True)
                return

            if commandDict["command"]==constants.Protocol.CMD_RESET_SCAN_DATA:
                with constants.Control.imageLock:
                    constants.Control.pcImageList=Manager().list()
                constants.Control.cancelList=Manager().list()
                lanHelpers.doneReply(self.request, CMD_ID=commandDict["CMD_ID"], success=True)
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
    constants.Control.mServer=lanServerMaster()
    try:
        constants.Control.mServer.start()
        if not _is_pi5():
            # Pi4: wait for the slave Pi to be ready before showing idle image
            lanHelpers.waitForPi2Ready()
        constants.Control.mProjScreen.showImageFromFile(constants.Scanning.IDLE_IMAGE)
        while True:
            time.sleep(99999)
    except Exception as e:
        print('server error',e)
    finally:
        lanHelpers.close()#else can jam and need reboot
    
if __name__ == "__main__":
    startServer()
