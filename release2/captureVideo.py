import time
from picamera import PiCamera
import cv2
import numpy as np
import constants
import io
import playSound
import cameraSyncerMaster
import cameraSyncerSlave
import os

class capture():
    camera = None

    def __init__(self, preview=False):
        self.currentBitRate=0
        self.openCamera(preview)
        
        # SET UP SYNCING
        self.mSyncerMaster = cameraSyncerMaster.cameraSyncerMaster(self.camera)
        self.mSyncerSlave = cameraSyncerSlave.cameraSyncerSlave(self.camera)

        
    def openCamera(self, preview=False):
        if self.isOpen():
            print('Camera already open')
            return
        
        # CAMERA SET_UP
        self.camera = PiCamera(resolution=constants.Scanning.RESOLUTION, sensor_mode=constants.Scanning.CAMERA_MODE)  # FHD => frame rate 1/10 fps to 30fps

        self.camera.iso = constants.Scanning.ISO
        self.setExposure(constants.Scanning.EXPOSURE_TIME_SCAN)
        # self.camera.meter_mode = 'spot'
        self.camera.exposure_mode = 'off'  # no more auto exposure
        # g = self.camera.awb_gains
        self.camera.awb_mode = 'off'
        self.camera.awb_gains = (1.9, 1.2)  # set for C6 proj on paper with R and B a little lower than Green to ensure the camera isn't brighter than it needs to be.
        self.camera.clock_mode = 'raw'
        self.camera.image_denoise = False

        self.updateCameraSettings()

        if preview:
            self.camera.start_preview()
            print('start preview')
        
    def closeCamera(self):
        try:
            self.camera.stop_preview()
        except Exception as e:
            print("Warning: camera close preview error", e)
        try:
            self.camera.close()
            print("camera closed")
        except Exception as e:
            print("Warning: camera close error", e)

    def isOpen(self):
        try:
            closed=self.camera.closed
        except Exception as e:
            #print('captureVideo isOpen error: ',e)
            return False
        return not closed

    def printSettings(self):
        print('SENSOR_MODE : ', self.camera.sensor_mode)
        print('EXPOSURE    : ', self.camera.shutter_speed, self.camera.exposure_speed )#/ 1000, ' msec')
        print('ISO         : ', self.camera.iso)
        print('ANALOG GAIN : ', self.camera.analog_gain)
        print('DIGITAL GAIN: ', self.camera.digital_gain)
        print('AWB         : ', self.camera.awb_mode, self.camera.awb_gains)
        print('FRAME RATE  : ', float(self.camera.framerate))
        print('RESOLUTION  : ', self.camera.resolution)
        print('RESIZE      : ', constants.Scanning.RESIZE)

    def updateCameraSettings(self):
        # Note: 64MB GPU memory not enough for FHD, 128MB ok.
        if not self.isOpen():
            print('camera closed - settings not changed')  # but settings will be changed when camera is opened.
            return

        # self.camera.exposure_mode = 'off'
        restartRecording = False

        if self.currentBitRate!=constants.Scanning.BIT_RATE:
            restartRecording=True
        
        if self.camera.sensor_mode != constants.Scanning.CAMERA_MODE:
            if self.camera.recording:
                self.camera.stop_recording()
                restartRecording = True
                self.camera.sensor_mode = constants.Scanning.CAMERA_MODE
                self.camera.sensor_mode = constants.Scanning.CAMERA_MODE  # docs say set it twice
            else:
                self.camera.sensor_mode = constants.Scanning.CAMERA_MODE
                self.camera.sensor_mode = constants.Scanning.CAMERA_MODE  # docs say set it twice
                
        if self.camera.resolution != constants.Scanning.RESOLUTION:
            if self.camera.recording:
                self.camera.stop_recording()
                restartRecording = True
                self.setResolution(constants.Scanning.RESOLUTION)  # require camera open but no recording
            else:
                self.setResolution(constants.Scanning.RESOLUTION)  # require camera open but no recording

        if self.camera.framerate != constants.Scanning.FRAME_RATE:
            if self.camera.recording:
                self.camera.stop_recording()
                restartRecording = True
                self.setFrameRate(constants.Scanning.FRAME_RATE)  # require camera open but no recording
            else:
                self.setFrameRate(constants.Scanning.FRAME_RATE)  # require camera open but no recording

        if restartRecording:
            self.startVideoAndProcessing()
        # self.camera.exposure_mode = 'off'

        # SETUP CAMERA ALIGNMENT
        if os.uname()[1] == constants.Info.MASTER_UNAME:
            zoom = constants.Scanning.ZOOM_L
        else:
            zoom = constants.Scanning.ZOOM_R

        self.camera.zoom = zoom

        # SET EXPOSURE
        if self.camera.iso != constants.Scanning.ISO:
            if constants.Scanning.ISO < 100:
                self.camera.iso = constants.Scanning.ISO  # untested atttempt
                time.sleep(0.25)
                self.camera.exposure_mode = 'off'  # no more auto exposure
            else:
                self.camera.exposure_mode = 'fixedfps'  # no more auto exposure
                time.sleep(0.25)
                self.camera.iso = constants.Scanning.ISO

        if self.camera.shutter_speed != constants.Scanning.EXPOSURE_TIME_SCAN:
            self.setExposure(constants.Scanning.EXPOSURE_TIME_SCAN)

        # self.camera.exposure_mode = 'off'
        if constants.Scanning.RESIZE is None:
            self.CAMERA_RES=self.camera.resolution
        else:
            self.CAMERA_RES=constants.Scanning.RESIZE

        self.printSettings()

    def setResolution(self, resolution):  # w x h
        self.camera.resolution = resolution

    def setFrameRate(self, frameRate):
        self.camera.framerate = frameRate
        if constants.Control.mRealTime is not None:
            constants.Control.mRealTime.updateFrameTime(frameRate)
        #self.printSettings()

    def setExposure(self, msec):#USED
        #if constants.Info.PROJ_MODEL=='C6_V2':#added v3.02 as a patch for if old pc software (v1.24 and before) sending bad exposure times. Ideally use later PC versions.
        #    msec=self.roundExposure(msec)
        #frameRate=1000/msec
        #if constants.Scanning.IMAGE_STACK<2:
        #if frameRate>30:
        #    frameRate=30
        #        frameRate=29.3
        #    else:
        #        frameRate=frameRate/1.0238
        #else:
        #    if frameRate>30:
        #        frameRate=29.6
        #    else:
        #        frameRate=frameRate/1.0135
        #self.camera.framerate=frameRate
        print('exp request',int(msec*1000))
        self.camera.shutter_speed = int(msec*1000)
        #self.printSettings()
        
    def setExposureAndMaxFrameRate(self, msec):#used by lag test to get 90fps, and by auto exposure.
        frameRate=1000/msec
        if frameRate>constants.Scanning.MAX_FRAME_RATE:
            frameRate=constants.Scanning.MAX_FRAME_RATE
        self.setFrameRate(frameRate)
        #self.camera.framerate=frameRate
        self.camera.shutter_speed = int(msec*1000)
        self.printSettings()
        
    def roundExposure(self, msec):
        msec=round(msec/10)*10
        return msec

    def setAutoExposureThenLock(self):
        #NEW AF alg. - picks highest exposure that is not more than targetMax (old algo used to pick so peak grey was closest to targetMax.
        #note using factory auto exposure changes iso secretly by adjusting analogue gain, so no good.
        #max allowed grey was 245 for v2.03 which had 5 nd2 filter units (allows 10% more lux than 240 before using 8.3msec, which is less accurate).
        #Using 240 will give better colour capture images because of less saturation.  strips seems to be fine even at 245 setting.
        #Decision was use 240 to be safe on future models.  I could set depending on serial number but probably not worth it, just use v2.04 firmware on nd4 models and if ever need to upgrade v2.03 models it won't make much difference, maybe even an improvement.
        #Addendum May 2020 now setting nd2 units to 240, and nd4 to 230 because had over exposure on some ambient lightings.
        #bestScore=100000#99999
        bestExposure=constants.Scanning.AUTO_EXPOSURE_LIST[0]
        bestMax=-1
        borderTrimL=100#pixels off edge
        borderTrimR=300#pixels off edge
        borderTrimT=100#pixels off edge
        borderTrimB=0#pixels off edge
        if self.camera.recording:
            self.camera.stop_recording()#needed to change frameRate
        for msec in constants.Scanning.AUTO_EXPOSURE_LIST:
            self.setExposureAndMaxFrameRate(msec)
            mStream=self.captureColourJPG()#first image is funny so discard
            mStream=self.captureColourJPG()
            mStream.seek(0, 0)
            string = mStream.read()
            array = np.fromstring(string, np.uint8)
            mStream.close()
            testImage = cv2.imdecode(array, cv2.IMREAD_COLOR)
            testImage=testImage[borderTrimT:testImage.shape[0]-borderTrimB,borderTrimL:testImage.shape[1]-borderTrimR]#starty:endy,startx,endx
            scale=constants.Scanning.AUTO_EXPOSURE_DOWNSCALE/testImage.shape[0]
            testImage=cv2.resize(testImage, (0,0), fx=scale,fy=scale, interpolation=cv2.INTER_AREA)
            #show(testImage)
            maxGrey=np.max(testImage)
            print('msec, max grey:',msec, maxGrey)
            if maxGrey>constants.Scanning.AUTO_EXPOSURE_TARGET_MAX:
                print('Rejected ', msec ,' could cause saturation: >',constants.Scanning.AUTO_EXPOSURE_TARGET_MAX, 'maxGrey was ', maxGrey)
                break#exit if exposure too high, not point trying higher exposures.
            else:
                bestExposure=msec
                bestMax=maxGrey

        print('Auto Exposure chosen as:', bestExposure, ' targetMax:', constants.Scanning.AUTO_EXPOSURE_TARGET_MAX, ' with max grey:',bestMax)
        self.setFrameRate(constants.Scanning.MAX_FRAME_RATE)
        self.setExposureAndMaxFrameRate(bestExposure)
        if bestExposure<12:
            print('HIGH AMBIENT LIGHT OR STONG REFLECTION WARNING')
            playSound.file(soundCode=constants.Sounds.HIGH_AMBIENT_LIGHT)
        return bestExposure

    #NOTE colour resolution is quarter when capturing rgb or yuv so use higher resolution and downscale.
    def getOpticalAngleImage(self):
        img=np.empty((int(1664*928*1.5),),dtype=np.uint8)
        try:
            self.camera.capture(img,format='yuv',use_video_port=True, resize=None)
        except Exception as e:
            print("Camera error", e)
        yChannelSize=int(1664*928)
        img=img[0:yChannelSize].reshape((928,1664))
        return np.copy(img)
    
    
    def getOpticalAngleMarkerImage(self):
        #resolution should be set to 1440,1088
        #WARNING MUST BE DOWNSCALED BY 1080/1088 in DECODE IMAGES SO IT MATCHES CALIB IMAGES
        img=None
        try:
            img=np.empty((1648*928*3,),dtype=np.uint8)
            self.camera.capture(img,format='bgr',use_video_port=True, resize=None)#TODO can I hardware resize for speed?
        except Exception as e:
            print("Camera error", e)
        img=img.reshape((928,1648,3))
        #return np.copy(img)
        return img

    def getScanImageStack(self):
        #WARNING MUST BE DOWNSCALED BY 1080/1088 in DECODE IMAGES SO IT MATCHES CALIB IMAGES
        imageList=[]
        if constants.Scanning.RESIZE==None:
            w=self.CAMERA_RES[0]
            h=self.CAMERA_RES[1]
        else:
            w=constants.Scanning.RESIZE[0]
            h=constants.Scanning.RESIZE[1]
        for i in range(constants.Scanning.IMAGE_STACK):
            imageList.append(np.empty((int(h*w*1.5),),dtype=np.uint8))
        try:
            self.camera.capture_sequence([imageList[i] for i in range(len(imageList))],format='yuv',use_video_port=True, resize=constants.Scanning.RESIZE)
        except Exception as e:
            print("Camera error", e)
        yChannelSize=int(h*w)
        sumImage=imageList[0][0:yChannelSize].reshape((h,w))
        if len(imageList)>1:
            sumImage=sumImage.astype(np.float32)
            for i in range(1,len(imageList)):
                sumImage+=imageList[i][0:yChannelSize].reshape((h,w)).astype(np.float32)
            sumImage=sumImage/constants.Scanning.IMAGE_STACK
        return sumImage.astype(np.uint8)
    
    def captureColourImageStack(self):#need 6 averages to make good job of removing 8.3msec proj colour banding.
        #resolution should be set to 1440,1088
        #WARNING MUST BE DOWNSCALED BY 1080/1088 in DECODE IMAGES SO IT MATCHES CALIB IMAGES
        #print('camera res:', self.CAMERA_RES[1]*self.CAMERA_RES[0]*3)
        imageList=[]
        if constants.Scanning.RESIZE==None:
            w=self.CAMERA_RES[0]
            h=self.CAMERA_RES[1]
        else:
            w=constants.Scanning.RESIZE[0]
            h=constants.Scanning.RESIZE[1]
        for i in range(constants.Scanning.IMAGE_STACK):
            imageList.append(np.empty((w*h*3,),dtype=np.uint8))
        try:
            self.camera.capture_sequence([imageList[i] for i in range(len(imageList))],format='bgr',use_video_port=True, resize=constants.Scanning.RESIZE)
        except Exception as e:
            print("Camera error", e)
        sumImage=imageList[0].reshape((h,w,3))
        if len(imageList)>1:
            sumImage=sumImage.astype(np.float32)
            for i in range(1,len(imageList)):
                sumImage+=imageList[i].reshape((h,w,3)).astype(np.float32)
            sumImage=sumImage/constants.Scanning.IMAGE_STACK
        return sumImage.astype(np.uint8)

    def captureColourJPG(self):
        try:
            mStream = io.BytesIO()
            self.camera.capture(mStream,format='jpeg',use_video_port=True, resize=constants.Scanning.RESIZE, quality=constants.Scanning.JPG_QUALITY)
        except Exception as e:
            print("Camera error", e)
            return None
        #mStream.close()
        return mStream

    def startVideoAndProcessing(self, mode='yuv'):
        if constants.Control.mRealTime is None:
            return
        try:
            if self.camera.recording:
                self.stopVideo()
            if mode=='yuv':
                self.camera.start_recording(constants.Control.mRealTime, format='yuv', resize=constants.Scanning.RESIZE)
            if mode=='mjpeg':
                self.camera.start_recording(constants.Control.mRealTime, format='mjpeg', bitrate=constants.Scanning.BIT_RATE, resize=constants.Scanning.RESIZE)#60000000 for desktop FHD
                self.currentBitRate=constants.Scanning.BIT_RATE
            print('start_recording')
        except Exception as e:
            print("Camera video error:",e)
            #print('mReal, bitrate, resize', constants.Control.mRealTime, constants.Scanning.BIT_RATE, constants.Scanning.RESIZE)
        return True

    def stopVideo(self):
        try:
            self.camera.stop_recording()
            print('stop_recording')
        except Exception as e:
            print("Camera video error:", e)
        return True

    def wait(self, time):
        try:
            self.camera.wait_recording(time)
        except Exception as e:
            print("Camera video error:",e)
            return False
        return True


