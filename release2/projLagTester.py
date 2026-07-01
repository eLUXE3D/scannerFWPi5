import time
import os
import cv2
import numpy as np

import realTimeAsync2
import captureVideo
import constants
if constants.DEBUG.PROJ_SCREEN_DEBUG_MODE:
    import projScreen  # pygame based - works in gui
    import matplotlib.pyplot as plt #DEBUG only
else:
    import projScreenFB as projScreen  # direct screen access from CLI - much faster.
import gc

class projLagTester():
            
    def __init__(self):
        if constants.Control.mCapture is not None:
            self.origSensorMode=constants.Control.mCapture.camera.sensor_mode
            self.origExposure=constants.Control.mCapture.camera.exposure_speed
            self.origResolution=constants.Control.mCapture.camera.resolution
            self.origFrameRate=constants.Control.mCapture.camera.framerate
            self.origMaxFrameRate=constants.Scanning.MAX_FRAME_RATE
            # SETTINGS
            self.origCAPTURE_START_DELAY_TARGET =constants.Scanning.CAPTURE_START_DELAY_TARGET

    def setupForMeasurement(self):
        constants.Control.mCapture.camera.sensor_mode=7
        constants.Control.mCapture.setResolution((160,120))
        constants.Scanning.MAX_FRAME_RATE=90
        constants.Control.mCapture.setExposureAndMaxFrameRate(10.0)
        #print('projLagTester saved camera params', self.origSensorMode, self.origExposure, self.origResolution, self.origMaxFrameRate)

        constants.Control.mCapture.stopVideo()
        constants.Control.mRealTime = realTimeAsync2.RealTimeProcessing(syncMaster=True)
        constants.Control.mCapture.startVideoAndProcessing(mode='mjpeg')  # bitrate=2000000
        constants.Scanning.CAPTURE_START_DELAY_TARGET = 50000

    def setBackCameraSettings(self):
        constants.Scanning.CAPTURE_START_DELAY_TARGET = self.origCAPTURE_START_DELAY_TARGET
        constants.Scanning.MAX_FRAME_RATE=self.origMaxFrameRate
        
        constants.Control.mCapture.stopVideo()
        constants.Control.mCapture.camera.sensor_mode=self.origSensorMode
        constants.Control.mCapture.setResolution(self.origResolution)
        constants.Control.mCapture.camera.framerate=self.origFrameRate
        constants.Control.mCapture.camera.shutter_speed=self.origExposure
        
    def saveDebugImages(self, mRealTime, angleData=None):
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

    def measureProjLag(self, repeat=5):
        #SETUP
        self.setupForMeasurement()
        scanImageList = [26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26]#25black, 26 white
        #START


        #DO MEASUREMENTS
        # MEASURE
        changeList = []
        plotList = []
        changeReadyList = []
        plotReadyList = []
        changePlotList=[]
        for i in range(repeat):
            projChangeIndex, timeLine , projReadyIndex, timeLineReady, changePlot= self.singleMeasurement(scanImageList)
            if projChangeIndex is not None:
                changeList.append(projChangeIndex)
                plotList.append(timeLine)
                changeReadyList.append(projReadyIndex)
                plotReadyList.append(timeLineReady)
                changePlotList.append(changePlot)

        # PLOT
        print('changeList', changeList)
        frameTime=1000*1.0/constants.Control.mCapture.camera.framerate
        minLag=min(changeList)*frameTime/5#5 lines per image
        maxLag=max(changeList)*frameTime/5
        #print('Latency Min, Max:', min(changeList), max(changeList))
        #print('Latency minLag, maxLag (msec):', minLag, maxLag)
        #for x in plotList:
        #    plt.plot(x)
        #plt.xlabel('pixels')
        #plt.show()
        
        print('changeReadyList', changeReadyList)
        frameTime=1000*1.0/constants.Control.mCapture.camera.framerate
        minLagReady=min(changeReadyList)*frameTime/5#5 lines per image
        maxLagReady=max(changeReadyList)*frameTime/5
        #print('Ready Min, Max:', min(changeReadyList), max(changeReadyList))
        #print('Ready minLag, maxLag (msec):', minLagReady, maxLagReady)
        #for x in plotReadyList:
        #    plt.plot(x)
        #plt.xlabel('pixels')
        #plt.show()
        
        #change plot
        print('Latency Min, Ready Max:', minLag, maxLagReady)
        #for x in changePlotList:
        #    plt.plot(x)
        #plt.xlabel('pixels')
        #plt.show()

        #WRITE TO LOG FILE
        # Open a file with access mode 'a'
        file_object = open('projTestResults.txt', 'a')
        # Append 'hello' at the end of file
        file_object.write('Latency Min, Ready Max:' + str(minLag) +' '+ str(maxLagReady) + '\n')
        file_object.close()

        #FINISH
        self.setBackCameraSettings()

        return minLag, maxLag



    def singleMeasurement(self, scanImageList):
        constants.Control.mRealTime.frameCounter=0
        constants.Control.mRealTime.waitForFirstFrame()
        constants.Control.mRealTime.syncingCameras=False
        constants.Control.mProjScreen.showImageFromFile('s0025')
        time.sleep(0.3)
        #gc.collect()
        captureTimeList, projTimeList = constants.Control.mRealTime.generateCaptureTimesLAGTEST(numberOfImages=len(scanImageList))
        constants.Control.mRealTime.captureRequest(captureTimeList, projTimeList=projTimeList, scanImageList=scanImageList, preImage=False)
        success, missingImageList, projErrorList = constants.Control.mRealTime.waitForFrameCapture()
        # print('Success - no image drops or proj drops: ', success)
        # redefine success - ok if proj does not show second white image
        if missingImageList == [] and not 26 in projErrorList:
            success = True
        else:
            return None, None, None, None
        # projSequence.saveDebugImages(constants.Control.mRealTime, 0)
        #print('i, projTime, frameTime, captureTime min to max')
        #for i in range(len(captureTimeList)):
        #    print(i, (projTimeList[i]-captureTimeList[0][0])/1000, (constants.Control.mRealTime.frameTimes[i]-captureTimeList[0][0])/1000, (captureTimeList[i][0]-captureTimeList[0][0])/1000,'to',(captureTimeList[i][1]-captureTimeList[0][0])/1000)
        # time.sleep(2)

        # PROCESS IMAGES
        # images to numpy array resized to 1 col, then h stacked into time plot
        jpg = np.frombuffer(constants.Control.mRealTime.imageSet[0], dtype=np.dtype('B'))
        bgImage = cv2.imdecode(jpg, cv2.IMREAD_GRAYSCALE).astype(np.float32)
        lastImageIndex=len(constants.Control.mRealTime.imageSet)-1
        jpg = np.frombuffer(constants.Control.mRealTime.imageSet[lastImageIndex], dtype=np.dtype('B'))
        endImage = cv2.imdecode(jpg, cv2.IMREAD_GRAYSCALE).astype(np.float32)
        # show(bgImage/np.max(bgImage))
        timeLine = None
        timeLineReady=None
        for i, image in enumerate(constants.Control.mRealTime.imageSet):
            jpg = np.frombuffer(constants.Control.mRealTime.imageSet[i], dtype=np.dtype('B'))
            image = cv2.imdecode(jpg, cv2.IMREAD_GRAYSCALE).astype(np.float32)
            #show(image/np.max(image))
            #print('imagemax',np.max(image))
            imageLatency= image-bgImage
            imageLatency = cv2.resize(imageLatency, (1, 5), interpolation=cv2.INTER_AREA).T
            imageReady= endImage-image
            imageReady = cv2.resize(imageReady, (1, 5), interpolation=cv2.INTER_AREA).T
            if timeLine is None:
                timeLine = imageLatency
            else:
                timeLine = np.hstack((timeLine, imageLatency))
            if timeLineReady is None:
                timeLineReady = imageReady
            else:
                timeLineReady = np.hstack((timeLineReady, imageReady))
        timeLine = np.squeeze(timeLine)
        timeLine = timeLine / np.max(timeLine)
        timeLineReady = np.squeeze(timeLineReady)
        timeLineReady = timeLineReady / np.max(timeLineReady)
        # find stdev of first frame
        threshold = 10 * (np.std(timeLine[5:10]) + 1 / 255)
        projChangeIndex = 0
        for i in range(timeLine.shape[0]):
            if timeLine[i] > threshold:
                projChangeIndex = i
                break
            
        threshold = 10 * (np.std(timeLineReady[-10:-5]) + 1 / 255)
        print('threshold', threshold)
        projReadyIndex = 0
        for i in range(timeLineReady.shape[0]-1,0,-1):
            if timeLineReady[i] > threshold:
                projReadyIndex = i
                break

        #print('projChangeIndex, threshold', projChangeIndex, threshold)
        #plot(timeLine)
        changePlot=np.minimum(timeLine,timeLineReady)

        return projChangeIndex, timeLine, projReadyIndex, timeLineReady, changePlot

def plot(x):
    plt.plot(x) 
    plt.xlabel('pixels') 
    plt.show()
        
def show(image):
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return None

if __name__ == "__main__":
    #UNIT TEST
    #setup
    constants.Scanning.RESOLUTION=(160,120)
    constants.Scanning.CAMERA_MODE=7
    constants.Scanning.EXPOSURE_TIME_SCAN=10
    constants.Control.mCapture=captureVideo.capture(preview=False)
    constants.Control.mProjScreen=projScreen.projScreen()
    constants.Control.mProjScreen.loadImagesAndResize()

    mLagTester=projLagTester()
    minLag, maxLag=mLagTester.measureProjLag(repeat=20)

            
    #FINISH
    constants.Control.mProjScreen.closeProjWindow()    
    constants.Control.mCapture.closeCamera()



    

    

    
    
        

