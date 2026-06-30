import numpy as np
import time
import os
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

    def _is_pi5(self):
        return os.uname()[1] == constants.Info.PI5_UNAME

    def syncCameras(self, captureTimePi2):  # used by pi2 / right camera on pi5

        captureTimePi1 = constants.Protocol.CAPTURE_TIME_PI_1
        syncError = 99999
        # On Pi5 both cameras share the same hardware clock so CLOCK_OFFSET is 0;
        # the sync logic still measures the inter-camera frame-boundary skew.
        clockOffset = constants.Protocol.CLOCK_OFFSET if constants.Protocol.CLOCK_OFFSET is not None else 0
        if captureTimePi1 is not None:
            syncError = self.calcSyncError(captureTimePi1, captureTimePi2, clockOffset)
            if constants.DEBUG.SYNC_CAMERAS:
                pass
                self.adjustFrameRate(syncError)
        if abs(syncError) < 1 and not self.goodSync:
            self.goodSync = True
            print('Good camera sync', syncError)
        if abs(syncError) >= 4 and self.goodSync:
            self.goodSync = False
            print('Poor camera sync', syncError)

    def calcSyncError(self, captureTimePi1, captureTimePi2, clockOffset=None):
        if clockOffset is None:
            clockOffset = constants.Protocol.CLOCK_OFFSET if constants.Protocol.CLOCK_OFFSET is not None else 0
        captureTimePi2Corrected = captureTimePi2 - clockOffset
        thisFrameTime = captureTimePi2Corrected - self.lastCaptureTimePi2Corrected
        self.lastCaptureTimePi2Corrected = captureTimePi2Corrected
        syncError = (captureTimePi2Corrected - captureTimePi1) % thisFrameTime
        # make syncError + or - around 0, in msec
        self.frameTime = 1000 * 1.0 / self.camera.framerate  # frame time in msec
        syncError = syncError / 1000  # for msec
        halfShift = syncError + self.frameTime / 2
        frameShift = int(halfShift / self.frameTime)
        syncError = syncError - frameShift * self.frameTime
        return syncError

    def adjustFrameRate(self, syncError):
        adjustmentSize = abs(0.3 * self.camera.framerate * syncError / self.frameTime)
        if syncError > ACTION_THRESHOLD:  # msec
            delta = +adjustmentSize
        elif syncError < -ACTION_THRESHOLD:  # msec
            delta = -adjustmentSize
        else:
            delta = 0
        self.camera.framerate_delta = delta

    def blockUntilSyncGood(self):
        while not self.goodSync:
            time.sleep(0.1)
        print('Sync Good')









