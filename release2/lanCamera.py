import captureVideo
import constants
import os
import time
import io
import numpy as np
import lanClientPi
import lanHelpers
import cv2

def startCamera():
    if constants.Control.mCapture.isOpen():
        print('start camera: camera already open')
        return
    
    constants.Control.mCapture = captureVideo.capture(preview=False)

    print('camera started')
    
def getCameraImage(clientPC, commandDict):
    try:
        mStream = None
        # GET CAMERA IMAGE
        if not constants.Control.mCapture.isOpen():
            print('camera is closed, opening')  # assume camera closed so re open
            constants.Control.mCapture.openCamera()

        if commandDict['previewType'] == 'jpg':
            mStream = constants.Control.mCapture.captureColourJPG()
        if commandDict['previewType'] == 'yuv':
            sumImage = constants.Control.mCapture.getScanImageStack()
            mStream = io.BytesIO(sumImage.tostring())
        if commandDict['previewType'] == 'rgb':
            sumImage = constants.Control.mCapture.captureColourImageStack()
            mStream = io.BytesIO(sumImage.tostring())
        if commandDict['previewType'] == 'jpgStack':
            sumImage = constants.Control.mCapture.captureColourImageStack()
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), constants.Scanning.JPG_QUALITY]
            is_success, buffer = cv2.imencode('.jpg', sumImage, encode_param)
            mStream = io.BytesIO(buffer.tostring())

    except Exception as e:
        print('getCameraImage', e)

    try:
        if mStream is None:
            # create blank jpg and send it back
            print('creating blank image')
            img = np.zeros((405, 540), np.uint8)
            is_success, buffer = cv2.imencode(".jpg", img)
            mStream = io.BytesIO(buffer)
        # SEND mStream TO CLIENT
        mStream.seek(0, 0)
        try:
            clientPC.sendfile(mStream, 0)
        except Exception as e:
            print('ERROR getCameraImage: ', e)
        finally:
            lanHelpers.gracefullClose(clientPC)

        mStream.close()
        # print('SENT CAMERA IMAGE', time.time()-tick)
    except Exception as e:
        print('getCameraImage2', e)
    return

def getCameraSyncInfo(clientPC, commandDict):#used by pi2: triggered when pi1 has sent pi1 clock info to pi2.
    clockPi1 = commandDict['clockPi1']
    constants.Protocol.CAPTURE_TIME_PI_1 = commandDict['captureTimePi1']
    if constants.Control.mCapture is not None:
        if constants.Control.mCapture.isOpen():
            clockPi2 = constants.Control.mCapture.camera.timestamp
            clockOffset = clockPi2 - clockPi1
            if len(constants.Protocol.CLOCK_OFFSET_BUFFER) == 100:  # buffer last 20 or so readings and take min (had lowest latency
                constants.Protocol.CLOCK_OFFSET_BUFFER = constants.Protocol.CLOCK_OFFSET_BUFFER[1:] + [clockOffset]
            else:
                constants.Protocol.CLOCK_OFFSET_BUFFER += [clockOffset]
            constants.Protocol.CLOCK_OFFSET = min(constants.Protocol.CLOCK_OFFSET_BUFFER)
            rangeTest = max(constants.Protocol.CLOCK_OFFSET_BUFFER) - constants.Protocol.CLOCK_OFFSET
    # print('CAPTURE_TIME_PI_1',constants.Protocol.CAPTURE_TIME_PI_1, 'CLOCK_OFFSET (msec)', constants.Protocol.CLOCK_OFFSET /1000, 'rangeTest',rangeTest)
    lanHelpers.gracefullClose(clientPC)
    return


if __name__ == "__main__":
    pass

