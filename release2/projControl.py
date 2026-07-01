import time
import threading
import constants
import os
from threading import Event
from multiprocessing import Process#, Event
import gc


class projControl():
            
    def __init__(self):
        self.projErrorList = []
        self.projDoneEvent = Event()
        self.projDoneEvent.clear()#clear = started, set when done
        
    def requestSequenceOnThread(self, scanImageList, frameTimeList, useProcess=False, preImage=True):
        #should be process to be on another core? - No because projScreen ([ygame and also sdl2) doesn't work if I do. - maybe put camera on different process?
        #can do fb on process?

        useProcess=False#from Intra1 I found that running on process causes led to miss frame frequently with no error reported, so not using it.

        clockOffset=time.perf_counter()*1000000-constants.Control.mCapture.camera.timestamp
            
        self.projDoneEvent.clear()
        if useProcess:
            p = Process(target=self.requestSequence, args=(scanImageList, frameTimeList, preImage, clockOffset))
            p.daemon=True  # if true it will stop automatically if your program exits.
            p.start()
        else:
            t = threading.Thread(target=self.requestSequence, args=(scanImageList, frameTimeList, preImage, clockOffset))
            t.daemon = True
            t.start()

        #debug
        waitTime=frameTimeList[0]-constants.Control.mCapture.camera.timestamp
        #print('Thread started, wait time:', waitTime)
        #debug end

    def requestSequence(self, scanImageList, frameTimeList, preImage, clockOffset):#usec
        try:
            niceness=os.nice(-20)
        except Exception as e:
            print('Error could not set niceness (need sudo)', e)
        #print('projControl niceness', niceness)
        waitTimesList=[]
        i=0
        
        if preImage:
            constants.Control.mProjScreen.bufferImageFromArray(scanImageList[i])#see if showing first image will make future images smoother
            constants.Control.mProjScreen.showBuffer()
            #print('Proj Control showed preImage')
            #gc.collect()
        while i<len(frameTimeList):
            tick=time.perf_counter()
            if i<len(scanImageList):
                constants.Control.mProjScreen.bufferImageFromArray(scanImageList[i])
            bufferTime=time.perf_counter()-tick
            #waitTime=frameTimeList[i]-constants.Control.mCapture.camera.timestamp
            waitTime=frameTimeList[i]-time.perf_counter()*1000000+clockOffset
            if waitTime>0:
                #time.sleep(waitTime/1000000)
                busy_wait(waitTime/1000000)
            tick=time.perf_counter()
            constants.Control.mProjScreen.showBuffer()
            showBufferTime=time.perf_counter()-tick
            waitTimesList.append((i, waitTime/1000, (showBufferTime)*1000, bufferTime*1000))
            i+=1
        
        self.projErrorList = []
        for w in waitTimesList:
            #print('wait times: ', w)
            if w[1]<0:
                #print('ERROR: projControl missed frame :', w[0],':', scanImageList[w[0]])
                self.projErrorList.append(scanImageList[w[0]])
        self.projDoneEvent.set()
        
        
def busy_wait(dt):#in seconds
    #loop more accurate than time.sleep #https://stackoverflow.com/questions/17499837/python-time-sleep-vs-busy-wait-accuracy
    #loop takes 95%  cpu usage  - time.sleep takes ~0%, high cpu usage could be causing network issues.
    #could put loop wait on another process, but not sure bout spin up time.
    #trying sleep.
    tick=time.perf_counter()
    #time.sleep(dt)#can be upto 30ms off, when on same thread as camera, up to 6msec off when on separate process.
    end_time = time.time() + dt
    while (time.time() < end_time):#some error when on same thread as camera, less than 2msec error when on separate process.
        pass
    error=time.perf_counter()-tick-dt
    #print('timing error: ',error*1000)
    return
        
        
if __name__ == "__main__":
    import projScreenFB as projScreen
    import captureVideo
    #import projScreen
    constants.Control.mCapture=captureVideo.capture(preview=False)    
    constants.Control.mProjScreen=projScreen.projScreen()
    constants.Control.mProjScreen.loadImagesAndResize()
    constants.Control.mProjScreen.showImageFromFile('magen')
    mProjControl=projControl()
    scanImageList = [12,13,14,15,16,17,18,19,20,21,22,23,0,1,2,3,4,5,6,7,8,9,10,11,24]#
    #test

    for test in range(10):
        frameTimeList=[]
        timeNow=constants.Control.mCapture.camera.timestamp
        for x in range(25):
            frameTimeList.append(timeNow+x*100000)
        mProjControl.requestSequenceOnThread(scanImageList, frameTimeList)
        time.sleep(3)
    constants.Control.mCapture=captureVideo.closeCamera()  
    
