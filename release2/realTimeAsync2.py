import numpy as np
import time
import captureVideo
import constants
import os
from threading import Event
import projControl
import math
import gc
import traceback


class RealTimeProcessing():
            
    def __init__(self, syncMaster=True, camera_id=0):
        """
        :param syncMaster: True if this RealTimeProcessing drives the projector
                           (always True for camera 0; False for camera 1).
        :param camera_id: 0 = left camera (mCapture), 1 = right camera (mCaptureRight).
        """
        self.camera_id = camera_id
        self.getFrame=-1#-1 is dummy, 3 means get frame 3 and put in imageSet[3] etc.
        self.captureDoneEvent = Event()
        self.captureDoneEvent.set()#done, so can sync
        self.syncingCameras=False
        self.lastCaptureTime=0
        self.syncMaster=syncMaster
        self.mProjControl=projControl.projControl()
        self.frameCounter=0
        self.idealCaptureTime1=0
        self.idealCaptureTime2=0
        self.idealCaptureTimeEnd=0
        self.frameTimes=[]
        self.catch=0
        self.drop=0
        self.ratio=0
        constants.Protocol.CLOCK_OFFSET_BUFFER=[]#reset clock sync buffer.
        self.updateFrameTime()
        self.i=0
        self.numberOfImages=0
        self.colourImage=None
        self.jpgNotComplete=-1
        self.projStarted=False

    def _get_capture(self):
        """Return the capture object that feeds this RealTimeProcessing instance."""
        if self.camera_id == 1:
            return constants.Control.mCaptureRight
        return constants.Control.mCapture

    def updateFrameTime(self, framerate=None):#called from mCapture if frame rate changes
        if framerate is None:
            cap = self._get_capture()
            if cap is None:
                return
            framerate = cap.camera.framerate
        self.frameTime=1000000*1.0/framerate

    def generateCaptureTimes(self, numberOfImages):
        #proj screen freq : 60.61Hz, 60Hz, 50Hz, 59.94Hz - 60.61Hz USED, now on 59.86 - cvt mode
        self.updateFrameTime()
        cap = self._get_capture()
        currentTime=cap.camera.timestamp
        lastCaptureTimeEstimated=self.lastCaptureTime+self.frameTime*math.ceil((currentTime-self.lastCaptureTime)/self.frameTime)
        imageTimeRounded = self.frameTime * (math.ceil(constants.Scanning.IMAGE_SYNC_ERROR_MARGIN / self.frameTime)+2)
        endTime=constants.Scanning.CAPTURE_START_DELAY_TARGET+constants.Scanning.LATENCY+imageTimeRounded
        endTimeRounded=lastCaptureTimeEstimated+self.frameTime*math.ceil(endTime/self.frameTime)

        captureTimeList=[]
        projTimeList=[]
        for n in range(numberOfImages):
            captureTimeMin=endTimeRounded+n*imageTimeRounded-self.frameTime/2
            captureTimeMax=captureTimeMin+self.frameTime
            #projTimeList.append(captureTimeMin-imageTimeRounded*0.5-projLagTime)
            projTimeList.append(captureTimeMax-imageTimeRounded-self.frameTime/2-constants.Scanning.LATENCY)
            captureTimeList.append((captureTimeMin, captureTimeMax))
        #print('camera frameTime, exp, nFramesPerImage:', self.frameTime/1000, constants.Control.mCapture.camera.shutter_speed/1000, math.ceil(imageTimeTarget/self.frameTime))
        #print('lastCaptureTimeEstimated', lastCaptureTimeEstimated, currentTime, currentTime-lastCaptureTimeEstimated)
        #for i in range(len(captureTimeList)):
        #    print(int(projTimeList[i]-lastCaptureTimeEstimated)/1000, int(captureTimeList[i][0]-lastCaptureTimeEstimated)/1000, int(captureTimeList[i][1]-lastCaptureTimeEstimated)/1000)
        #waitTime=projTimeList[0]-constants.Control.mCapture.camera.timestamp
        #print('generateCaptureTimes, proj wait time:', waitTime)
        #print('imageTimeRounded',imageTimeRounded/1000)
        return captureTimeList, projTimeList

    def generateCaptureTimesLAGTEST(self, numberOfImages):
        #proj screen freq : 60.61Hz, 60Hz, 50Hz, 59.94Hz - 60.61Hz USED, now on 59.86 - cvt mode
        self.updateFrameTime()
        cap = self._get_capture()
        currentTime=cap.camera.timestamp
        lastCaptureTimeEstimated=self.lastCaptureTime+self.frameTime*math.ceil((currentTime-self.lastCaptureTime)/self.frameTime)
        #imageTimeRounded = self.frameTime * (math.ceil(constants.Scanning.IMAGE_SYNC_ERROR_MARGIN / self.frameTime)+2)
        imageTimeRounded=self.frameTime
        endTime=constants.Scanning.CAPTURE_START_DELAY_TARGET+imageTimeRounded
        endTimeRounded=lastCaptureTimeEstimated+self.frameTime*math.ceil(endTime/self.frameTime)

        captureTimeList=[]
        for n in range(numberOfImages):
            captureTimeMin=endTimeRounded+n*imageTimeRounded-self.frameTime/2
            captureTimeMax=captureTimeMin+self.frameTime
            #projTimeList.append(captureTimeMin-imageTimeRounded*0.5-projLagTime)
            captureTimeList.append((captureTimeMin, captureTimeMax))
        
        projTimeList=[]
        projTimeList.append(endTimeRounded-self.frameTime)
        #print('camera frameTime, exp, nFramesPerImage:', self.frameTime/1000, constants.Control.mCapture.camera.shutter_speed/1000, math.ceil(imageTimeTarget/self.frameTime))
        #print('lastCaptureTimeEstimated', lastCaptureTimeEstimated, currentTime, currentTime-lastCaptureTimeEstimated)
        #for i in range(len(captureTimeList)):
        #    print(i,int(projTimeList[0]-lastCaptureTimeEstimated)/1000, int(captureTimeList[i][0]-lastCaptureTimeEstimated)/1000, int(captureTimeList[i][1]-lastCaptureTimeEstimated)/1000)
        #waitTime=projTimeList[0]-constants.Control.mCapture.camera.timestamp
        #print('generateCaptureTimes, proj wait time:', waitTime)
        #print('imageTimeRounded',imageTimeRounded/1000, 'endTimeRounded', (endTimeRounded-lastCaptureTimeEstimated)/1000)
        return captureTimeList, projTimeList
    
    def captureRequest(self, captureTimeList, scanImageList, projTimeList=None, retry=False, preImage=True):#projTimeList, and scanImageList are for pi1 only.
        self.numberOfImages=len(captureTimeList)
        self.captureTimeList=captureTimeList
        self.scanImageList=scanImageList
        if not retry:#if retry don't clear image lists, just add on to them.
            self.frameTimes=[]#debug
            self.imageSet=[]
            self.capturedList=[]
        self.i=0
        self.jpgNotComplete=-1
        self.projStarted=False
        if projTimeList is not None:
            self.mProjControl.requestSequenceOnThread(scanImageList, projTimeList, preImage=preImage)#TODO retry if an image not shown in time (or does this never happen)?
            self.projStarted=True
        self.captureDoneEvent.clear()#capturing - set after idealCapture times set

    #TODO
        #- some frames skipping
        #could slow frame rate - 90fps drops 30-40% pairs, 75fps drops 10-20% pairs, 60fps drops ~0%
        #use CLI not windows gives 90fps at only 10% drop.
        #or return only what images captured (metadata), then PC requests only images that were useful - so can have faster retry rate.
        #could capture 1x proj, 2x white, 1x proj :then I have double chance to get sequential pair.
        #could use jpg - less data maybe faster - but less quality!
        #mjpeg seems not to drop frames, but not tested visually.
        #less nice did not help.
        

    def write(self, s):
        try:
            cap = self._get_capture()
            captureTime=cap.camera.frame.timestamp        #system time clock - used by gpu and camera.
            
            if self.jpgNotComplete >-1 and not self.captureDoneEvent.is_set():#and if not done:
                if len(self.imageSet)>self.jpgNotComplete:
                    self.imageSet[self.jpgNotComplete]+=s
                if s.endswith(b'\xff\xd9'):
                    self.jpgNotComplete=-1
                else:
                    pass
                    #print('jpg still not complete!')
                return len(s)
            
            if captureTime is None:#seems to happen when s a continuation of a frame.
                return len(s)
            
            #print(self.frameCounter, captureTime-self.lastCaptureTime)
            self.lastCaptureTime=captureTime
            self.frameCounter+=1
            #print(self.lastCaptureTime)

            while self.i<self.numberOfImages and not self.captureDoneEvent.is_set():
                if captureTime<self.captureTimeList[self.i][0]:
                    break
                if captureTime>self.captureTimeList[self.i][1]:
                    self.i+=1
                #get frames
                if captureTime>=self.captureTimeList[self.i][0] and captureTime<self.captureTimeList[self.i][1]:
                    self.imageSet.append(s)
                    self.capturedList.append(self.scanImageList[self.i])
                    self.frameTimes.append(captureTime)
                    #print('2',self.frameCounter, self.i, len(self.imageSet))
                    if s.endswith(b'\xff\xd9'):
                        self.jpgNotComplete=-1
                    else:
                        self.jpgNotComplete=self.i
                    self.i+=1
                    return len(s)#say we read entire image - seems to mean we always get one whole frame at a time...usually true but not always!
                
            if not self.captureDoneEvent.is_set():#if not done
                if captureTime>self.captureTimeList[self.numberOfImages-1][1] and self.jpgNotComplete==-1:# timeout.
                    #print('timeout')
                    self.captureDoneEvent.set()#done

            #SYNC
            if self.syncingCameras and self.captureDoneEvent.is_set() is True:#sync only when not capturing to avoid frame skips
                if self.syncMaster:
                    cap.mSyncerMaster.syncCameras(cap.camera.timestamp, captureTime)
                else:
                    cap.mSyncerSlave.syncCameras(captureTime)
                    
        except Exception as e:
            print('Error realTimeAsync2: ',e)
            traceback.print_exc()
        
        return len(s)
    
        
    def waitForFirstFrame(self):
        while self.frameCounter<1:#wait for first frame to come in so camera.frame.timestamp is meaningful
            time.sleep(0.005)

    def flush(self):
        print('flush')
            
    def waitForFrameCapture(self):
        self.captureDoneEvent.wait()
        if self.projStarted:#assuming sync master has the projControl
            self.mProjControl.projDoneEvent.wait()
        #for i in self.mProjControl.projErrorList:
        #    print('projErrorList: ', i)

        #for i in self.frameTimes:
        #    print('captureTime-ideal1',i)
        #for i in self.capturedList:
        #    print('capturedList', i)

        missingImageList=self.find_missing(self.capturedList, self.scanImageList)
        self.drop=len(missingImageList)
        self.catch=len(self.capturedList)
        if self.catch!=0:
            self.ratio=self.drop/self.catch
        else:
            self.ratio=0
        success=False
        if (len(missingImageList)+len(self.mProjControl.projErrorList))==0:
            success=True
        print('drop, catch, ratio, missing, projError:', self.drop, self.catch, self.ratio, missingImageList, self.mProjControl.projErrorList)
        return success, missingImageList, self.mProjControl.projErrorList
    
    def find_missing(self, lst, refList):
        missingImageList=[]
        for x in refList:
            if x not in lst:
                missingImageList.append(x)
        return missingImageList
    
    def reorderLists(self, scanImageList):
        #print('self.capturedList',self.capturedList)
        #print('scanImageList',scanImageList)
        orderedCaptureList=[]
        orderedImageSet=[]
        for i in range(len(scanImageList)):
            scanImage=scanImageList[i]
            captureListIndexOfscanImage=self.capturedList.index(scanImage)
            orderedCaptureList.append(self.capturedList[captureListIndexOfscanImage])
            orderedImageSet.append(self.imageSet[captureListIndexOfscanImage])
        self.capturedList=orderedCaptureList
        self.imageSet=orderedImageSet
        #test
        print('orderedCaptureList', orderedCaptureList)
        #print('self.imageSet len', len(self.imageSet))
        
    def removeProjErrorsFromImageSet(self, projErrorList):#input list or empty list
        if projErrorList==[] or projErrorList is None:
            return
        
        for projError in projErrorList:
            try:
                captureListIndexOfProjError=self.capturedList.index(projError)
            except Exception as e:
                continue # projError image was not captured so skip to next.
            self.capturedList.pop(captureListIndexOfProjError)
            self.imageSet.pop(captureListIndexOfProjError)
            
        return
    
    def clearMemory(self):#did nothing to help time critical capture so NOT USED
        self.frameTimes=[]#debug
        self.imageSet=[]
        self.capturedList=[]
        tick=time.perf_counter()
        x=gc.collect()
        print('garbage colection:', time.perf_counter()-tick,'sec ', x)
        

def testCamera():
    mCapture=captureVideo.capture(preview=False, resolution=(constants.Scanning.CAPTURE_W,constants.Scanning.CAPTURE_H))
    msec=20
    mCapture.setExposure(msec)
    mRealTime=RealTimeProcessing(mCapture)
    mCapture.startVideoAndProcessing(mRealTime)
    mCapture.wait(5)
    mCapture.stopVideo()
    #sleep(60)
    mCapture.closeCamera()
    #mRealTime.flush()

if __name__ == "__main__":
    testCamera()
    
