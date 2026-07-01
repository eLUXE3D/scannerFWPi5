import lanClientPi

class cameraSyncerMaster():
    # variable shared over all classes

    def __init__(self, camera=None):
        # variable for this instance - self..
        # self.q = queue.Queue(maxsize=10)
        # self.worker = Thread(target=self.qProcessor, args=(self.q,self.mLanServer))
        # self.worker.setDaemon(True)  # if true it will stop automatically if your program exits.
        # self.worker.start()
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
            mLanClient = lanClientPi()
            mLanClient.sendCameraSyncInfo(clockPi1, captureTimePi1)
            q.task_done()
            # print('cameraSyncer task done')

    def sendSyncInfo(self, clockPi1, captureTimePi1):
        dataList = [clockPi1, captureTimePi1]
        self.q.put(dataList, True, None)

    def finish(self):
        self.q.join()  # wait for all jobs to finish
        # TODO do I need to stop thread?
        return


if __name__ == '__main__':
    pass




