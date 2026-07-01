import cv2
import numpy as np
import captureVideo
import time
import constants


def show(image):
    #image=image.astype(np.float32)
    #print(np.max(image))
    #image=2*image/np.max(image)
    #image = image/1024
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return None

def testAveraging():
    mCapture=capture(preview=False, resolution=(1440,1088))

    count=1
    average=mCapture.getScanImage().astype(np.float32)
    while count<100:
        image=mCapture.getScanImage()#runs at 200ms per frame
        average=(average*count+image.astype(np.float32))/(count+1)
        count+=1
        #show(average/255)
        print(count)
    cv2.imwrite('single.png', image)
    cv2.imwrite('saveraged.png', average)

def testAveraging2():
    mCapture=capture(preview=False, resolution=(1440,1088))
    
    captures=[1,2,3,4,5,10,15,100]
    for i in captures:
        print('start')
        average=mCapture.getScanImageStack(averages=i)#about 68msec per frame
        print('stop')
        #cv2.imwrite('single.png', image)
        cv2.imwrite('saveraged'+str(i)+'.png', average[500:600,500:600])

def fullResPreview():
    camera=PiCamera(sensor_mode=5)
    camera.start_preview()
    time.sleep(300)
    
def findGoodExposures():
    constants.Scanning.RESOLUTION=(1920,1088)
    mCapture=captureVideo.capture()
    mCapture.openCamera()
    exp=8.0
    while exp<35.0:
        exp+=0.1
        #exp=33.2
        mCapture.setExposure(exp)
        print(exp)
        #cvImage=mCapture.getScanImage()
        #cvImage=mCapture.getScanImage()
        cvImage=mCapture.captureColourImageStack()
        cvImage=mCapture.captureColourImageStack()
        cv2.imwrite('testExposures/test'+'{0:06.2f}'.format(exp)+'.png',cvImage)
        time.sleep(3)
    mCapture.closeCamera()

    
def testGoodExposures():
    mCapture=capture(preview=True, resolution=(1440,1088))
    expList=[10.0,20.0,30.0,40.0,50.0,60.0,100.0]
    for exp in expList:
        #exp=33.2
        mCapture.setExposure(exp)
        print(exp)
        #cvImage=mCapture.getScanImage()
        #cvImage=mCapture.getScanImage()
        #cv2.imwrite('testExposures/test'+'{0:06.2f}'.format(exp)+'.png',cvImage)
        time.sleep(1)

        
def testGoodFrameRate():
    expList=[29.3,29.2,29.1,29.0,28.9,28.8,28.7]
    expList=[27.5, 27, 26.7,26,25,24,23]
    #for exp in expList:
    for exp in np.arange(30.0,25,-0.1):
        constants.Scanning.MAX_FRAME_RATE=exp
        mCapture=capture(preview=True, resolution=(1440,1088), initExposure=10.0)
        print(exp)
        #time.sleep(4)
        msg=input("E")
        mCapture.closeCamera()
        
def testGhostImage():
    if constants.DEBUG.PROJ_SCREEN_DEBUG_MODE:
        import projScreen  # pygame based - works in gui
    else:
        import projScreenFB as projScreen  # direct screen access from CLI - much faster.
    mProjScreen=projScreen.projScreen()
    mProjScreen.showImageFromFilePadded('2stripeb')
    mCapture=capture(preview=False, resolution=(1440,1088))
    mCapture.setExposure(100)
    
    print('start')
    img=mCapture.getScanImageStack(averages=5)#about 68msec per frame
    print('stop')
    img=img.astype('float32')
    img=cv2.resize(img,(720,544))
    print(img.dtype)
    show(img/255)
    #cv2.imwrite('test.png', img)
    
def testResSwitch():
    w=1920
    h=1088
    
    w2=1440
    h2=1088
    
    w3=1430
    h3=1080
    
    w4=1906#1906 is calculated
    h4=1080
    
    scale=1080/1088
    
    mCapture=capture(preview=False, resolution=(w2,h2))
    mCapture.setExposure(33)
    
    print('start')
    img=mCapture.getScanImageStack(averages=5)
    
    mCapture.setResolution((w,h))
    img2=mCapture.getScanImageStack(averages=5)
    
    #img=cv2.resize(img,(w3,h3))
    #img2=cv2.resize(img2,(w4,h4))
    
    img=cv2.resize(img,(0,0),fx=scale,fy=scale, interpolation=cv2.INTER_CUBIC)
    img2=cv2.resize(img2,(0,0),fx=scale,fy=scale, interpolation=cv2.INTER_CUBIC)
    
    print(img.shape, img2.shape)
    
    w3=img.shape[1]
    w4=img2.shape[1]
    
    left=int((w4-w3)/2)
    right=w4-w3-left
    img = cv2.copyMakeBorder(
        img,
        top=0,
        bottom=0,
        left=left,
        right=right,
        borderType=cv2.BORDER_CONSTANT,
        value=[128, 128, 128]
    )


    print(img.shape)
    print(img2.shape)
    img=img.astype('float32')/255
    img2=img2.astype('float32')/255
    
    show((img-img2)/2+0.5)
    
def testResSwitch2():
    w=3264
    h=2448
    
    camera = PiCamera(sensor_mode=2)
    camera.resolution = (w, h)
    #camera.start_preview()
    # Camera warm-up time
    time.sleep(2)
    #camera.capture('test.jpg')
    
    #camera=PiCamera(sensor_mode=2)
    #camera.shutter_speed=33
    img=np.empty((int(3264*2464*1.5),),dtype=np.uint8)
    camera.capture(img,format='yuv',use_video_port=True, resize=None)
    print(img.shape)
    
    
    show(img)
    
    
def testJPGvsYUV():
    mCapture=capture(preview=False, resolution=(1856,1088))
    mCapture.setExposure(33)
    time.sleep(2)
    mStream=mCapture.captureColourJPG(resize=None, quality=10)
    mStream.seek(0, 0)
    string=mStream.read()
    mCapture.captureFocusJPG().close()
    array=np.fromstring(string, np.uint8)
    cvImage=cv2.imdecode(array,cv2.IMREAD_COLOR)
    time.sleep(1)
    img=mCapture.getScanImage()
    cvImage=cv2.cvtColor(cvImage, cv2.COLOR_RGB2GRAY)
    show(0.5+(img.astype('float32')-cvImage.astype('float32'))/255)
        
        
def openCloseTest():
    mCapture=captureVideo.capture(preview=False)
    time.sleep(2)
    print(mCapture.isOpen())
    time.sleep(1)
    mCapture.closeCamera()
    time.sleep(2)
    mCapture.closeCamera()
    print(mCapture.isOpen())
    mCapture.openCamera()
    time.sleep(2)
    mCapture.openCamera()
    print(mCapture.isOpen())
    
def testAE():
    mCapture=captureVideo.capture(preview=False)
    time.sleep(2)
    mCapture.setAutoExposureThenLock()
    
def testExposures():
    mCapture=captureVideo.capture(preview=True)

    mCapture.setFrameRate(9.9882)
    #mCapture.setExposure(10.01)
    #mCapture.setFrameRate(30)
    mCapture.setExposure(1)
    msg=input('M')
    expList=[10.0, 10.01, 11.02]
    #expList=[20.0, 20.01, 20.02]
    #for exp in expList:
    #for exp in np.arange(9.0,11.2, 0.1):
    for fr in np.arange(9.984,10.0, 0.001):
        #exp=33.2
        mCapture.setFrameRate(fr*2.5)
        #mCapture.setExposure(exp)
        print(fr)
        #time.sleep(5)
        msg=input('M')
        #cvImage=mCapture.getScanImage()
        #cvImage=mCapture.getScanImage()
        #cv2.imwrite('testExposures/test'+'{0:06.2f}'.format(exp)+'.png',cvImage)


if __name__ == "__main__":
    #openCloseTest()
    #testAE()
    #testExposures()
    findGoodExposures()
    
