import constants
import time
import threading
import os
import cv2
import numpy as np
import lanClientPi
import lanHelpers

def projSeqAsync(scanImageList):#USED
    success, missingImageList, projErrorList=projSeqAsyncOneTry(scanImageList, retry=False)
    count=0
    while not success:
        success, missingImageList, projErrorList=projSeqAsyncOneTry(missingImageList, retry=True, imageOrder=scanImageList, projErrorList=projErrorList)
        if success:
            constants.Control.mRealTime.reorderLists(scanImageList)
        count+=1
        if count>3:
            break

    return
        
def projSeqAsyncOneTry(scanImageList, retry=False, imageOrder=None, projErrorList=None):
    #SET UP PI1 CAPTURE
    tick=time.perf_counter()
    captureTimeList, projTimeList=constants.Control.mRealTime.generateCaptureTimes(numberOfImages=len(scanImageList))
    constants.Control.mRealTime.captureRequest(captureTimeList, scanImageList=scanImageList, projTimeList=projTimeList, retry=retry)
    #print('setup time', time.perf_counter()-tick)
    #SET UP PI2 CAPTURE
    mLanClientPi = lanClientPi.lanClientPi()
    cmdID_capture = mLanClientPi.setPi2mode(PI2_MODE='captureScanImagesFast', CAPTURE_TIME_LIST=captureTimeList, SCAN_IMAGE_LIST=scanImageList, RETRY=retry, IMAGE_ORDER=imageOrder, PROJ_ERROR_LIST=projErrorList)
    #WAIT FOR PI1 CAPTURE TO FINISH
    successPi1, missingImageListPi1, projErrorListPi1=constants.Control.mRealTime.waitForFrameCapture()
    #TODO remove projError Images from mRealTime Pi1
    constants.Control.mRealTime.removeProjErrorsFromImageSet(projErrorListPi1)
    #WAIT FOR PI2
    done, msg=lanHelpers.checkIfDone(cmdID_capture)
    successPi2=msg['SUCCESS_PI2']
    missingImageListPi2=msg['MISSING_IMAGE_LIST_PI2']
    if successPi1 and successPi2:
        return True, None, None
    #COMBINE MISSING IMAGES TO ONE LIST
    success=False
    mergedMissingImageList = list(set(missingImageListPi1+missingImageListPi2+projErrorListPi1))
    print('mergedMissingImageList', mergedMissingImageList)
    return success, mergedMissingImageList, projErrorListPi1

def projSeqBuffered(): #USED in slow mode
    #buffer seems to copy to gpu memory but this takes 30ms and then flip buffer takes 30ms
    #so takes 2x processor time, and does not reduce latency significantly if not at all.
    #could try to bypass pygame which may do a one frame lag.
    #sequential show image and capture, robust, pretty fast.

    projLag=constants.Scanning.PROJ_LAG_TIME
    scanImageList=constants.Scanning.SCAN_IMAGE_LIST

    constants.Control.mRealTime.debugFrameSkipList=[]
    exposure=constants.Control.mCapture.camera.shutter_speed/1000#exposure in msec
    frameTime=1000*1.0/constants.Control.mCapture.camera.framerate#frame time in msec
    tick=constants.Control.mCapture.camera.timestamp
    i=0
    constants.Control.mProjScreen.bufferImageFromArray(scanImageList[i])
    while i<len(scanImageList):
        constants.Control.mProjScreen.showBuffer()
        displayTime=constants.Control.mCapture.camera.timestamp
        idealCaptureTimeMinPi1=displayTime+projLag+frameTime*1000
        idealCaptureTimeMax=displayTime+projLag+frameTime*1000+10000000#+10 sec in case processing over runs
        mLanClientPi = lanClientPi.lanClientPi()
        cmdID_capture = mLanClientPi.setPi2mode(PI2_MODE='captureScanImage', IMAGE_NUMBER=i, idealCaptureTimeMinPi1=idealCaptureTimeMinPi1)

        if scanImageList[i]==constants.Scanning.WHITE_MATCHING_PEAK_STRIP_INTENSITY:#white image for colour grab
            #colourImage=mCapture.captureColourImage()#gets rgb direct, yuv to rbg in numpy was very slow 4 sec.
            #mRealTime.getFrame=-2#gives yuv
            constants.Control.mCapture.wait(float(projLag+2*frameTime*1000)/1000000)#TODO tune: wait projLag + 2 frame times
            if exposure<10.0:#if we need to stack colour image to avoid projector colour banding
                constants.Control.mRealTime.colourImage=constants.Control.mCapture.captureColourImageStack()
            else:
                constants.Control.mRealTime.colourImage=constants.Control.mCapture.captureColourImage()#can this capture retrospectively? yes so need to wait more than projLag
        else:
            constants.Control.mRealTime.captureRequest(i, idealCaptureTimeMinPi1, idealCaptureTimeMax)
        
        i+=1
        if i<len(scanImageList):
            constants.Control.mProjScreen.bufferImageFromArray(scanImageList[i])
            
        #wait for Pi 2 to be done
        constants.Control.mRealTime.waitForFrameCapture()
        lanHelpers.checkIfDone(cmdID_capture)

    print('Proj seq', float(constants.Control.mCapture.camera.timestamp-tick)/1000000)   
    return

def saveDebugImages(mRealTime, angleData=None):
    SCANS_PATH = 'scanData/'
    
    angleDir=angleData
    scanDir=0
    angleDirString='{:03d}'.format(angleDir)
    scanDirString='{:03d}'.format(scanDir)
    path=SCANS_PATH+"/"+scanDirString+"/"+angleDirString
    if not os.path.exists(path):
        os.makedirs(path)
    for i, image in enumerate(mRealTime.imageSet):
        jpg = np.frombuffer(mRealTime.imageSet[i], dtype=np.dtype('B'))
        image = cv2.imdecode(jpg, cv2.IMREAD_COLOR)
        cv2.imwrite(path+'/'+str(i).zfill(5)+'.png', image)
    #if angleData is not None:
    #    np.savetxt(path +'/angleData.txt',angleData)


    
if __name__ == "__main__":
    measureProjLag()
