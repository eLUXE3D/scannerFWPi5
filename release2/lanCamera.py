import captureVideo
import constants
import os
import time
import io
import numpy as np
import lanClientPi
import lanHelpers
import cv2

def _is_pi5():
    return os.uname()[1] == constants.Info.PI5_UNAME

def startCamera():
    if constants.Control.mCapture.isOpen():
        print('start camera: camera already open')
        return
    
    constants.Control.mCapture = captureVideo.capture(preview=False, camera_id=0)

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
    except Exception as e:
        print('getCameraImage2', e)
    return

def getCameraSyncInfo(clientPC, commandDict):
    """Receive clock-sync data sent from the master camera.
    On Pi4 this arrives over the LAN from Pi1.
    On Pi5 it is called directly (clientPC is None); the clock offset is 0
    because both cameras share the same hardware clock.
    """
    clockPi1 = commandDict['clockPi1']
    constants.Protocol.CAPTURE_TIME_PI_1 = commandDict['captureTimePi1']

    # Determine clock offset
    if _is_pi5():
        # Both cameras on the same Pi5 share the same hardware clock.
        # CLOCK_OFFSET stays 0; still keep a running buffer so the sync
        # maths work without special-casing.
        clockOffset = 0
    else:
        if constants.Control.mCapture is not None and constants.Control.mCapture.isOpen():
            clockPi2 = constants.Control.mCapture.camera.timestamp
            clockOffset = clockPi2 - clockPi1
        else:
            clockOffset = 0

    if len(constants.Protocol.CLOCK_OFFSET_BUFFER) == 100:
        constants.Protocol.CLOCK_OFFSET_BUFFER = constants.Protocol.CLOCK_OFFSET_BUFFER[1:] + [clockOffset]
    else:
        constants.Protocol.CLOCK_OFFSET_BUFFER += [clockOffset]
    constants.Protocol.CLOCK_OFFSET = min(constants.Protocol.CLOCK_OFFSET_BUFFER)

    if clientPC is not None:
        lanHelpers.gracefullClose(clientPC)
    return


if __name__ == "__main__":
    pass

