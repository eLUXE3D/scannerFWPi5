import time
import constants
import osCommands
import subprocess
import raw2 as raw
import numpy as np
import os
import json
import zipfile
from shutil import copyfile
import io

import cv2
import captureVideo
import motorsArduino
import lanClientPi
import socket
import wifiStats


POLLING_TIME = 0.25  # seconds between checking for new images etc. coming in.

def setup():
    # GET HW INFO
    if os.uname()[1] in (constants.Info.MASTER_UNAME, constants.Info.PI5_UNAME):
        constants.Info.SERIAL_PI1_ACTUAL = getSerialPi()
        # constants.Info.BT_MAC_PI1 = self.getBTmacPi()
        constants.Info.MAC_PI1 = getMacPi()
        piSerialKey='SERIAL_PI1'
    if os.uname()[1] == constants.Info.SLAVE_UNAME:
        constants.Info.SERIAL_PI2_ACTUAL = getSerialPi()
        # constants.Info.BT_MAC_PI2 = self.getBTmacPi()
        constants.Info.MAC_PI2 = getMacPi()
        piSerialKey='SERIAL_PI2'

    # LOAD SETUP FILE
    try:
        file = np.load('resource')
        res = file['arr_0']
    except Exception as e:
        print(e)
        print('Resource file error')
        return  # leave defaults

    count = raw.NOISE.shape[0] - 1
    data = np.zeros((res.shape[0]), 'uint8')
    JSON = ''
    for i in range(res.shape[0]):
        if res[i] < raw.NOISE[count]:
            data[i] = res[i] + 256 - raw.NOISE[count]
        else:
            data[i] = res[i] - raw.NOISE[count]
        JSON += chr(data[i])
        count -= 1
    # print(JSON)
    commandDictList = json.loads(JSON)

    actualCPU = getSerialPi()
    for commandDict in commandDictList:
        if actualCPU == commandDict[piSerialKey]:
            break

    # SETUP HW SETTINGS IN CONSTANTS
    if actualCPU != commandDict[piSerialKey]:
        # CPU not found in list
        print('not found')
        # leave defaults
    else:
        print('found')
        if "SERIAL" in commandDict:#check field exists added in v3.02 and on
            constants.Info.SERIAL = commandDict['SERIAL']
        if "IP_PI1" in commandDict:
            constants.Protocol.IP_PI1 = commandDict['IP_PI1']
        if "IP_PI2" in commandDict:
            constants.Protocol.IP_PI2 = commandDict['IP_PI2']
        if "SERIAL_PI1" in commandDict:
            constants.Info.SERIAL_PI1 = commandDict['SERIAL_PI1']
        if "SERIAL_PI2" in commandDict:
            constants.Info.SERIAL_PI2 = commandDict['SERIAL_PI2']
        #if "BT_UUID_PI1" in commandDict:#not checked from v3.02on
        #    constants.BlueTooth.BT_UUID_PI1 = commandDict['BT_UUID_PI1']
        #if "BT_MAC_PROJ" in commandDict:#not checked from v3.02on
        #    constants.BlueTooth.BT_MAC_PROJ = commandDict['BT_MAC_PROJ']
        if "CIRCLE_PITCH" in commandDict:
            constants.Processing.CIRCLE_PITCH = float(commandDict['CIRCLE_PITCH'])
        if "PROJ_MODEL" in commandDict:
            constants.Info.PROJ_MODEL = commandDict['PROJ_MODEL']
            print('PROJ_MODEL:', constants.Info.PROJ_MODEL)
        if "LEVELLER" in commandDict:
            constants.Info.LEVELLER = commandDict['LEVELLER']
            print('LEVELLER:', constants.Info.LEVELLER)
        if "LENSES" in commandDict:
            constants.Info.LENSES = commandDict['LENSES']
            print('LENSES:', constants.Info.LENSES)
        if "TYPE" in commandDict:
            constants.Info.TYPE = commandDict['TYPE']
            print('TYPE:', constants.Info.TYPE)                       
        if "WIFI_READY" in commandDict:
            constants.Info.WIFI_READY = commandDict['WIFI_READY']
            print('WIFI_READY:', constants.Info.WIFI_READY)
        if "CODE" in commandDict:
            constants.Info.CODE = commandDict['CODE']
            print('CODE:', constants.Info.CODE)
            

def getSerialPi():
    command = "cat /proc/cpuinfo |grep Serial|cut -d' ' -f2"
    p = subprocess.check_output(command, shell=True).decode()
    p = p[0:16]
    return p

def getMacPi(interface='eth0'):
    command = "cat /sys/class/net/" + interface + "/address"
    p = subprocess.check_output(command, shell=True).decode()
    p = p[0:17]
    return p

def fixDisk():  # added in v2.05
    osCommands.fixDisk()
    print('FIX DISK')
    return

def changeSettings(commandDict):
    if "SW_VERSION" in commandDict:
        constants.Info.SW_VERSION = commandDict["SW_VERSION"]
    if "SCAN_TYPE" in commandDict:
        constants.ScanType.SCAN_TYPE = commandDict["SCAN_TYPE"]
    #if "MIN_INTENSITY" in commandDict:
    #    constants.Processing.MIN_INTENSITY = commandDict["MIN_INTENSITY"]
    #if "MAX_GRADIENT" in commandDict:
    #    constants.Processing.MAX_GRADIENT = commandDict["MAX_GRADIENT"]
    if "SOUND" in commandDict:
        constants.Scanning.SOUND = commandDict["SOUND"]
    if "IMAGE_STACK" in commandDict:
        constants.Scanning.IMAGE_STACK = commandDict["IMAGE_STACK"]
    if "COLOUR_SCAN" in commandDict:
        constants.Scanning.COLOUR_SCAN = commandDict["COLOUR_SCAN"]
    #if "EDGE_NOISE_REMOVAL" in commandDict:
    #    constants.Processing.EDGE_NOISE_REMOVAL = commandDict["EDGE_NOISE_REMOVAL"]
    if "FRINGE_MODE" in commandDict:
        constants.FringeMode.FRINGE_MODE = commandDict["FRINGE_MODE"]  # VERSION 4
    if "SCAN_IMAGE_ARRAY_FILENAMES" in commandDict:# VERSION 4
        if constants.Scanning.SCAN_IMAGE_ARRAY_FILENAMES != commandDict["SCAN_IMAGE_ARRAY_FILENAMES"]:
            constants.Scanning.SCAN_IMAGE_ARRAY_FILENAMES = commandDict["SCAN_IMAGE_ARRAY_FILENAMES"]  
            #reload images if necessary and if master
            if os.uname()[1] in (constants.Info.MASTER_UNAME, constants.Info.PI5_UNAME):
                constants.Control.mProjScreen.loadImagesAndResize()        
    if "SCAN_IMAGE_LIST" in commandDict:
        constants.Scanning.SCAN_IMAGE_LIST = commandDict["SCAN_IMAGE_LIST"]  # VERSION 4
    if "SCAN_ANGLES" in commandDict:
        constants.Scanning.SCAN_ANGLES = commandDict["SCAN_ANGLES"]  # VERSION 4
    if "START_TARGET" in commandDict:
        constants.Scanning.START_TARGET = commandDict["START_TARGET"]  # VERSION 4, needed to old optical marker units.
    if "MAG_LEVEL" in commandDict:
        constants.Scanning.MAG_LEVEL = commandDict["MAG_LEVEL"]  # VERSION 4
    #MOTOR SPEEDS - v4.05
    motorSpeedsChanged = False
    if "MAX_SPEED_V" in commandDict:
        if constants.Motor.MAX_SPEED_V != commandDict["MAX_SPEED_V"]:#if changed
            motorSpeedsChanged=True
            constants.Motor.MAX_SPEED_V = commandDict["MAX_SPEED_V"]
    if "ACCEL_V" in commandDict:
        if constants.Motor.ACCEL_V != commandDict["ACCEL_V"]:#if changed
            motorSpeedsChanged=True
            constants.Motor.ACCEL_V = commandDict["ACCEL_V"]
    if "MAX_SPEED_H" in commandDict:
        if constants.Motor.MAX_SPEED_H != commandDict["MAX_SPEED_H"]:#if changed
            motorSpeedsChanged=True
            constants.Motor.MAX_SPEED_H = commandDict["MAX_SPEED_H"]
    if "ACCEL_H" in commandDict:
        if constants.Motor.ACCEL_H != commandDict["ACCEL_H"]:#if changed
            motorSpeedsChanged=True
            constants.Motor.ACCEL_H = commandDict["ACCEL_H"]
    if motorSpeedsChanged:
        constants.Control.mMotors.setSpeeds()
    if "LEVEL_ANGLE" in commandDict:
        constants.Scanning.LEVEL_ANGLE = commandDict["LEVEL_ANGLE"]  # VERSION 4.07, should only changed for X3D system

    #PROJECTOR TIMINGS
    if "LATENCY" in commandDict:
        constants.Scanning.LATENCY = commandDict["LATENCY"]  # VERSION 4
    if "IMAGE_SYNC_ERROR_MARGIN" in commandDict:
        constants.Scanning.IMAGE_SYNC_ERROR_MARGIN = commandDict["IMAGE_SYNC_ERROR_MARGIN"]  # VERSION 4
    if "CAPTURE_START_DELAY_TARGET" in commandDict:
        constants.Scanning.CAPTURE_START_DELAY_TARGET = commandDict["CAPTURE_START_DELAY_TARGET"]  # VERSION 4
    if "DEBUG_NUMBER_IMAGES" in commandDict: # VERSION 4.05
        if constants.DEBUG.DEBUG_NUMBER_IMAGES != commandDict["DEBUG_NUMBER_IMAGES"]:#if changed
            constants.DEBUG.DEBUG_NUMBER_IMAGES = commandDict["DEBUG_NUMBER_IMAGES"]
            if os.uname()[1] in (constants.Info.MASTER_UNAME, constants.Info.PI5_UNAME):
                constants.Control.mProjScreen.loadImagesAndResize()

    #CAMERA SETTINGS
    if "ISO" in commandDict:
        constants.Scanning.ISO = commandDict["ISO"]
    if "ISO_AUTO" in commandDict:
        constants.Scanning.ISO_AUTO = commandDict["ISO_AUTO"]
    if "EXPOSURE_TIME_SCAN" in commandDict:
        constants.Scanning.EXPOSURE_TIME_SCAN = commandDict["EXPOSURE_TIME_SCAN"]
    if "SCAN_AUTO_EXPOSURE" in commandDict:
        constants.Scanning.SCAN_AUTO_EXPOSURE = commandDict["SCAN_AUTO_EXPOSURE"]
    if "AUTO_EXPOSURE_LIST" in commandDict:
        constants.Scanning.AUTO_EXPOSURE_LIST = commandDict["AUTO_EXPOSURE_LIST"]
    if "MAX_FRAME_RATE" in commandDict:
        constants.Scanning.MAX_FRAME_RATE = commandDict["MAX_FRAME_RATE"]
    if "AUTO_EXPOSURE_TARGET_MAX" in commandDict:
        constants.Scanning.AUTO_EXPOSURE_TARGET_MAX = commandDict["AUTO_EXPOSURE_TARGET_MAX"]
    if "FRAME_RATE" in commandDict:
        constants.Scanning.FRAME_RATE = commandDict["FRAME_RATE"]
    if "RESOLUTION" in commandDict:
        constants.Scanning.RESOLUTION = commandDict["RESOLUTION"]
    if "CAMERA_MODE" in commandDict:
        constants.Scanning.CAMERA_MODE = commandDict["CAMERA_MODE"]
    if "ZOOM_L" in commandDict:
        constants.Scanning.ZOOM_L = commandDict["ZOOM_L"]
    if "ZOOM_R" in commandDict:
        constants.Scanning.ZOOM_R = commandDict["ZOOM_R"]
    if "RESIZE" in commandDict:
        constants.Scanning.RESIZE = commandDict["RESIZE"]
    if "BIT_RATE" in commandDict:
        constants.Scanning.BIT_RATE = commandDict["BIT_RATE"]
    if "JPG_QUALITY" in commandDict:
        constants.Scanning.JPG_QUALITY = commandDict["JPG_QUALITY"]
    if "AUTO_EXPOSURE_DOWNSCALE" in commandDict:
        constants.Scanning.AUTO_EXPOSURE_DOWNSCALE = commandDict["AUTO_EXPOSURE_DOWNSCALE"]



def pingReply(clientPC, commandDict):
    if os.uname()[1] in (constants.Info.MASTER_UNAME, constants.Info.PI5_UNAME):
        replyDict={"pingReplyCode":constants.Info.PING_REPLY_CODE_MASTER,
                   "scannerName": constants.Info.SCANNER_NAME,
                   "hwVersion": constants.Info.HW_VERSION,
                   "swVersion": constants.Info.SW_VERSION,
                   "masterUname": constants.Info.MASTER_UNAME,
                   "slaveUname": constants.Info.SLAVE_UNAME,
                   "statusCode": constants.Info.STATUS_CODE,
                   "serial": constants.Info.SERIAL,
                   "SERIAL_PI1_ACTUAL": constants.Info.SERIAL_PI1_ACTUAL,
                   "BT_MAC_PI1": constants.Info.BT_MAC_PI1,
                   "MAC_PI1": constants.Info.MAC_PI1,
                   "PLATE_NUMBER": constants.Scanning.PLATE_NUMBER,  #added v3.01
                   "PROJ_MODEL": constants.Info.PROJ_MODEL,  #added v3.02
                   "LEVELLER": constants.Info.LEVELLER,  #added v4
                   "LENSES": constants.Info.LENSES,  # added v4
                    "TYPE": constants.Info.TYPE,
                    "WIFI_READY": constants.Info.WIFI_READY,
                   "CODE": constants.Info.CODE
                   }

    if os.uname()[1] == constants.Info.SLAVE_UNAME:
        replyDict={"pingReplyCode":constants.Info.PING_REPLY_CODE_SLAVE,
                   "scannerName": constants.Info.SCANNER_NAME,
                   "hwVersion": constants.Info.HW_VERSION,
                   "swVersion": constants.Info.SW_VERSION,
                   "masterUname": constants.Info.MASTER_UNAME,
                   "slaveUname": constants.Info.SLAVE_UNAME,
                   "statusCode": constants.Info.STATUS_CODE,
                   "serial": constants.Info.SERIAL,
                   "SERIAL_PI2_ACTUAL": constants.Info.SERIAL_PI2_ACTUAL,
                   "BT_MAC_PI2": constants.Info.BT_MAC_PI2,
                   "MAC_PI2": constants.Info.MAC_PI2,
                   "PLATE_NUMBER": constants.Scanning.PLATE_NUMBER,  # added v3.02
                   "PROJ_MODEL": constants.Info.PROJ_MODEL,  #added v3.02
                   "LEVELLER": constants.Info.LEVELLER,  #added v4
                   "LENSES": constants.Info.LENSES,  # added v4
                    "TYPE": constants.Info.TYPE,
                    "WIFI_READY": constants.Info.WIFI_READY,
                   "CODE": constants.Info.CODE
                   }

    if commandDict['header'] == 'tD':  # if its old software making the request, nobble the old PC software
        replyDict['TYPE']='ELUXE'
        replyDict['CODE']=16

    replyJSON=json.dumps(replyDict)

    try:
        clientPC.sendall(replyJSON.encode())
    except Exception as e:
        print('ERROR pingReply: ', e)
    finally:
        gracefullClose(clientPC)

    print('PING REPLY')
    return

def diagnosisReply(clientPC):#added in v2.05
    upTimeMins=int(time.clock_gettime(time.CLOCK_BOOTTIME)/60.0)
    print('upTimeMins', upTimeMins)
    strength, quality=None,None
    if os.uname()[1] in (constants.Info.MASTER_UNAME, constants.Info.PI5_UNAME):
        pingReplyCode=constants.Info.PING_REPLY_CODE_MASTER
        strength, quality=wifiStats.getWifiStrengthAndQuality()
    if os.uname()[1] == constants.Info.SLAVE_UNAME:
        pingReplyCode=constants.Info.PING_REPLY_CODE_SLAVE
    replyDict={"pingReplyCode":pingReplyCode,
               "diskInfo": osCommands.getDiskInfo(),
               "RMS_SYSTEM": constants.Scanning.RMS_SYSTEM,
               "UP_TIME_MINS": upTimeMins,
               "STRENGTH": strength,
               "QUALITY": quality
    }

    replyJSON=json.dumps(replyDict)
    try:
        clientPC.sendall(replyJSON.encode())
    except Exception as e:
        print('ERROR pingReply: ', e)
    finally:
        gracefullClose(clientPC)
    print('DIAGNOSIS REPLY')
    return

def updateFirmware(clientPC, data, commandDict):
    updateFilename = '../update.zip'  # update in update.py also
    # SWITCH TO WRITE MODE
    osCommands.setRW()

    print('Receiving update')
    # RECEIVE THE ZIPFILE
    fileSize=int(commandDict["fileSize"])
    f=getFile(clientPC, False, data, fileSize)#dont close socket yet, this will happen after donereply.
    if f is None:
        print('ERROR updateFirmware')
        return False
    with open(updateFilename, 'wb') as w:
        w.write(f.getbuffer())
    f.close()
    gracefullClose(clientPC)
    print('Got update')

    # RETURN IF ZIP BAD
    if not isGoodZip(updateFilename):
        # delete zip
        os.remove(updateFilename)
        osCommands.setRO()
        if constants.Control.mProjScreen is not None:
            constants.Control.mProjScreen.showImageFromFile(constants.Scanning.IDLE_IMAGE)
        print('zip bad')
        return False

    # ZIP OK
    print('zip ok')
    osCommands.setRO()
    close(reboot=True)

def factoryReset():
    factoryResetFilename = '../main.zip'
    updateFilename = '../update.zip'  # update in update.py also

    # SWITCH TO WRITE MODE
    osCommands.setRW()
    copyfile(factoryResetFilename, updateFilename)
    osCommands.setRO()
    close(reboot=True)

def setChargeMode():
    # SWITCH TO WRITE MODE
    osCommands.setRW()
    f = open("../chargeMode.txt", "w+")
    f.write("Blank line \r\n")
    f.close()
    osCommands.setRO()
    print('CHARGE MODE SET')

def enableWifi(SSID,pw,countryCode):
    try:
        print('Enable WiFi')
        if constants.Control.mProjScreen is not None:
            constants.Control.mProjScreen.showImageFromFile('red__')
        setChargeMode()#so projector doesn't get switched on twice during reboot.
        #copy over interfaces file to enable wifi
        osCommands.setRW()
        copyfile('interfacesMasterV4wifiON', '/etc/network/interfaces')
        #create new ssid and pw file
        os.remove('/etc/wpa_supplicant/wpa_supplicant.conf')
        f = open('/etc/wpa_supplicant/wpa_supplicant.conf', "w+")
        f.write("ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\r\n")
        f.write("update_config=1\r\n")
        f.write("country="+countryCode+"\r\n")
        f.write("network={\r\n")
        f.write('   ssid="'+SSID+'"\r\n')
        f.write('   psk="'+pw+'"\r\n')
        f.write('   key_mgmt=WPA-PSK\r\n')
        f.write('}\r\n')
        f.close()
        osCommands.setRO()
    except Exception as e:
        print('Error: enableWifi: ', e)
        if constants.Control.mProjScreen is not None:
            constants.Control.mProjScreen.showImageFromFile(constants.Scanning.IDLE_IMAGE)
        return

    close(reboot=True)#TODO can I ifdown, ifup instead?

def disableWifi():
    try:
        print('Disable WiFi')
        if constants.Control.mProjScreen is not None:
            constants.Control.mProjScreen.showImageFromFile('red__')
        setChargeMode()#so projector doesn't get switched on twice during reboot.
        #copy over interfaces file to enable wifi
        osCommands.setRW()
        copyfile('interfacesMasterV4wifiOFF', '/etc/network/interfaces')
        osCommands.setRO()
    except Exception as e:
        print('Error: disableWifi: ', e)
        if constants.Control.mProjScreen is not None:
            constants.Control.mProjScreen.showImageFromFile(constants.Scanning.IDLE_IMAGE)
        return

    close(reboot=True)#TODO can I ifdown, ifup instead?


def isGoodZip(updateFilename):
    try:
        the_zip_file = zipfile.ZipFile(updateFilename)
        the_zip_file.setpassword(constants.Protocol.UPDATE_PWD)
        ret = the_zip_file.testzip()
        if ret is not None:  # bad zip
            return False
    except Exception as e:
        print(e)
        return False
    return True




def close(reboot=False):
    try:
        constants.Control.decodeImageQ=None# must do this else port jams as in use.
        constants.Control.mServer.server.shutdown()
        constants.Control.mServer.server.server_close()
        print('Pi to pi server closed')
    except Exception as e:
        print('close error', e)

    try:
        if constants.Control.mProjScreen is not None:
            constants.Control.mProjScreen.closeProjWindow()
    except Exception as e:
        print('close error2', e)

    if reboot:
        osCommands.osReboot()

def doneReply(clientPC, CMD_ID, success=True, msg='-'):
    #SHOW DONE BY SENDING NUMPY FILE
    tick = time.time()
    msg=np.array([msg], dtype=object)
    # PUT NUMPY IMAGE INTO A FILE IN MEMORY
    f = io.BytesIO()
    np.savez(f, CMD_ID=CMD_ID, success=success, msg=msg)
    # SEND NUMPY TO CLIENT
    f.seek(0, 0)
    try:
        clientPC.sendfile(f, 0)
    except Exception as e:
        print('ERROR sendDoneToPC: ', e)
    finally:
        gracefullClose(clientPC)

    f.close()
    return

def gracefullClose(clientPC):
    try:
        clientPC.shutdown(socket.SHUT_WR) #I've finished writing
        check = clientPC.recv(constants.Protocol.FILE_BUFFER_SIZE)  # have you finished sending? should be 0 length received if so
        while (check):
            print('Waiting for graceful close', clientPC.getsockname())
            check = clientPC.recv(constants.Protocol.FILE_BUFFER_SIZE)
        clientPC.close()
    except Exception as e:
        print('ERROR: gracefullClose ', e)

#************************************* BELOW ARE USED BY LAN MASTER ONLY *****************************************************************************



def waitForPi2Ready():
    finished = False
    print('Waiting for Pi2')
    while not finished:
        mLanClientPi = lanClientPi.lanClientPi()
        commandJSON = mLanClientPi.pingScanner(constants.Protocol.IP_PI2, constants.Protocol.TCP_PORT_PI2)
        if mLanClientPi.connectionFail or commandJSON=='':
            connected = False
        else:
            connected = True
        if connected:
            commandDict = json.loads(commandJSON)
            statusCode = commandDict["statusCode"]

            if statusCode == constants.Protocol.STATUS_READY:
                finished = True

        print(connected, finished)
        time.sleep(3)
    print('Pi2 Ready')

        
def getCalibData(clientPC, commandDict):#calib file from pi to PC
    try:
        filename = commandDict['filename']
        f = open(filename, 'rb')
        f.seek(0, 0)
        clientPC.sendfile(f, 0)
    except Exception as e:
        print('ERROR getCalibData: ', e)
    finally:
        gracefullClose(clientPC)
    f.close()
    return

def getPlateFile(clientPC, commandDict):#calib file from pi to PC
    plateFileNumber=commandDict['plateFileNumber']
    platePathAndFilename='plateFiles/plateFile_' + '{:05d}'.format(plateFileNumber) + '.npz'

    f = open(platePathAndFilename, 'rb')
    f.seek(0, 0)
    try:
        clientPC.sendfile(f, 0)
    except Exception as e:
        print('ERROR getPlateFile: ', e)
    finally:
        gracefullClose(clientPC)
    f.close()
    return

def setCalibData(clientPC, data, commandDict):#calib file from PC to pi
    try:
        if constants.Control.mProjScreen is not None:
            constants.Control.mProjScreen.showImageFromFile('red__')
        fileSize=int(commandDict["fileSize"])
        filename = commandDict['filename']
        f=getFile(clientPC, False, data, fileSize)#dont close socket yet, this will happen after donereply.
        if f is None:
            print('ERROR setCalibData')
            return False
        osCommands.setRW()
        with open(filename, 'wb') as w:
            w.write(f.getbuffer())
        osCommands.setRO()
        f.close()
        if constants.Control.mProjScreen is not None:
            constants.Control.mProjScreen.showImageFromFile(constants.Scanning.IDLE_IMAGE)
    except Exception as e:
        print('ERROR2 setCalibData: ', e)

    return True

def setMSG(commandDict):
    try:
        if constants.Control.mProjScreen is not None:
            constants.Control.mProjScreen.showImageFromFile('red__')
        message = commandDict['message']
        filename = 'msg'
        osCommands.setRW()
        with open(filename, 'w') as w:
            w.write(message)
        osCommands.setRO()
        if constants.Control.mProjScreen is not None:
            constants.Control.mProjScreen.showImageFromFile(constants.Scanning.IDLE_IMAGE)
    except Exception as e:
        print('ERROR setMSG: ', e)

    return True

def getMSG(clientPC, commandDict):
    message=''
    try:
        filename = 'msg'
        with open(filename, "r") as file:
            message = file.read()
            print(message)

    except Exception as e:
        print('ERROR getMSG: ', e)

    replyDict={}
    replyDict['message']=message

    replyJSON=json.dumps(replyDict)

    try:
        clientPC.sendall(replyJSON.encode())
    except Exception as e:
        print('ERROR getMSG: ', e)
    finally:
        gracefullClose(clientPC)

    print('getMSG REPLY')
    return

def checkIfDone(CMD_ID, timeout=None):
    done = False
    msgDict = {}
    startTime = time.perf_counter()
    while not done:
        try:
            # index = doneCommands.index(CMD_ID)
            index = [cmd[0] for cmd in constants.Control.doneCommands].index(CMD_ID)  # searching pos[0] in list of tuples
            cmdID, msgDict = constants.Control.doneCommands.pop(index)
            done = True
        except:  # if CMD_ID not in list yet
            if timeout is not None:
                if time.perf_counter() - startTime > timeout:
                    return False, msgDict
            constants.Control.newCommandDoneFlag.wait()
            constants.Control.newCommandDoneFlag.clear()
            # time.sleep(0.005)

    return True, msgDict

def getNPZfile(clientPC, closeSocket, data, fileSize):#need to close NPZ, and F after.
    f=getFile(clientPC, closeSocket, data, fileSize)
    npz = np.load(f, allow_pickle=True)
    return npz, f

def getFile(clientPC, closeSocket, data, fileSize):#need to close F after.
    tick=time.perf_counter()
    recvError = False
    f = io.BytesIO()
    bytesReceived = 0
    if data is not None:
        if len(data)!=0:
            bytesReceived+=len(data)
            f.write(data)#write data that was accidentally captured by json header capture.
        
    try:
        while bytesReceived<fileSize:
            data = clientPC.recv(constants.Protocol.FILE_BUFFER_SIZE)
            f.write(data)
            bytesReceived+=len(data)
    except Exception as e:
        print('ERROR: getFile', e)
        recvError = True
    finally:
        if closeSocket:
            gracefullClose(clientPC)

    f.seek(0, 2)
    fileSizeInt = f.tell()
    fileSize = '{:09d}'.format(fileSizeInt)
    print('Got file size', fileSize, 'time', time.perf_counter()-tick)

    if fileSizeInt == 0 or recvError:
        print('ERROR receiving file')
        f.close()
        return None

    f.seek(0, 0)

    return f
