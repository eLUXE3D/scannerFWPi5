try:
    import captureVideo
    import motorsArduino
except:
    print('could not import')
import time
import os
import numpy as np
import playSound
import cv2
import constants
import realTimeAsync2
import projSequence
import os
import lanClientPi
import lanHelpers
from multiprocessing import Manager, JoinableQueue
import traceback
import gc
import copy

VERTICAL_LEVEL=-32.4#deg

class ScanMaster():
            
    def __init__(self):
        pass


    def projScan(self, SCAN_ID=None):#FAST SCAN
        startTime=time.perf_counter()
        #SETUP READY FOR SCAN

        #SETUP SCAN ANGLES
        scanAngles=constants.Scanning.SCAN_ANGLES
        print('Scan Angles: ',scanAngles)
        gc.collect()

        #PI 2 - start scan with known exposure.
        mLanClientPi = lanClientPi.lanClientPi()
        cmdID_initPi2 = mLanClientPi.setPi2mode(PI2_MODE='fastScan')#, EXPOSURE_TIME_SCAN=msec)
        #block until pi2 command done
        success,msg=lanHelpers.checkIfDone(cmdID_initPi2)
        
        #DO SCAN
        shotNumber=0
        with constants.Control.imageLock:
            constants.Control.pcImageList = Manager().list()  # clear imaage queue
            
        #SET UP REALTIME VIDEO PROCESSOR
        print('Projector timings, latency, startDelay, errorMargin:',constants.Scanning.LATENCY, constants.Scanning.CAPTURE_START_DELAY_TARGET, constants.Scanning.IMAGE_SYNC_ERROR_MARGIN)
        constants.Control.mRealTime=realTimeAsync2.RealTimeProcessing(syncMaster=True)
        constants.Control.mCapture.startVideoAndProcessing(mode='mjpeg')
        constants.Control.mRealTime.waitForFirstFrame()
        constants.Control.mRealTime.syncingCameras=True
        frameSyncWaitTime=constants.Control.mRealTime.frameTime*15/1000000#TODO could get feedback - more efficient, but risk bugs (e.g. frame sync'd but not stable yet, needs care to implement).
        print('Wait 15 frames for sync:', frameSyncWaitTime)
        time.sleep(frameSyncWaitTime)
        
        print('Number of shots to take=',len(scanAngles))
        cancelled=False
        frameTime=1000*1.0/constants.Control.mCapture.camera.framerate
        print('FrameTime: ', frameTime)
        
        niceness=os.nice(-20)
        print('main loop niceness', niceness)
        #print('start seq at:', time.perf_counter()-startTime)
        tick=time.perf_counter() 

        try:
            lastVertAngle=999
            for vertAngle, horizAngle in scanAngles:
                if self.cancel():
                    cancelled=True
                    mLanClientPi = lanClientPi.lanClientPi()
                    cmdID_cancelPi2 = mLanClientPi.setPi2mode(PI2_MODE='cancelScanFast', SCAN_ID=SCAN_ID)
                    break
                constants.Control.mMotors.moveToTwoAngles(vertAngle, horizAngle, shortestRouteH=True)
                if vertAngle!=lastVertAngle:#if moved vertically need to wait longer to settle
                    time.sleep(constants.Scanning.SETTLE_TIME_VERT)
                else:
                    time.sleep(constants.Scanning.SETTLE_TIME)
                lastVertAngle=vertAngle
                angleData=np.array([vertAngle,horizAngle])
                
                projSequence.projSeqAsync(scanImageList=constants.Scanning.SCAN_IMAGE_LIST)
                
                #PUT PI1 IMAGE SET ON QUEUE
                with constants.Control.imageLock:
                    constants.Control.pcImageList.append([copy.deepcopy(shotNumber), copy.deepcopy(np.asarray(constants.Control.mRealTime.imageSet)), copy.deepcopy(angleData),copy.deepcopy(len(constants.Scanning.SCAN_IMAGE_LIST)), copy.deepcopy(SCAN_ID)])
                # PUT PI2 IMAGE SET ON QUEUE
                mLanClientPi = lanClientPi.lanClientPi()
                cmdID_processScanShot = mLanClientPi.setPi2mode(PI2_MODE='processScanShotFast', SHOT_NUMBER=shotNumber, SCAN_ID=SCAN_ID)

                if constants.DEBUG.SAVE_SCAN_IMAGES:
                    projSequence.saveDebugImagesFast(constants.Control.mRealTime, shotNumber)
                
                lanHelpers.checkIfDone(cmdID_processScanShot)
                shotNumber+=1
            if not cancelled:
                pass
                mLanClientPi = lanClientPi.lanClientPi()
                cmdID_processPi2 = mLanClientPi.setPi2mode(PI2_MODE='processScanFast', SCAN_ID=SCAN_ID)
        except Exception as e:
            print("Scanning error", e)
            traceback.print_exc()
        

        #CLOSE UP AND PROCESS
        print("scan time", time.perf_counter()-tick)
        self.scanShutDown(cancelled=cancelled)

        if cancelled:
            exitCode=-2
            time.sleep(0.2)#maybe needed to ensure -1 does not skip queue order. Used to happen weirdly in triandMasterProcessor, so assume could happen here.
            #constants.Control.decodeImageQ.put([exitCode, 'L', 0, 0, 0,0,0,0,0,0],True)
            with constants.Control.imageLock:
                constants.Control.pcImageList.append([exitCode,0,0,0, SCAN_ID])
            constants.Control.mProjScreen.showImageFromFile(constants.Scanning.IDLE_IMAGE)
            constants.Control.mMotors.powerOn(False, False)
        else:
            exitCode=-1
            time.sleep(0.2)#maybe needed to ensure -1 does not skip queue order. Used to happen weirdly in triandMasterProcessor, so assume could happen here.
            #constants.Control.decodeImageQ.put([exitCode, 'L', 0, 0, 0,0,0,0,0,0],True)
            with constants.Control.imageLock:
                constants.Control.pcImageList.append([exitCode,0,0,0, SCAN_ID])
            if self.cancel():#catch a cancel after last shot captured.
                constants.Control.mProjScreen.showImageFromFile(constants.Scanning.IDLE_IMAGE)
                constants.Control.mMotors.powerOn(False, False)

        print('finished scan, total time',time.perf_counter()-tick)

        return


    def scanShutDown(self, cancelled=False):
        #mProjScreen.delImages()
        #print('Proj Image kunld')
        constants.Control.mProjScreen.showImageFromFile(constants.Scanning.PROCESSING_IMAGE)
        #mProjScreen.closeProjWindow()#TODO FOR DEBUG ONLY
        constants.Control.mMotors.moveToTwoAngles(VERTICAL_LEVEL, 0, shortestRouteH=True)
        constants.Control.mCapture.stopVideo()
        constants.Control.mCapture.closeCamera()
        if constants.Scanning.SOUND!=0 and not cancelled:
            playSound.file(soundCode=constants.Sounds.PROCESSING)


    def cancel(self):
        if len(constants.Control.cancelList)>0:
            print('CANCEL')
            return True
        else:
            return False
    
    
if __name__ == "__main__":
    print("cv2 version", cv2.__version__)
    mScanMaster=ScanMaster()
    #mScanMaster.speedTest()
    #playSound.file(soundCode=constants.Sounds.START_PING)


    
