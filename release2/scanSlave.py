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

    def _capture(self):
        """Return the capture object for the right camera."""
        return constants.Control.mCaptureRight

    def _realtime(self):
        """Return the RealTimeProcessing object for the right camera."""
        return constants.Control.mRealTimeRight

    def _set_realtime(self, rt):
        """Assign a new RealTimeProcessing object for the right camera."""
        constants.Control.mRealTimeRight = rt

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
        with constants.Control.imageLock:
            constants.Control.pcImageList=Manager().list()

        # Camera 1 (right camera)
        rt = realTimeAsync2.RealTimeProcessing(syncMaster=False, camera_id=1)
        self._set_realtime(rt)

        self._capture().startVideoAndProcessing(mode='mjpeg')
        rt.waitForFirstFrame()
        rt.syncingCameras=True
        frameTime=1000*1.0/self._capture().camera.framerate#frame time in msec
        print('FrameTime (slave):', frameTime)

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

        # On Pi5 both cameras share the same hardware clock so offset is 0.
        clockOffset = constants.Protocol.CLOCK_OFFSET if constants.Protocol.CLOCK_OFFSET is not None else 0
        captureTimeListInSlaveTime=[]
        for captureTime in captureTimeList:
            captureTimeListInSlaveTime.append((captureTime[0] + clockOffset, captureTime[1] + clockOffset))

        rt = self._realtime()
        rt.removeProjErrorsFromImageSet(projErrorListPi1)
        rt.captureRequest(captureTimeListInSlaveTime, scanImageList=scanImageList, retry=retry)
        successSlave, missingImageListSlave, dummy=rt.waitForFrameCapture()
        if retry and successSlave:
            rt.reorderLists(imageOrder)
        msg={}
        msg['SUCCESS_PI2']=successSlave
        msg['MISSING_IMAGE_LIST_PI2']=missingImageListSlave
        return msg

    def processScanShotFast(self, commandDict):
        i=commandDict["SHOT_NUMBER"]
        SCAN_ID=commandDict["SCAN_ID"]
        rt = self._realtime()
        with constants.Control.imageLock:
            constants.Control.pcImageList.append([copy.deepcopy(i), copy.deepcopy(np.asarray(rt.imageSet)),  0, copy.deepcopy(self.expectedImages), copy.deepcopy(SCAN_ID)])
        if constants.DEBUG.SAVE_SCAN_IMAGES:
            projSequence.saveDebugImagesFast(rt, i)

    def processScanFast(self, commandDict):
        SCAN_ID=commandDict["SCAN_ID"]
        exitCode = -1
        time.sleep(0.1)#may help queue order.
        with constants.Control.imageLock:
            constants.Control.pcImageList.append([exitCode, 0, 0, 0, SCAN_ID])
        self._capture().stopVideo()
        self._capture().closeCamera()
        self._set_realtime(None)  # clear memory

    def cancelScanFast(self, commandDict):
        SCAN_ID=commandDict["SCAN_ID"]
        exitCode = -2
        time.sleep(0.1)#may help queue order.
        with constants.Control.imageLock:
            constants.Control.pcImageList.append([exitCode,0, 0,0, SCAN_ID])
        self._capture().stopVideo()
        self._capture().closeCamera()
        self._set_realtime(None)  # clear memory
        gc.collect()


            
if __name__ == "__main__":
    print("cv2 version", cv2.__version__)
    mScanSlave=ScanSlave()
    mScanSlave.readyToScan()

