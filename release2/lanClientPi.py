import socket
import io
import numpy as np
import constants
import json
import osCommands
import uuid
import time
import os
import threading


class lanClientPi():
    # variable shared over all classes

    def __init__(self):
        # variable for this instance - self..
        self.sock = None
        self.connectionFail=False

    # ------------------------------------------------------------------
    # Pi5: in-process dispatch helpers
    # ------------------------------------------------------------------

    def _dispatchPi2ModeLocally(self, commandDict):
        """Run scanSlave.setPi2Mode() in a background thread and post the
        result to doneCommands so lanHelpers.checkIfDone() works unchanged."""
        CMD_ID = commandDict["CMD_ID"]
        def _run():
            try:
                msgDict = constants.Control.mScanSlaveLocal.setPi2Mode(commandDict)
            except Exception as e:
                print('Local Pi2 dispatch error:', e)
                msgDict = {}
            constants.Control.doneCommands.append((CMD_ID, msgDict))
            constants.Control.newCommandDoneFlag.set()
        t = threading.Thread(target=_run, daemon=True)
        t.start()

    def _syncCameraLocally(self, clockPi1, captureTimePi1):
        """Update the clock-sync constants directly (no LAN round-trip)."""
        import lanCamera
        commandDict = {'clockPi1': clockPi1, 'captureTimePi1': captureTimePi1}
        lanCamera.getCameraSyncInfo(None, commandDict)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def pingScanner(self, IP, PORT):
        commandDict={ "header":constants.Protocol.HEADER,
                      "command":constants.Protocol.CMD_PING}
        commandJSON=json.dumps(commandDict)

        self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.settimeout(constants.Scanning.TIMEOUT_CONNECT)
            self.sock.connect((IP, PORT))
            self.sock.settimeout(constants.Scanning.TIMEOUT_DATA)
            self.sock.sendall(commandJSON.encode(encoding='ascii', errors="ignore"))
            self.connectionFail = False
        except Exception as e:
            print('connection error', e)
            self.connectionFail = True
            self.sock = 0
            return False

        try:
            data=''
            data = self.sock.recv(constants.Protocol.FILE_BUFFER_SIZE).decode()
            print(data)
        except Exception as e:
            print('ERROR pingScanner', e)
        finally:
            try:
                self.sock.shutdown(socket.SHUT_WR)
                check = self.sock.recv(constants.Protocol.FILE_BUFFER_SIZE)
                while (check):
                    check = self.sock.recv(constants.Protocol.FILE_BUFFER_SIZE)
                self.sock.close()
            except Exception as e:
                print('ERROR: gracefullClose ', e)
        return data

    def sendCameraSyncInfo(self, clockPi1, captureTimePi1):
        # Both cameras are on the same machine; update the constant directly.
        self._syncCameraLocally(clockPi1, captureTimePi1)
        return True

    def setPi2mode(self, PI2_MODE, EXPOSURE_TIME_SCAN=None, EXPOSURE_TIME_CALIB=None, IMAGE_NUMBER=None, idealCaptureTimeMinPi1=None, PLATE_NUMBER=None, SHOT_NUMBER=None, CAPTURE_TIME_LIST=None, SCAN_IMAGE_LIST=None, RETRY=None, IMAGE_ORDER=None, PROJ_ERROR_LIST=None, SCAN_ID=None):#'scan', 'calib', 'reset'
        CMD_ID=str(uuid.uuid4())
        commandDict={ "header":constants.Protocol.HEADER,
                      "command":constants.Protocol.CMD_SET_PI2_MODE,
                      "PI2_MODE":PI2_MODE,
                      "CMD_ID": CMD_ID}
        if EXPOSURE_TIME_SCAN is not None:
            commandDict["EXPOSURE_TIME_SCAN"]=EXPOSURE_TIME_SCAN
        if EXPOSURE_TIME_CALIB is not None:
            commandDict["EXPOSURE_TIME_CALIB"] = EXPOSURE_TIME_CALIB
        if IMAGE_NUMBER is not None:
            commandDict["IMAGE_NUMBER"] = IMAGE_NUMBER
        if idealCaptureTimeMinPi1 is not None:
            commandDict["idealCaptureTimeMinPi1"] = idealCaptureTimeMinPi1
        if PLATE_NUMBER is not None:
            commandDict["PLATE_NUMBER"] = PLATE_NUMBER
        if SHOT_NUMBER is not None:
            commandDict["SHOT_NUMBER"] = SHOT_NUMBER
        if CAPTURE_TIME_LIST is not None:
            commandDict["CAPTURE_TIME_LIST"] = CAPTURE_TIME_LIST
        if SCAN_IMAGE_LIST is not None:
            commandDict["SCAN_IMAGE_LIST"] = SCAN_IMAGE_LIST
        if RETRY is not None:
            commandDict["RETRY"] = RETRY
        commandDict["IMAGE_ORDER"] = IMAGE_ORDER
        if PROJ_ERROR_LIST is not None:
            commandDict["PROJ_ERROR_LIST"] = PROJ_ERROR_LIST
        if SCAN_ID is not None:
            commandDict["SCAN_ID"] = SCAN_ID

        # Dispatch directly in-process to the local ScanSlave instance.
        self._dispatchPi2ModeLocally(commandDict)
        return CMD_ID

    def commandDone(self, CMD_ID, msgDict={}):
        # There is no separate Pi2; the caller already handles results.
        return True


if __name__ == "__main__":
    pass
