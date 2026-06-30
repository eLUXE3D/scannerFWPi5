import os
import constants
import lanClientPi

class cameraSyncerMaster():
    # variable shared over all classes

    def __init__(self, camera=None):
        self.camera = camera

    def syncCameras(self, clockPi1, captureTimePi1):  # USED
        mLanClient = lanClientPi.lanClientPi()
        mLanClient.sendCameraSyncInfo(clockPi1, captureTimePi1)

    def qProcessor(self, q, mLanServer):
        # loop continuously processing jobs from the queue.
        while True:
            # dataList = [clockPi1, captureTimePi1]
            job = q.get(True)  # blocking
            clockPi1 = job[0]
            captureTimePi1 = job[1]
            mLanClient = lanClientPi.lanClientPi()
            mLanClient.sendCameraSyncInfo(clockPi1, captureTimePi1)
            q.task_done()

    def sendSyncInfo(self, clockPi1, captureTimePi1):
        dataList = [clockPi1, captureTimePi1]
        self.q.put(dataList, True, None)

    def finish(self):
        self.q.join()
        return


if __name__ == '__main__':
    pass




