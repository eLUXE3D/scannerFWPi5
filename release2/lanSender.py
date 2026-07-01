import numpy as np
import time
from multiprocessing import Manager, JoinableQueue, Process#, Event
from threading import Event #TEST TODO
import constants
import copy
import io
import traceback
import socket

class lanSender():
            
    def __init__(self):
        self.lastSocket=None
        self.lastSocketJob=None
        
    def sendNextImageToPC(self, clientPC, commandDict):  # to send shots to PC
        #IF ALREADY SENDING - CANCEL IT, something is wrong, pc should not ask before last one was received.
        try:
            self.lastSocket.close()#should normally be error because it was already closed, but if not close it.
            print('SUCCESSFULLY CLOSED lastSocket',self.lastSocketJob, self.lastSocket.getsockname())
        except Exception as e:
            pass
            #print('CLOSE ERROR on Job: ',self.lastSocketJob, 'error: ' ,e)

        #REMOVE LAST SHOT RECEIVED BY PC (if it exists)
        lastImagePCreceived=commandDict["LAST_IMAGE_PC_RECEIVED"]

        if lastImagePCreceived is not None:
            with constants.Control.imageLock:
                for i in range(len(constants.Control.pcImageList)):
                    angleNumber= constants.Control.pcImageList[i][0]
                    if angleNumber==lastImagePCreceived:
                        constants.Control.pcImageList.pop(i)
                        break

        #GET NEXT SHOT (if it exists, else send None: -4).
        blocking=False
        if blocking:
            while True:
                with constants.Control.imageLock:
                    length=len(constants.Control.pcImageList)
                    #TODO if cancelled exit?
                    if length > 0:
                        dataToSendToPC = copy.deepcopy(constants.Control.pcImageList[0])
                        break
                time.sleep(0.5)
        else:
            with constants.Control.imageLock:
                if len(constants.Control.pcImageList)>0:
                    dataToSendToPC=copy.deepcopy(constants.Control.pcImageList[0])
                else:
                    dataToSendToPC=(-4, 0, 0, 0)#code for no image ready yet.

        #SEND NEXT SHOT - using process
        if len(dataToSendToPC)>=11:
            SCAN_ID=dataToSendToPC[10]
        else:
            SCAN_ID=None

        self.lastSocket=clientPC
        self.lastSocketJob=dataToSendToPC[0]
        useProcess=False
        if useProcess:
            self.sendImageToPConThread(clientPC, dataToSendToPC[0], dataToSendToPC[1], dataToSendToPC[2], dataToSendToPC[3], SCAN_ID)
        else:
            sendDoneFlag = Event()
            self.sendImageToPC(self.lastSocket, dataToSendToPC[0], dataToSendToPC[1], dataToSendToPC[2], dataToSendToPC[3], SCAN_ID, sendDoneFlag)

    def sendImageToPConThread(self, clientPC, angleNumber, lOrR, imageSet, angleData,  expectedImages, SCAN_ID):
        sendDoneFlag=Event()
        sendDoneFlag.clear()#clear not done, set done.
        worker1 = Process(target=self.sendImageToPC, args=(clientPC, angleNumber, imageSet, angleData, expectedImages,SCAN_ID, sendDoneFlag))
        worker1.daemon=True  # if true it will stop automatically if your program exits.
        worker1.start()
        worker1.join(timeout=12)#sec - terminates if not finished after 12 seconds.
        print('Send exitCode', worker1.exitcode, 'done flag ',sendDoneFlag.is_set(), 'job ', angleNumber)
        #sendDoneFlag.wait()#block until set
        if not sendDoneFlag.is_set():
            self.gracefullClose(clientPC)


    def sendImageToPC(self, clientPC, angleNumber, imageSet, angleData, expectedImages, SCAN_ID, sendDoneFlag):
        tick = time.time()
        bytesSent = 0
        fileSize = 0
        # PUT NUMPY IMAGE INTO A FILE IN MEMORY
        try:
            f = io.BytesIO()
            np.savez(f, angleNumber=angleNumber, imageSet=imageSet, angleData=angleData, expectedImages=expectedImages, SCAN_ID=SCAN_ID)
            f.seek(0, 2)
            fileSizeInt = f.tell()
            fileSize = '{:09d}'.format(fileSizeInt)
            f.seek(0, 0)
        except Exception as e:
            print('SEND ERROR1', e)
            self.gracefullClose(clientPC)
            f.close()
            sendDoneFlag.set()
            return

        try:
            bytesSent=clientPC.sendfile(f, 0)
        except Exception as e:
            print('SEND ERROR2: ', e, 'job', angleNumber)
            traceback.print_exc()
        finally:
            # GRACEFUL SHUTDOWN
            self.gracefullClose(clientPC)
            
        try:
            f.close()
            if angleNumber!=-4:
                print('SEND END', time.time() - tick, 'sec ', bytesSent, '/', fileSize, 'sent. Job', angleNumber)
            sendDoneFlag.set()
        except Exception as e:
            print('SEND ERROR3: ', e, 'job', angleNumber)
            traceback.print_exc()

        return

    def gracefullClose(self, clientPC):
        # on pi in python if os has to close port after 16 mins because its left hanging, then the whole python server crashes, so must take care to close them all to prevent scanner freezing up.

        # https://stackoverflow.com/questions/51281111/python-network-socket-client-freezes-sporadically
        # https://stackoverflow.com/questions/4160347/close-vs-shutdown-socket/23483487#23483487
        try:
            clientPC.shutdown(socket.SHUT_WR) #I've finished writing
            check = clientPC.recv(constants.Protocol.FILE_BUFFER_SIZE)  # have you finished sending? should be 0 length received if so
            while (check):
                print('Waiting for graceful close', clientPC.getsockname())
                check = clientPC.recv(constants.Protocol.FILE_BUFFER_SIZE)
            clientPC.close()
        except Exception as e:
            print('ERROR: gracefullClose ', e)
