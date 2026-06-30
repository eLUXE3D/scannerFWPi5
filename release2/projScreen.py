import os
import pygame
import time
import cv2
import numpy as np
import constants
 
class projScreen:
    screen = None;
    
    def __init__(self):
        "Ininitializes a new pygame screen using the framebuffer"
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            print ("I'm running under X display = {0}".format(disp_no))
        
        # Check which frame buffer drivers are available
        # Start with fbcon since directfb hangs with composite output
        drivers = ['fbcon', 'directfb', 'svgalib']
        found = False
        for driver in drivers:
            # Make sure that SDL_VIDEODRIVER is set
            if not os.getenv('SDL_VIDEODRIVER'):
                #os.putenv('SDL_VIDEODRIVER', driver)
                #print(driver)
                pass
            try:
                pygame.display.init()
                print('driver used was', pygame.display.get_driver())
            except pygame.error:
                print ('Driver: {0} failed.'.format(driver))
                continue
            found = True
            break
    
        if not found:
            raise Exception('No suitable video driver found!')
        else:
            print('SDL_VIDEODRIVER', os.getenv('SDL_VIDEODRIVER'))
        
        #IF FULL SCREEN:
        self.size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        if constants.DEBUG.PROJ_SCREEN_DEBUG_MODE:
            self.screen = pygame.display.set_mode(self.size, pygame.RESIZABLE)#can close if crashes
        else:
            self.screen = pygame.display.set_mode(self.size, pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)#orig v3.01 
            #self.screen = pygame.display.set_mode(self.size, pygame.FULLSCREEN | pygame.HWSURFACE)
        
        #IF WINDOW - for debug
        #self.size=(854,480)
        #self.size=(1280,720)
        #self.screen = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        print ("Window size: %d x %d" % (self.size[0], self.size[1]))
        # Clear the screen to start
        #self.screen.fill((0, 0, 0))        
        # Render the screen
        pygame.display.flip()
        
        #INITIALISE
        self.startTime=None
        self.started=False
        self.displayTimes=[]
        self.imageArray=np.array([0], 'uint8')#small dummy,
 
    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."
        #pygame.quit()
        pass
        
    def bufferImageFromArray(self, index):
        index=index%1000#so image 105 is 5, and 205 is 5, etc. so can use big labels to identify repeat images but actually use the same image from buffer.
        if self.imageArray.shape==(1,):
            self.loadImagesAndResize()#orig
            #self.loadImagesAndPad()#TODO JUST TESTING
        #tick=time.perf_counter()
        try:
            pygame.surfarray.blit_array(self.screen, self.imageArray[index])#note: must be colour, its rotated from the way np images are, so need to pre rotate
        except Exception as e:
            print('ERROR blit:',e)
        #print('buffer', time.perf_counter()-tick)
        
    def showBuffer(self):
        #tick=time.perf_counter()
        try:
            pygame.display.flip()
        except Exception as e:
            print('ERROR flip:',e)
        #print('showed buffer', time.perf_counter()-tick)
        
    def showImageFromArray(self, index):
        index = index % 1000
        if self.imageArray.shape==(1,):
            self.loadImagesAndResize()
        tick=time.perf_counter()
        try:
            pygame.surfarray.blit_array(self.screen, self.imageArray[index])#note: must be colour, its rotated from the way np images are, so need to pre rotate
            #pygame.display.update()
            pygame.display.flip()
        except Exception as e:
            print('ERROR showImageFromArray:',e)
        #print('showImageFromArray', index, time.perf_counter()-tick)

    def showImageFromFile(self, filename):
        try:
            pathAndFilename=os.path.join('Images', filename+'.png')
            img= cv2.imread(pathAndFilename)
            img=cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
            img = cv2.flip( img, -1 )#mirror both h and v
            img=cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
            img=cv2.resize(img,(self.size[1],self.size[0]))
            print('showImageFromFile', filename, img.shape)
            pygame.surfarray.blit_array(self.screen, img)#note: must be colour, its rotated from the way np images are, so need to pre rotate
            pygame.display.flip()
        except Exception as e:
            print('ERROR showImageFromFile:',e)#error catch does not work for pygame it can still crash program out completely.

    def showImageFromFilePadded(self, filename):
        try:
            imagePadded=np.zeros((self.size[0],self.size[1],3), 'uint8')
            pathAndFilename=os.path.join('Images', filename+'.png')
            img= cv2.imread(pathAndFilename)
            img=cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
            img = cv2.flip( img, -1 )#mirror both h and v
            img=cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
            w=img.shape[0]
            h=img.shape[1]
            imagePadded[0:w, 0:h,:]=img
            print('showImageFromFile', filename, imagePadded.shape)
            pygame.surfarray.blit_array(self.screen, imagePadded)#note: must be colour, its rotated from the way np images are, so need to pre rotate
            pygame.display.flip()
        except Exception as e:
            print('ERROR showImageFromFile:',e)#error catch does not work for pygame it can still crash program out completely.
        
    def loadImagesAndResize(self):#USED
        numberOfImagesInArray=len(constants.Scanning.SCAN_IMAGE_ARRAY_FILENAMES)
        self.imageArray=np.zeros((numberOfImagesInArray,self.size[0],self.size[1],3), 'uint8')
        for i in range(numberOfImagesInArray):#24 grey190, 25 black, 26 white
            pathAndFilename='Images/'+constants.Scanning.SCAN_IMAGE_ARRAY_FILENAMES[i]+'.png'
            if constants.DEBUG.DEBUG_NUMBER_IMAGES:
                pathAndFilename='Images/n'+str(i).zfill(4)+'.png'
            print(pathAndFilename)
            img= cv2.imread(pathAndFilename)
            img = cv2.flip( img, -1 )#mirror both h and v
            img=cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
            self.imageArray[i]=cv2.resize(img,(self.size[1],self.size[0]), interpolation = cv2.INTER_CUBIC)#orig cv2.INTER_CUBIC
        print('loaded imageArray',self.imageArray.shape)

    def delImages(self):
        self.imageArray=np.array([0], 'uint8')#small dummy, setting to None makes all elements none and so does not clear memory.
        print(self.imageArray.shape)
        
    def closeProjWindow(self):
        try:
            pygame.display.quit()#TODO, doesn't really shut down properley, cpu thread still left 100%
            pygame.quit()
        except Exception as e:
            print('ERROR closeProjWindow:',e)
        
        #time.sleep(5)
        print('projScreen quit')
        
    def test(self):
        # Fill the screen with red (255, 0, 0)
        red = (255, 0, 0)
        self.screen.fill(red)
        # Update the display
        pygame.display.flip()
        



if __name__ == "__main__":
    #test image
    #mProjScreen=projScreen()
    #mProjScreen.showImageFromFile('n0012')
    #time.sleep(10)
    #mProjScreen.closeProjWindow()
    #exit()
    
    
    print("cv2 version", cv2.__version__)
    mProjScreen=projScreen()
    for i in range(26):
        mProjScreen.bufferImageFromArray(i)
        print('buffered')
        time.sleep(0.1)
        mProjScreen.showBuffer()
        print('showed buffer')
        time.sleep(0.1)
    mProjScreen.closeProjWindow()
    exit()
    #mProjScreen.loadImagesAndResize()
    #mProjScreen.showImageFromArray(10)
    mProjScreen.showImageFromFile('bsb__')
    time.sleep(5)
    mProjScreen.closeProjWindow()





        
 

 
