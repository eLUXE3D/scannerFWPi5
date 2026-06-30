import os
import time
import cv2
import numpy as np
import constants
import captureVideo
import subprocess
if constants.DEBUG.PROJ_SCREEN_DEBUG_MODE:
    import projScreen  # pygame based - works in gui
else:
    import projScreenFB as projScreen  # direct screen access from CLI - much faster.

def show(image):
    #image=image.astype(np.float32)
    #print(np.max(image))
    #image=2*image/np.max(image)
    #image = image/1024
    cv2.imshow('image', image)
    cv2.waitKey(5000)
    cv2.destroyAllWindows()
    return None

def showImage():
    mProjScreen=projScreen.projScreen()
    mProjScreen.showImageFromFilePadded('npx_640')

def captureImage(filename):
    mCapture=captureVideo.capture(preview=False, resolution=(1440,1088))
    msec=33
    mCapture.setExposure(msec)
    cvImage=mCapture.getScanImage()
    #show(cvImage)
    cv2.imwrite('scanData/'+filename+'.png', cvImage)
    
def nextVideoMode():
    with open('/boot/config.txt', 'r') as file :
        filedata = file.read()

    # Replace the target string
    #OVERSCAN CHANGE
    #index=filedata.find('overscan_left=')
    #currentStr=filedata[index+14:index+17]
    #current=int(currentStr)
    #current-=1
    #currentStr=str(current).zfill(3)
    #filedata = filedata[:index+14] +currentStr+ filedata[index+17:]
    
    #TIMINGS CHANGE
    index=filedata.find('hdmi_timings=')
    currentStr=filedata[index+19:index+21]
    current=int(currentStr)
    current+=1
    currentStr=str(current).zfill(2)
    filedata = filedata[:index+19] +currentStr+ filedata[index+21:]

    # Write the file out again
    with open('/boot/config.txt', 'w') as file:
        file.write(filedata)
    
    print('currentStr', currentStr)
    return currentStr

def shutdown():
    os.system('sudo reboot')
    
if __name__ == "__main__":
        #keep screen always on for proj
    subprocess.call(['sudo', 'xset', 's','off'])
    subprocess.call(['sudo', 'xset', '-dpms'])
    subprocess.call(['sudo', 'xset', 's','noblank'])
    subprocess.call(['sudo', 'xset', 's','noblank'])
    os.chdir('/home/pi/Teeth/release2/')
    time.sleep(5)
    showImage()
    currentStr=nextVideoMode()
    captureImage(currentStr)
    print('captured Image')
    time.sleep(5)
    #mProjScreen.closeProjWindow()
    shutdown()
    

    exit()




        
 

 
