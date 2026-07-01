import captureVideo
import time
import os
import numpy as np
import cv2
import constants
import lanClientPi
import realTimeAsync2
import projSequence
from multiprocessing import Manager#, JoinableQueue
import gc
import copy


#CONSTANTS
CALIB_IMAGE_PATH = 'scanData/calib'

class ScanSlave():
            
    def __init__(self):
        self.mTriangulateProcessor=None
        self.mCalibProcessor=None
        self.calibImages=None
        self.expectedImages=0

    def setPi2Mode(self, commandDict):
        msg={}
        #FAST SCANNING
        if commandDict["PI2_MODE"] == 'fastScan':
            self.setUpFastScan(commandDict)
            return msg
        if commandDict["PI2_MODE"] == 'captureScanImagesFast':
            msg=self.captureScanImagesFast(commandDict)
            return msg
        if commandDict["PI2_MODE"] == 'processScanShotFast':
            self.processScanShotFast(commandDict)
            return msg
        if commandDict["PI2_MODE"] == 'processScanFast':
            self.processScanFast(commandDict)
            return msg
        if commandDict["PI2_MODE"] == 'cancelScanFast':
            self.cancelScanFast(commandDict)
            return msg


#FAST SCAN
    def setUpFastScan(self, commandDict):
        #SET UP CAMERA
        #constants.Control.mCapture = captureVideo.capture(preview=False)
        #constants.Control.mCapture.setResolution((constants.Scanning.CAPTURE_W, constants.Scanning.CAPTURE_H))  # crop to 4/3 aspect from now
        #msec = commandDict["EXPOSURE_TIME_SCAN"]
        #constants.Control.mCapture.setExposure(msec)
        #constants.Control.decodeImageQ=JoinableQueue(maxsize=12)#clear images
        with constants.Control.imageLock:
            constants.Control.pcImageList=Manager().list()
        #self.mTriangulateProcessor = triangulateProcessorSlave.triangulateProcessor(useProcesses=True)

        #SET UP REAL TIME VIDEO CAPTURE
        constants.Control.mRealTime=realTimeAsync2.RealTimeProcessing(syncMaster=False)
        constants.Control.mCapture.startVideoAndProcessing(mode='mjpeg')
        constants.Control.mRealTime.waitForFirstFrame()
        constants.Control.mRealTime.syncingCameras=True
        colourImage=None
        frameTime=1000*1.0/constants.Control.mCapture.camera.framerate#frame time in msec
        print('FrameTime: ',frameTime)

    def captureScanImagesFast(self,commandDict):#TODO if retry need to remove, old images from imageset, (only if because of projError) 
        captureTimeList=commandDict["CAPTURE_TIME_LIST"]
        scanImageList=commandDict["SCAN_IMAGE_LIST"]
        retry=commandDict["RETRY"]
        if not retry:
            self.expectedImages=len(scanImageList)
        imageOrder=commandDict["IMAGE_ORDER"]
        projErrorListPi1=[]
        if "PROJ_ERROR_LIST" in commandDict:
            projErrorListPi1=commandDict["PROJ_ERROR_LIST"]
        captureTimeListInPi2Time=[]
        clockOffset=constants.Protocol.CLOCK_OFFSET#TODO can be None on 1.2sec exposure, and crash.
        #convert time list to pi2 time
        for captureTime in captureTimeList:
            captureTimeListInPi2Time.append((captureTime[0] + clockOffset, captureTime[1] + clockOffset))

        constants.Control.mRealTime.removeProjErrorsFromImageSet(projErrorListPi1)
            
        constants.Control.mRealTime.captureRequest(captureTimeListInPi2Time, scanImageList=scanImageList, retry=retry)
        successPi2, missingImageListPi2, dummy=constants.Control.mRealTime.waitForFrameCapture()
        if retry and successPi2:
            constants.Control.mRealTime.reorderLists(imageOrder)
        msg={}
        msg['SUCCESS_PI2']=successPi2
        msg['MISSING_IMAGE_LIST_PI2']=missingImageListPi2
        return msg

    def processScanShotFast(self, commandDict):
        i=commandDict["SHOT_NUMBER"]
        SCAN_ID=commandDict["SCAN_ID"]
        #constants.Control.decodeImageQ.put([i, 'R', np.asarray(constants.Control.mRealTime.imageSet), 0, 0, 0, 0, 0, 0, self.expectedImages], True)
        with constants.Control.imageLock:
            constants.Control.pcImageList.append([copy.deepcopy(i), copy.deepcopy(np.asarray(constants.Control.mRealTime.imageSet)),  0, copy.deepcopy(self.expectedImages), copy.deepcopy(SCAN_ID)])
        if constants.DEBUG.SAVE_SCAN_IMAGES:
            projSequence.saveDebugImagesFast(constants.Control.mRealTime,i)

    def processScanFast(self, commandDict):
        SCAN_ID=commandDict["SCAN_ID"]
        exitCode = -1
        time.sleep(0.1)#may help queue order.
        #constants.Control.decodeImageQ.put([exitCode, 'R', 0, 0, 0, 0, 0, 0, 0,0], True)
        with constants.Control.imageLock:
            constants.Control.pcImageList.append([exitCode, 0, 0,0, SCAN_ID])
        constants.Control.mCapture.stopVideo()
        constants.Control.mCapture.closeCamera()
        constants.Control.mRealTime = None  # clear memory

    def cancelScanFast(self, commandDict):
        SCAN_ID=commandDict["SCAN_ID"]
        exitCode = -2
        time.sleep(0.1)#may help queue order.
        #constants.Control.decodeImageQ.put([exitCode, 'R', 0, 0, 0, 0, 0, 0, 0,0], True)
        with constants.Control.imageLock:
            constants.Control.pcImageList.append([exitCode,0, 0,0, SCAN_ID])
        constants.Control.mCapture.stopVideo()
        constants.Control.mCapture.closeCamera()
        constants.Control.mRealTime = None  # clear memory
        gc.collect()


            
if __name__ == "__main__":
    print("cv2 version", cv2.__version__)
    mScanSlave=ScanSlave()
    mScanSlave.readyToScan()

