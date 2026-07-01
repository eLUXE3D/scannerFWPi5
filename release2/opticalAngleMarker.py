import cv2
import numpy as np
import captureVideo
import time
import motorsArduino
import constants
if constants.DEBUG.PROJ_SCREEN_DEBUG_MODE:
    import projScreen  # pygame based - works in gui
else:
    import projScreenFB as projScreen  # direct screen access from CLI - much faster.



DEBUG=False

ANGLE_MARKER_WIDTH_REAL_WORLD = 64#32  # pixels
ANGLE_OUTER_HUE_REAL_WORLD = 35#opencv hue goes from 0 to 180, 0 or 180 is red,
ANGLE_INNER_HUE_REAL_WORLD = 97
MARKER_FOUND_THRESHOLD=8#higher means less likely to find a marker

def show(image1, image2=None):
    if DEBUG:
        if image1 is not None:
            cv2.imshow('image1', image1)
        if image2 is not None:
            cv2.imshow('image2', image2)
        cv2.waitKey(500)
        #cv2.destroyAllWindows()
    return None

class opticalAngleMarker():

    def __init__(self):
        pass
    
    def initialise(self):
        if constants.Control.mProjScreen is not None:
            constants.Control.mProjScreen.showImageFromArray(constants.Scanning.WHITE_IMAGE)
            time.sleep(0.2)#wait for proj to change and camera to flush buffer
        if constants.Control.mCapture is not None:
            #save currrent settings
            self.origSensorMode=constants.Scanning.CAMERA_MODE
            self.origResolution=constants.Scanning.RESOLUTION
            self.origZoom=constants.Scanning.ZOOM_L
            self.origFrameRate=constants.Scanning.FRAME_RATE
            self.origExposure=constants.Scanning.EXPOSURE_TIME_SCAN
            
            #modify settings for marker detection
            constants.Scanning.CAMERA_MODE=5
            constants.Scanning.RESOLUTION=(1640,922)
            constants.Scanning.ZOOM_L=(0, 0, 1, 1)
            constants.Scanning.FRAME_RATE = 30
            constants.Scanning.EXPOSURE_TIME_SCAN=8.33
            if constants.Info.PROJ_MODEL=='C6':
                constants.Scanning.EXPOSURE_TIME_SCAN=8.33
            if constants.Info.PROJ_MODEL=='C6_V2':
                constants.Scanning.EXPOSURE_TIME_SCAN=10.0
            constants.Control.mCapture.updateCameraSettings()
            
            print('OpticalAngleMarker saved camera params', self.origSensorMode, self.origResolution, self.origZoom, self.origFrameRate, self.origExposure)
            #print('START_TARGET',constants.Scanning.START_TARGET)
            
    def getDisp(self):#displacement
        frame=constants.Control.mCapture.getOpticalAngleMarkerImage()
        #show(frame)
        #crop
        xCrop1=975
        yCrop1=275
        ROI1=frame[yCrop1:900,xCrop1:xCrop1+450]
        
        x,y=self.detectMarkerTemplate(ROI1)
        if x is None and y is None:
            return 1500#likely position if marker not found TODO could ask user to level table
        
        disp=x+y
        print('disp', disp)
        
        return disp
        
    def plotAngleVsDisp(self):
        mMotors=motorsArduino.motorsArduino()
        mMotors.powerOn(True, True)
        mMotors.setMotorNumber(motorsArduino.motorsArduino.MOTOR_V)
        for theta in np.arange(-90,45,9):
            mMotors.moveToAngle(float(theta), shortestRoute=False)
            d=self.getDisp()
            print(theta,d)
        mMotors.powerOn(False)
    
    def estimateAngleFromDisp(self,disp): #TODO retune this since res and FOV change
        #from a 2 degree polyfit of disp vs angle data
        #a=-0.0609801721
        #b=10.95757575
        #c=170.0666667-disp
        #angle=(-b+(b*b-4*a*c)**0.5)/(2*a)
        #TEMP
        angle=(disp-547)*0.261#TODO works ok for small corrections, could improve but slight gain only
        return angle
    
    def getAngleEstimate(self):
        d=self.getDisp()
        angleEstimate=self.estimateAngleFromDisp(d)
        return angleEstimate
    
    def genMarkerForFactoryPrint(self):#print circle 17mm wide, cut it 16mm wide (stamp), print line marker 9.5mm wide cut 9.5mm wide
        X_RES=360
        Y_RES=1080
        colours=[(255, 255, 0), (0, 255, 255)]#,(255, 0, 0),(0, 0, 255)]

        marker=np.ones((Y_RES,X_RES,3), 'uint8')*255
        marker = cv2.rectangle(marker, (0, 0), (int(X_RES / 3), int(Y_RES)), color=colours[1], thickness=-1, lineType=cv2.LINE_AA)
        marker = cv2.rectangle(marker, (int(X_RES *1/ 3), 0), (int(X_RES *2/ 3), int(Y_RES)), color=colours[0], thickness=-1, lineType=cv2.LINE_AA)
        marker = cv2.rectangle(marker, (int(X_RES *2/ 3), 0), (int(X_RES *3/ 3), int(Y_RES)), color=colours[1], thickness=-1, lineType=cv2.LINE_AA)

        show(marker)
        cv2.imwrite('opticalAngleMarker.png', marker)
        return

    def genTemplate(self):
        templateColours=[ANGLE_INNER_HUE_REAL_WORLD,ANGLE_OUTER_HUE_REAL_WORLD]#real world hue: outer, innner
        angleMarkerHeight=int(ANGLE_MARKER_WIDTH_REAL_WORLD/4)
        template=np.ones((angleMarkerHeight, ANGLE_MARKER_WIDTH_REAL_WORLD), 'uint8')*255
        template = cv2.rectangle(template, (0, 0),                                        (int(ANGLE_MARKER_WIDTH_REAL_WORLD / 3), angleMarkerHeight), color=templateColours[1], thickness=-1, lineType=cv2.LINE_AA)
        template = cv2.rectangle(template, (int(ANGLE_MARKER_WIDTH_REAL_WORLD *1/ 3), 0), (int(ANGLE_MARKER_WIDTH_REAL_WORLD *2/ 3), angleMarkerHeight), color=templateColours[0], thickness=-1, lineType=cv2.LINE_AA)
        template = cv2.rectangle(template, (int(ANGLE_MARKER_WIDTH_REAL_WORLD *2/ 3), 0), (int(ANGLE_MARKER_WIDTH_REAL_WORLD *3/ 3), angleMarkerHeight), color=templateColours[1], thickness=-1, lineType=cv2.LINE_AA)
        #show(template)
        return template

    def getHue(self, image):
        HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hue=HSV[:,:,0]
        hue=cv2.GaussianBlur(hue, (3,3), sigmaX=0, sigmaY=0)
        return hue

    def detectMarkerTemplate(self, image):
        templateHue=self.genTemplate()
        image=cv2.GaussianBlur(image, (3,3), sigmaX=0, sigmaY=0)#denoise
        hue=self.getHue(image)
        #show(templateHue)
        #print(hue.dtype, templateHue.dtype)
        #print(hue.shape, templateHue.shape)
        res = cv2.matchTemplate(hue,templateHue,cv2.TM_SQDIFF)#not using normalisation because it is hue so should be light intensity independent.
        #show(res/np.max(res))
        res=cv2.GaussianBlur(res, (3,31), sigmaX=2, sigmaY=15)#vertical blur to find centre of the vertical line that occurs in the correspondance map, and to blur out non marker features.
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        resInv=1/res
        resInv=resInv/np.max(resInv)
        peakToBgRatio=1/np.mean(resInv)
        print('Marker score:', peakToBgRatio)#min_loc + template res /2 is centre of marker #no marker min=10,069,664, marker min=856,448
        if peakToBgRatio<MARKER_FOUND_THRESHOLD:
            print('No marker found')
            return None,None
        marker_x = min_loc[0] + templateHue.shape[1] / 2
        marker_y = min_loc[1] + templateHue.shape[0] / 2
        #print('marker coords', marker_x,marker_y)
        #TEST
        hue=cv2.circle(hue, (int(marker_x),int(marker_y)), 5, color=255, thickness=1)
        resInv=cv2.circle(resInv, (int(marker_x),int(marker_y)), 5, color=1, thickness=1)
        #show(resInv)
        #show(hue)
        #show(image)
        return marker_x,marker_y#TODO get angle off y+x might be good
    
    def finish(self):
        constants.Scanning.CAMERA_MODE=self.origSensorMode
        constants.Scanning.RESOLUTION=self.origResolution
        constants.Scanning.ZOOM_L=self.origZoom
        constants.Scanning.FRAME_RATE=self.origFrameRate
        constants.Scanning.EXPOSURE_TIME_SCAN=self.origExposure
        constants.Control.mCapture.updateCameraSettings()




if __name__ == "__main__":
    #constants.Info.PROJ_MODEL='C6_V2'#TEST
    mOpticalAngleMarker=opticalAngleMarker()
    #mBTserver=BTserver.BTserver()
    #mProjScreen=projScreen.projScreen()
    #mBTserver=None
    constants.Control.mCapture=captureVideo.capture(preview=False)
    mOpticalAngleMarker.initialise()    #mOpticalAngleMarker.genTemplate()
    
    #mOpticalAngleMarker.plotAngleVsDisp()
    #exit()
    for x in range(1000):
        #image=constants.Control.mCapture.getOpticalAngleMarkerImage()
        #test=cv2.resize(image, (0,0), fx=0.25, fy=0.25) 
        #show(test)
        #mOpticalAngleMarker.detectMarkerTemplate(image)
        mOpticalAngleMarker.getDisp()
        #time.sleep(1)
    
