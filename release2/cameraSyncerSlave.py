import numpy as np
import time
import constants

ACTION_THRESHOLD = 1  # 0.1*self.frameTime#msec - if syncError more than this then do an adjustment


class cameraSyncerSlave():
    # variable shared over all classes

    def __init__(self, camera=None):
        # variable for this instance - self..
        self.clockPi1 = None
        self.clockPi2 = None
        self.captureTimePi2 = None
        self.lastCaptureTimePi2Corrected = 0
        self.goodSync = False
        self.frameTime = None
        self.camera = camera
        # constants.Protocol.CAPTURE_TIME_PI_1=None
        # constants.Protocol.CLOCK_OFFSET=None

    def syncCameras(self, captureTimePi2):  # used by pi2

        captureTimePi1 = constants.Protocol.CAPTURE_TIME_PI_1
        syncError = 99999
        if captureTimePi1 is not None and constants.Protocol.CLOCK_OFFSET is not None:
            syncError = self.calcSyncError(captureTimePi1, captureTimePi2)
            if constants.DEBUG.SYNC_CAMERAS:
                pass
                self.adjustFrameRate(syncError)
        if abs(syncError) < 1 and not self.goodSync:
            self.goodSync = True
            print('Good camera sync', syncError)
        if abs(syncError) >= 4 and self.goodSync:
            self.goodSync = False
            print('Poor camera sync', syncError)

    def calcSyncError(self, captureTimePi1, captureTimePi2):
        captureTimePi2Corrected = captureTimePi2 - constants.Protocol.CLOCK_OFFSET
        thisFrameTime = captureTimePi2Corrected - self.lastCaptureTimePi2Corrected
        self.lastCaptureTimePi2Corrected = captureTimePi2Corrected
        syncError = (captureTimePi2Corrected - captureTimePi1) % thisFrameTime
        # make syncError + or - around 0, in msec
        self.frameTime = 1000 * 1.0 / self.camera.framerate  # frame time in msec, #set approx framerate (frame rate from camera is actually off by the odd msec)
        syncError = syncError / 1000  # for msec
        halfShift = syncError + self.frameTime / 2
        frameShift = int(halfShift / self.frameTime)
        syncError = syncError - frameShift * self.frameTime
        #print('thisFrameTime, syncError, captureTimePi1:',thisFrameTime, syncError, captureTimePi1)
        return syncError

    def adjustFrameRate(self, syncError):
        #adjustmentSize = abs(0.1 * self.camera.framerate * syncError / self.frameTime)#up to v3.01
        adjustmentSize = abs(0.3 * self.camera.framerate * syncError / self.frameTime)
        if syncError > ACTION_THRESHOLD:  # msec
            delta = +adjustmentSize
        elif syncError < -ACTION_THRESHOLD:  # msec
            delta = -adjustmentSize
        else:
            delta = 0
        self.camera.framerate_delta = delta
        #print('framerate delta', syncError, adjustmentSize, delta, self.camera.framerate, self.frameTime)

    def blockUntilSyncGood(self):
        while not self.goodSync:
            time.sleep(0.1)
        print('Sync Good')









