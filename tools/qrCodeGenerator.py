import pyqrcode
import cv2
import numpy as np

FOLDER='C:/Work-TupelGit/Teeth/tools/qrLabels/'

def makeQRpng(plateNumber=100):
    #generate QR CODE
    #version specifies size, ver=1 can hold more than a trillion so I can lock size to 1.
    #error H means 30% damage ok.
    #mode numeric means can only take numbers
    plateNumberStr=str(plateNumber)
    filename=FOLDER+'qrLabel'+plateNumberStr.zfill(4)+'.png'
    plateQRcode = pyqrcode.create(plateNumber, error='H', version=1, mode='numeric')
    plateQRcode.png(filename, scale=20, module_color=[0, 0, 0, 255], background=[0xff, 0xff, 0xff])
    qrPNG=cv2.imread(filename)
    #print(qrPNG.shape)
    top=0
    bottom=250
    left=0
    right=0
    qrPNG = cv2.copyMakeBorder(qrPNG, top, bottom, left, right, cv2.BORDER_CONSTANT, None, (255,255,255))

    font= cv2.FONT_HERSHEY_PLAIN
    bottomLeftCornerOfText = (125,625)#x,y
    fontScale= 8
    fontColor= (0,0,0)
    lineType= 8

    cv2.putText(qrPNG,'Plate',
        bottomLeftCornerOfText,
        font,
        fontScale,
        fontColor,
        lineType)

    bottomLeftCornerOfText = (150,750)

    cv2.putText(qrPNG,plateNumberStr,
        bottomLeftCornerOfText,
        font,
        fontScale,
        fontColor,
        lineType)

    #crop
    c=25
    w=qrPNG.shape[1]
    h = qrPNG.shape[0]
    qrPNG=qrPNG[c:h-c,c:w-c]

    #Display the image
    #cv2.imshow("img",qrPNG)
    #cv2.waitKey(0)

    #Save image
    cv2.imwrite(filename, qrPNG)
    return qrPNG

def stitchMultipleLabelsToOneImage():
    rows=9
    cols=11
    qrPNG = makeQRpng(plateNumber=000)
    w=qrPNG.shape[1]
    h=qrPNG.shape[0]
    print(h,w)
    count = 998  # srdjan can use up to 799, then he must start from ?2500? or so
    for sheet in range(10,20):
        mainImage=np.ones((h*rows,w*cols), 'uint8')*255
        for y in range(0,h*rows,h):
            for x in range(0,w*cols,w):
                print(count)
                qrPNG=makeQRpng(plateNumber=count)
                count+=1
                mainImage[y:y+h,x:x+w]=qrPNG[:,:,0]
        #Display the image
        filename=FOLDER+'qrLabelOneSheet'+str(sheet).zfill(2)+'.png'
        cv2.imwrite(filename, mainImage)
        # cv2.imshow("img",mainImage)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()


if __name__ == '__main__':
    stitchMultipleLabelsToOneImage()

