import numpy as np
import time
import os
import time
import cv2
import constants
import subprocess

import RPi.GPIO as GPIO #for implant post scanning
LED_PIN = 26 # Broadcom pin 26 (P1 pin 37)

#This might be good to add vsync?
#https://github.com/justincjack/rasp_pi_graphics

# Map the screen as Numpy array
# N.B. Numpy stores in format HEIGHT then WIDTH, not WIDTH then HEIGHT!
# c is the number of channels, 4 because BGRA
#https://stackoverflow.com/questions/58772943/show-an-image-with-omxiv-direct-from-memory-on-rpi?noredirect=1&lq=1
 
class projScreen:
    
    def __init__(self):
        #INITIALISE
        
        self.c =int(self.detectDisplayBitDepth()/8) #3 or 4 for 24 or 32 bit
        print('DISPLAY DEPTH:', self.c*8,'BIT. 24 BIT IS BEST')
        self.h, self.w= 720, 1280#v4.04
        #self.h, self.w= 480, 854#test
        #self.h, self.w= 450, 854#test
        #self.h, self.w = 600,800#test
        #self.h, self.w= 1080, 1920

        self.fb = np.memmap('/dev/fb0', dtype='uint8',mode='w+', shape=(self.h,self.w,self.c)) 
        #self.fbVerify = np.memmap('/dev/fb0', dtype='uint8',mode='r', shape=(self.h,self.w,self.c))
        self.imageArray=np.array([0], 'uint8')#small dummy,

        # Pin Setup for implant post scanning
        GPIO.setmode(GPIO.BCM)  # Broadcom pin-numbering scheme
        GPIO.setup(LED_PIN, GPIO.OUT)  # LED pin set as output
        GPIO.output(LED_PIN, GPIO.LOW)
        
    def detectDisplayBitDepth(self):
        #TODO deduce if 24 or 32 bit and set accordingly (32 bit is upgraded 3.01 machine, 24 is new machine).
        command = "fbset"
        p = subprocess.check_output(command, shell=True).decode()
        bitDepth=p.splitlines()[2][-2:]
        return int(bitDepth)
        
    def bufferImageFromArray(self, index):
        self.index= index % 1000
        
    def showBuffer(self):
        #tick=time.perf_counter()
        self.fb[:]=self.imageArray[self.index]
        self.fb.flush()#should write data to file - test to see if it helps delayed frame errors.
        #if np.all(self.fb[700,400]==self.fbVerify[700,400]):
        #    return True
        #else:
        #    print('ERROR: fb verify fail')
        #    return False
        #print('showed buffer', time.perf_counter()-tick)
        if self.index==25:#for implant post scanning - if showing black image turn LED lights on.
            GPIO.output(LED_PIN, GPIO.HIGH)
        else:
            GPIO.output(LED_PIN, GPIO.LOW)
        
    def showImageFromArray(self, index):
        index = index % 1000
        if self.imageArray.shape==(1,):
            self.loadImagesAndResize()
        self.fb[:]=self.imageArray[index]

    def showImageFromFile(self, filename):
        try:
            pathAndFilename=os.path.join('Images', filename+'.png')
            img= cv2.imread(pathAndFilename)
            img=cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
            img = cv2.flip( img, 0 )#mirror h
            img=cv2.resize(img,(self.w,self.h))
            if self.c==3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            if self.c==4:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
            print('showImageFromFile', filename, img.shape)
            self.fb[:]=img
        except Exception as e:
            print('ERROR showImageFromFile:',e)#error catch does not work for pygame it can still crash program out completely.
        
    def loadImagesAndResize(self):#USED
        #note custom image names from PC not used, because it was not used correctly in PCv2.01 to 2.03 inclusive.
        #could do if v>2.03 then use custom images, but risk of bug so will implement only if custom images are needed.
        imageNames = constants.Scanning.SCAN_IMAGE_ARRAY_FILENAMES_C6V2
        if constants.DEBUG.DEBUG_NUMBER_IMAGES:
            imageNames=constants.Scanning.SCAN_IMAGE_ARRAY_FILENAMES_NUMBERS
        else:
            if constants.Info.PROJ_MODEL == 'C6':
                imageNames = constants.Scanning.SCAN_IMAGE_ARRAY_FILENAMES_C6
            if constants.Info.PROJ_MODEL == 'C6_V2':
                imageNames=constants.Scanning.SCAN_IMAGE_ARRAY_FILENAMES_C6V2
            if constants.Info.PROJ_MODEL == 'C6_V2B':
                imageNames=constants.Scanning.SCAN_IMAGE_ARRAY_FILENAMES_C6V2B
            if constants.Info.PROJ_MODEL == 'C6_V3':
                imageNames=constants.Scanning.SCAN_IMAGE_ARRAY_FILENAMES_C6V3
                #imageNames=constants.Scanning.SCAN_IMAGE_ARRAY_FILENAMES_C6V3_TEST#TODO_Remove TEST

        self.imageArray=np.zeros((len(imageNames),self.h,self.w,self.c), 'uint8')
        for i in range(len(imageNames)):#24 grey190, 25 black, 26 white
            #indexString=str(i).zfill(4)
            pathAndFilename='Images/'+imageNames[i]+'.png'
            print(pathAndFilename)
            img= cv2.imread(pathAndFilename)
            img = cv2.flip( img, 0 )#mirror h
            #img=cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
            if self.c==3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            if self.c==4:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
            self.imageArray[i]=cv2.resize(img,(self.w,self.h), interpolation = cv2.INTER_CUBIC)#orig cv2.INTER_CUBIC
        print('loaded imageArray',self.imageArray.shape)

    def delImages(self):
        self.imageArray=np.array([0], 'uint8')#small dummy, setting to None makes all elements none and so does not clear memory.
        print(self.imageArray.shape)
        
    def closeProjWindow(self):
        pass
              

if __name__ == "__main__":
    #test image
    mProjScreen=projScreen()
    #mProjScreen.showImageFromFilePadded('bsb__')
    mProjScreen.showImageFromFile('n0012')
    #mProjScreen.showImageFromArray(2)
    time.sleep(2)
    exit()





        
 

 



