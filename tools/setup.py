import json
import secrets
import numpy as np
# import raw  #use this to make the new noise file
import raw2 as raw  # new longer noise file
import os
import zipfile
import subprocess
import shutil

# MAX_FILE_LENGTH = 50000
MAX_FILE_LENGTH = 500000

# NOTES
# up to serial 106 uses noise in raw.py : has capacity for ~150 units
# so v2.07 on will use raw2.py which will take ~1500 units - actually it works fine for more than this but the noise repeats in a loop.
# don't update v2.06 with resource from v2.07 else it may crash - but this should never be needed.
# raw2 will end the same as raw.py (noise is read from end to start), so old v2.06 resource will work on v2p07 - so upgrade to v2p07 can work on older machines without resource update.

class setup():
    # variable shared over all classes
    def __init__(self):
        # variable for this instance - self..

        self.setupList=[]
        #BLANK*********************
        self.setupList.append({"SERIAL": '00000',
                           "SERIAL_PI1": '',  # CPU serial on pi USED
                           "SERIAL_PI2": '',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": '',  # unused
                           "MAC_PI2": '',
                           "PROJ_MODEL": 'C6_V2',
                           "LEVELLER": 'MARKER',
                           "LENSES": '3mm',
                            "TYPE": 'BSB',  ##BSB, DENTAL, GP
                            "WIFI_READY":'N',  #Y,N - Y if sd card is set up for it or N if old card.
                            "CODE": '0'})  #license code, e.g. bit 0 set 0.  Bit 1 is Dental, 0 no, 1 yes.  Bit 2 GP, bit 3 metal holders ... So Dental(2) + GP(4) + Metal(8) =  14
        #BLANK**********************

        self.setupList.append({"SERIAL": '00001',
                          "SERIAL_PI1": '0',  # CPU serial on pi USED
                          "SERIAL_PI2": '0',  # CPU serial on pi USED
                          "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                          "BT_MAC_PROJ": '22:22:03:D8:6D:99',  # Needed by pi1
                          "CIRCLE_PITCH": '6.0000', #mm needed by pi1 and pi2 originaly 5.95577
                          "IP_PI1": '',
                          "IP_PI2": '',
                          "BT_MAC_PI1": '',  #  Needed by proj
                          "BT_MAC_PI2": '',  #  unused
                          "MAC_PI1": '',  #  unused
                          "MAC_PI2": ''})  #  unused


        self.setupList.append({"SERIAL": '00002',#Cory's scanner, shipped with the measured at 5.95577mm calib plate
                          "SERIAL_PI1": '0000000002c2c5a8',  # CPU serial on pi  USED
                          "SERIAL_PI2": '???',  # CPU serial on pi USED
                          "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                          "BT_MAC_PROJ": '22:22:98:09:70:06',  # Needed by pi1
                          "CIRCLE_PITCH": '6.000',  # mm
                          "IP_PI1": '169.254.59.237',
                          "IP_PI2": '169.254.145.169',
                          "BT_MAC_PI1": 'B8:27:EB:68:6F:02',  #  Needed by proj
                          "BT_MAC_PI2": '',  #  unused
                          "MAC_PI1": 'B8:27:EB:C2:C5:A8',  #  unused
                          "MAC_PI2": ''})  #  unused

        self.setupList.append({"SERIAL": '00003',#Candidate release, my version, with v2 circuit and bigger vertical motor, and 2 new pis. Required standard IP to be changed.
                          "SERIAL_PI1": '000000007008de8f',  # CPU serial on pi USED
                          "SERIAL_PI2": '0000000009984b02',  # CPU serial on pi USED
                          "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                          "BT_MAC_PROJ": '22:22:D9:93:76:3C',  # Needed by pi1
                          "CIRCLE_PITCH": '6.000',  # mm
                          "IP_PI1": '169.254.30.155',
                          "IP_PI2": '169.254.71.46',
                          "BT_MAC_PI1": 'B8:27:EB:A2:74:25',  #  Needed by proj
                          "BT_MAC_PI2": 'B8:27:EB:32:E1:A8',  #  unused
                          "MAC_PI1": 'b8:27:eb:08:de:8f',  #  unused
                          "MAC_PI2": 'b8:27:eb:98:4b:02'})  #  unused

        self.setupList.append({"SERIAL": '00004',
                          "SERIAL_PI1": '00000000fe1e2fb4',  # CPU serial on pi USED
                          "SERIAL_PI2": '00000000d5d876b4',  # CPU serial on pi USED
                          "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                          "BT_MAC_PROJ": '22:22:91:8E:C5:EB',  # Needed by pi1
                          "CIRCLE_PITCH": '6.000',  # mm
                          "IP_PI1": '169.254.30.155',
                          "IP_PI2": '169.254.71.46',
                          "BT_MAC_PI1": 'B8:27:EB:B4:85:1E',  #  Needed by proj
                          "BT_MAC_PI2": 'B8:27:EB:72:DC:1E',  #  unused
                          "MAC_PI1": 'b8:27:eb:1e:2f:b4',  #  unused
                          "MAC_PI2": 'b8:27:eb:d8:76:b4'})  #  unused

        self.setupList.append({"SERIAL": '00005',#sent to cory with rc1b (slow motor update), 11th June 2019, ce marked.
                          "SERIAL_PI1": '00000000ddb3610c',  # CPU serial on pi USED
                          "SERIAL_PI2": '0000000099fe5e00',  # CPU serial on pi USED
                          "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                          "BT_MAC_PROJ": '22:22:BB:9A:A5:3E',  # Needed by pi1
                          "CIRCLE_PITCH": '6.000',  # mm
                          "IP_PI1": '169.254.30.155',
                          "IP_PI2": '169.254.71.46',
                          "BT_MAC_PI1": 'B8:27:EB:19:CB:A6',  #  Needed by proj
                          "BT_MAC_PI2": 'B8:27:EB:54:F4:AA',  #  unused
                          "MAC_PI1": 'b8:27:eb:b3:61:0c',  #  unused
                          "MAC_PI2": 'b8:27:eb:fe:5e:00'})  #  unused

        self.setupList.append({"SERIAL": '00006',
                           "SERIAL_PI1": '00000000e95a4242',  # CPU serial on pi USED
                           "SERIAL_PI2": '00000000c037a3fd',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '22:22:72:B4:1E:27',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'B8:27:EB:F0:E8:E8',  # Needed by proj
                           "BT_MAC_PI2": 'B8:27:EB:9D:09:57',  # unused
                           "MAC_PI1": 'b8:27:eb:5a:42:42',  # unused
                           "MAC_PI2": 'b8:27:eb:37:a3:fd'})  # unused

        self.setupList.append({"SERIAL": '00007',
                           "SERIAL_PI1": '00000000291c0c6a',  # CPU serial on pi USED
                           "SERIAL_PI2": '000000007913d009',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '22:22:AF:26:B2:07',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'B8:27:EB:B6:A6:C0',  # Needed by proj
                           "BT_MAC_PI2": 'B8:27:EB:B9:7A:A3',  # unused
                           "MAC_PI1": 'b8:27:eb:1c:0c:6a',  # unused
                           "MAC_PI2": 'b8:27:eb:13:d0:09'})  # unused

        self.setupList.append({"SERIAL": '00008',#shipped to cory rc1
                           "SERIAL_PI1": '00000000699b778a',  # CPU serial on pi USED
                           "SERIAL_PI2": '000000001cc042b2',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '22:22:8B:DA:FB:5A',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'B8:27:EB:31:DD:20',  # Needed by proj
                           "BT_MAC_PI2": 'B8:27:EB:6A:E8:18',  # unused
                           "MAC_PI1": 'b8:27:eb:9b:77:8a',  # unused
                           "MAC_PI2": 'b8:27:eb:c0:42:b2'})  # unused

        self.setupList.append({"SERIAL": '00009',
                           "SERIAL_PI1": '0000000062a1d76e',  # CPU serial on pi USED
                           "SERIAL_PI2": '00000000a936ea09',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '22:22:7C:03:96:50',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'B8:27:EB:0B:7D:C4',  # Needed by proj
                           "BT_MAC_PI2": 'B8:27:EB:9C:40:A3',  # unused
                           "MAC_PI1": 'b8:27:eb:a1:d7:6e',  # unused
                           "MAC_PI2": 'b8:27:eb:36:ea:09'})  # unused

        self.setupList.append({"SERIAL": '00010',
                           "SERIAL_PI1": '000000007331f51b',  # CPU serial on pi USED
                           "SERIAL_PI2": '0000000088482366',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '22:22:5D:2D:09:CE',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'B8:27:EB:9B:5F:B1',  # Needed by proj
                           "BT_MAC_PI2": 'B8:27:EB:E2:89:CC',  # unused
                           "MAC_PI1": 'b8:27:eb:31:f5:1b',  # unused
                           "MAC_PI2": 'b8:27:eb:48:23:66'})  # unused

        self.setupList.append({"SERIAL": '00011',
                           "SERIAL_PI1": '00000000cd9c8d39',  # CPU serial on pi USED
                           "SERIAL_PI2": '00000000a048abc7',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '22:22:4C:3F:61:95',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'B8:27:EB:36:27:93',  # Needed by proj
                           "BT_MAC_PI2": 'B8:27:EB:E2:01:6D',  # unused
                           "MAC_PI1": 'b8:27:eb:9c:8d:39',  # unused
                           "MAC_PI2": 'b8:27:eb:48:ab:c7'})  # unused

        self.setupList.append({"SERIAL": '00012',
                           "SERIAL_PI1": '00000000ddd7907e',  # CPU serial on pi USED
                           "SERIAL_PI2": '0000000056e4bfa3',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '22:22:0B:0E:D2:36',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'B8:27:EB:7D:3A:D4',  # Needed by proj
                           "BT_MAC_PI2": 'B8:27:EB:4E:15:09',  # unused
                           "MAC_PI1": 'b8:27:eb:d7:90:7e',  # unused
                           "MAC_PI2": 'b8:27:eb:e4:bf:a3'})  # unused

        self.setupList.append({"SERIAL": '00013',
                           "SERIAL_PI1": '000000003ea1a9f6',  # CPU serial on pi USED
                           "SERIAL_PI2": '000000000f0e8b80',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '22:22:34:37:63:3D',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'B8:27:EB:0B:03:5C',  # Needed by proj
                           "BT_MAC_PI2": 'B8:27:EB:A4:21:2A',  # unused
                           "MAC_PI1": 'b8:27:eb:a1:a9:f6',  # unused
                           "MAC_PI2": '27:eb:0e:8b:80'})  # unused

        self.setupList.append({"SERIAL": '00014',
                           "SERIAL_PI1": '00000000f1dfa0a7',  # CPU serial on pi USED
                           "SERIAL_PI2": '00000000334fca22',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '22:22:59:35:C9:1D',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'B8:27:EB:75:0A:0D',  # Needed by proj
                           "BT_MAC_PI2": 'B8:27:EB:E5:60:88',  # unused
                           "MAC_PI1": 'b8:27:eb:df:a0:a7',  # unused
                           "MAC_PI2": 'b8:27:eb:4f:ca:22'})  # unused

        self.setupList.append({"SERIAL": '00015',
                           "SERIAL_PI1": '00000000aa5901cb',  # CPU serial on pi USED
                           "SERIAL_PI2": '00000000e0f51e5d',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '22:22:B9:99:DF:C6',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'B8:27:EB:F3:AB:61',  # Needed by proj
                           "BT_MAC_PI2": 'B8:27:EB:5F:B4:F7',  # unused
                           "MAC_PI1": 'b8:27:eb:59:01:cb',  # unused
                           "MAC_PI2": 'b8:27:eb:f5:1e:5d'})  # unused

        self.setupList.append({"SERIAL": '00016',
                           "SERIAL_PI1": '000000004cb406a8',  # CPU serial on pi USED
                           "SERIAL_PI2": '00000000a65dbb36',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '22:22:72:B4:1E:27',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'B8:27:EB:1E:AC:02',  # Needed by proj
                           "BT_MAC_PI2": 'B8:27:EB:F7:11:9C',  # unused
                           "MAC_PI1": 'b8:27:eb:b4:06:a8',  # unused
                           "MAC_PI2": 'b8:27:eb:5d:bb:36'})  # unused

        self.setupList.append({"SERIAL": '00017',
                           "SERIAL_PI1": '00000000d3e024a3',  # CPU serial on pi USED
                           "SERIAL_PI2": '0000000080d19322',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '22:22:B8:F9:22:EB',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'B8:27:EB:4A:8E:09',  # Needed by proj
                           "BT_MAC_PI2": 'B8:27:EB:7B:39:88',  # unused
                           "MAC_PI1": 'b8:27:eb:e0:24:a3',  # unused
                           "MAC_PI2": 'b8:27:eb:d1:93:22'})  # unused

        self.setupList.append({"SERIAL": '00018',
                           "SERIAL_PI1": '000000007e6cb63e',  # CPU serial on pi USED
                           "SERIAL_PI2": '0000000044d89e36',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '22:22:B4:0F:82:CA',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'B8:27:EB:C6:1C:94',  # Needed by proj
                           "BT_MAC_PI2": 'B8:27:EB:72:34:9C',  # unused
                           "MAC_PI1": 'b8:27:eb:6c:b6:3e',  # unused
                           "MAC_PI2": 'b8:27:eb:d8:9e:36'})  # unused

        self.setupList.append({"SERIAL": '00019',
                           "SERIAL_PI1": '00000000c3998eb9',  # CPU serial on pi USED
                           "SERIAL_PI2": '000000009a168cbf',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '22:22:0B:76:82:EC',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'B8:27:EB:33:24:13',  # Needed by proj
                           "BT_MAC_PI2": 'B8:27:EB:BC:26:15',  # unused
                           "MAC_PI1": 'b8:27:eb:99:8e:b9',  # unused
                           "MAC_PI2": 'b8:27:eb:16:8c:bf'})  # unused

        self.setupList.append({"SERIAL": '00020',
                           "SERIAL_PI1": '00000000ff53840b',  # CPU serial on pi USED
                           "SERIAL_PI2": '000000000981887b',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '22:22:0B:DE:31:A3',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'B8:27:EB:F9:2E:A1',  # Needed by proj
                           "BT_MAC_PI2": 'B8:27:EB:2B:22:D1',  # unused
                           "MAC_PI1": 'b8:27:eb:53:84:0b',  # unused
                           "MAC_PI2": 'b8:27:eb:81:88:7b'})  # unused

        self.setupList.append({"SERIAL": '00021',
                           "SERIAL_PI1": '00000000c64ce271',  # CPU serial on pi USED
                           "SERIAL_PI2": '00000000ec91513e',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           #"BT_MAC_PROJ": '22:22:10:31:20:37',  # Needed by pi1 - proj suspected faulty, so switched to proj 0001
                           "BT_MAC_PROJ": '22:22:03:D8:6D:99',#proj 0001
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'B8:27:EB:E6:48:DB',  # Needed by proj
                           "BT_MAC_PI2": 'B8:27:EB:3B:FB:94',  # unused
                           "MAC_PI1": 'b8:27:eb:4c:e2:71',  # unused
                           "MAC_PI2": 'b8:27:eb:91:51:3e'})  # unused

        self.setupList.append({"SERIAL": '00022',
                           "SERIAL_PI1": '000000003151a1cd',  # CPU serial on pi USED
                           "SERIAL_PI2": '0000000089e206cf',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '22:22:80:15:9C:9A',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'B8:27:EB:FB:0B:67',  # Needed by proj
                           "BT_MAC_PI2": 'B8:27:EB:48:AC:65',  # unused
                           "MAC_PI1": 'b8:27:eb:51:a1:cd',  # unused
                           "MAC_PI2": 'b8:27:eb:e2:06:cf'})  # unused

        self.setupList.append({"SERIAL": '00023',
                           "SERIAL_PI1": '00000000f59f71fe',  # CPU serial on pi USED
                           "SERIAL_PI2": '00000000208e6ad0',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '22:22:FE:47:0C:41',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'B8:27:EB:35:DB:54',  # Needed by proj
                           "BT_MAC_PI2": 'B8:27:EB:24:C0:7A',  # unused
                           "MAC_PI1": 'b8:27:eb:9f:71:fe',  # unused
                           "MAC_PI2": 'b8:27:eb:8e:6a:d0'})  # unused

        self.setupList.append({"SERIAL": '00024',
                           "SERIAL_PI1": '000000003e661613',  # CPU serial on pi USED
                           "SERIAL_PI2": '000000003fbfb1b7',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '22:22:E3:A2:A5:D7',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'B8:27:EB:CC:BC:B9',  # Needed by proj
                           "BT_MAC_PI2": 'B8:27:EB:15:1B:1D',  # unused
                           "MAC_PI1": 'b8:27:eb:66:16:13',  # unused
                           "MAC_PI2": 'b8:27:eb:bf:b1:b7'})  # unused

        self.setupList.append({"SERIAL": '00025',
                           "SERIAL_PI1": '00000000e77e6d26',  # CPU serial on pi USED
                           "SERIAL_PI2": '000000002e19574c',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           #"BT_MAC_PROJ": '22:22:D8:F3:BA:61',  # Needed by pi1
                           "BT_MAC_PROJ": '22:22:40:A2:71:E4',  # Needed by pi1 - changed to this after factory reset (which I did because of BT failing 50% time).
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'B8:27:EB:D4:C7:8C',  # Needed by proj
                           "BT_MAC_PI2": 'B8:27:EB:B3:FD:E6',  # unused
                           "MAC_PI1": 'b8:27:eb:7e:6d:26',  # unused
                           "MAC_PI2": 'b8:27:eb:19:57:4c'})  # unused

        self.setupList.append({"SERIAL": '00026',#version 2 development model
                           #"SERIAL_PI1": '10000000f1133d21',  # CPU serial on pi USED
                           "SERIAL_PI1": '1000000071c6b210',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000e8431194',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '22:22:E3:A2:A5:D7',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'DC:A6:32:09:55:F8',  # Needed by proj
                           "BT_MAC_PI2": 'DC:A6:32:09:55:AA',  # unused
                           "MAC_PI1": 'dc:a6:32:09:55:f6',  # unused
                           "MAC_PI2": 'dc:a6:32:09:55:a8'})  # unused

        self.setupList.append({"SERIAL": '00027', #VERSION 2 FROM NOW
                           "SERIAL_PI1": '1000000051622aba',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000d50be41c',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # unused
                           "BT_MAC_PROJ": '22:22:E3:A2:A5:D7',  # unused
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'DC:A6:32:09:55:F8',  # unused
                           "BT_MAC_PI2": 'DC:A6:32:09:55:AA',  # unused
                           "MAC_PI1": 'dc:a6:32:09:55:f6',  # unused
                           "MAC_PI2": 'dc:a6:32:09:55:a8'})  # unused

        self.setupList.append({"SERIAL": '00028',
                           "SERIAL_PI1": '100000009c7c45a7',  # CPU serial on pi USED
                           "SERIAL_PI2": '100000002e2a1470',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # unused
                           "BT_MAC_PROJ": '22:22:E3:A2:A5:D7',  # unused
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'DC:A6:32:09:55:F8',  # unused
                           "BT_MAC_PI2": 'DC:A6:32:09:55:AA',  # unused
                           "MAC_PI1": 'dc:a6:32:27:36:fc',  # unused
                           "MAC_PI2": 'dc:a6:32:27:37:3f'})  # unused

        self.setupList.append({"SERIAL": '00029',
                           "SERIAL_PI1": '10000000f9ef4615',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000b224eff3',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # unused
                           "BT_MAC_PROJ": '22:22:E3:A2:A5:D7',  # unused
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'DC:A6:32:09:55:F8',  # unused
                           "BT_MAC_PI2": 'DC:A6:32:09:55:AA',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:5b:a8',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:54:00'})  # unused

        self.setupList.append({"SERIAL": '00030',
                           "SERIAL_PI1": '10000000b5168ae7',  # CPU serial on pi USED
                           "SERIAL_PI2": '100000002144d441',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # unused
                           "BT_MAC_PROJ": '22:22:E3:A2:A5:D7',  # unused
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'DC:A6:32:09:55:F8',  # unused
                           "BT_MAC_PI2": 'DC:A6:32:09:55:AA',  # unused
                           "MAC_PI1": 'dc:a6:32:27:37:53',  # unused
                           "MAC_PI2": 'dc:a6:32:27:12:ab'})  # unused

        self.setupList.append({"SERIAL": '00031',
                           "SERIAL_PI1": '1000000022fb8109',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000e136e7d4',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # unused
                           "BT_MAC_PROJ": '22:22:E3:A2:A5:D7',  # unused
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'DC:A6:32:09:55:F8',  # unused
                           "BT_MAC_PI2": 'DC:A6:32:09:55:AA',  # unused
                           "MAC_PI1": 'dc:a6:32:27:37:77',  # unused
                           "MAC_PI2": 'dc:a6:32:27:36:81'})  # unused

        self.setupList.append({"SERIAL": '00032',
                           "SERIAL_PI1": '100000001c82f47d',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000592e9089',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # unused
                           "BT_MAC_PROJ": '22:22:E3:A2:A5:D7',  # unused
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'DC:A6:32:09:55:F8',  # unused
                           "BT_MAC_PI2": 'DC:A6:32:09:55:AA',  # unused
                           "MAC_PI1": 'dc:a6:32:27:37:7a',  # unused
                           "MAC_PI2": 'dc:a6:32:26:f3:4e'})  # unused

        self.setupList.append({"SERIAL": '00033',
                           "SERIAL_PI1": '100000006b8a3a79',  # CPU serial on pi USED
                           "SERIAL_PI2": '100000004afef440',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # unused
                           "BT_MAC_PROJ": '22:22:E3:A2:A5:D7',  # unused
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'DC:A6:32:09:55:F8',  # unused
                           "BT_MAC_PI2": 'DC:A6:32:09:55:AA',  # unused
                           "MAC_PI1": 'dc:a6:32:27:36:72',  # unused
                           "MAC_PI2": 'dc:a6:32:27:36:cf'})  # unused

        self.setupList.append({"SERIAL": '00034',
                           'SERIAL_PI1': '100000002c3ffdba',
                           'SERIAL_PI2': '100000002c2fb47a',
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # unused
                           "BT_MAC_PROJ": '22:22:E3:A2:A5:D7',  # unused
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           'BT_MAC_PI1': '',
                           'BT_MAC_PI2': '',
                           'MAC_PI1': 'e4:5f:01:ce:4f:eb',
                           'MAC_PI2': 'e4:5f:01:ce:4f:f4',
                           'PROJ_MODEL': 'C6',
                           'LEVELLER': 'MARKER',
                           'LENSES': '3mm',
                           'TYPE': 'DENTAL',
                           'WIFI_READY': 'Y',
                           'CODE': '7'})

        self.setupList.append({"SERIAL": '00035',
                           "SERIAL_PI1": '10000000a3323312',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000a6b07b10',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # unused
                           "BT_MAC_PROJ": '22:22:E3:A2:A5:D7',  # unused
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": 'DC:A6:32:09:55:F8',  # unused
                           "BT_MAC_PI2": 'DC:A6:32:09:55:AA',  # unused
                           "MAC_PI1": 'dc:a6:32:27:36:92',  # unused
                           "MAC_PI2": 'dc:a6:32:27:16:59'})  # unused

        self.setupList.append({"SERIAL": '00036',
                           "SERIAL_PI1": '10000000a326730c',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000fee5dd80',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:75:8b',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:75:eb'})  # unused

        self.setupList.append({"SERIAL": '00037',
                           "SERIAL_PI1": '10000000e3520287',  # CPU serial on pi USED
                           "SERIAL_PI2": '100000005ac3f2db',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:75:35',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:75:f7'})  # unused

        self.setupList.append({"SERIAL": '00038',
                           "SERIAL_PI1": '10000000cc0a5bda',  # CPU serial on pi USED
                           "SERIAL_PI2": '100000006f24e907',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:76:09',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:76:b0'})  # unused

        self.setupList.append({"SERIAL": '00039',
                           "SERIAL_PI1": '10000000da7020c9',  # CPU serial on pi USED
                           "SERIAL_PI2": '100000009bea0d7f',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:75:b0',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:49:dc'})  # unused

        # self.setupList.append({"SERIAL": '00040',
        #                    "SERIAL_PI1": '100000009f525112',  # CPU serial on pi USED
        #                    "SERIAL_PI2": '10000000f0b2b964',  # CPU serial on pi USED
        #                    "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
        #                    "BT_MAC_PROJ": '',  # Needed by pi1
        #                    "CIRCLE_PITCH": '6.000',  # mm
        #                    "IP_PI1": '169.254.30.155',
        #                    "IP_PI2": '169.254.71.46',
        #                    "BT_MAC_PI1": '',  # Needed by proj
        #                    "BT_MAC_PI2": '',  # unused
        #                    "MAC_PI1": 'dc:a6:32:0d:75:9b',  # unused
        #                    "MAC_PI2": 'dc:a6:32:0d:76:4b'})  # unused


        self.setupList.append({'SERIAL': '00040',
                               'SERIAL_PI1': '100000009f525112',
                               'SERIAL_PI2': '10000000f0b2b964',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:0d:75:9b',
                               'MAC_PI2': 'dc:a6:32:0d:76:4b',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'GP',
                               'WIFI_READY': 'Y'})

        self.setupList.append({"SERIAL": '00041',
                           "SERIAL_PI1": '100000005874c4d2',  # CPU serial on pi USED
                           "SERIAL_PI2": '100000007cb7ec92',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:48:cd',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:78:06'})  # unused

        self.setupList.append({"SERIAL": '00042',
                           "SERIAL_PI1": '10000000555dd6e5',  # CPU serial on pi USED
                           "SERIAL_PI2": '100000006284b3bc',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:77:06',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:4a:1e',
                           'PROJ_MODEL': 'C6',
                           'LEVELLER': 'ARD',
                           'LENSES': '6mm',
                           'TYPE': 'DENTAL',
                           'WIFI_READY': 'Y'})

        self.setupList.append({"SERIAL": '00043',
                           "SERIAL_PI1": '1000000006d6134f',  # CPU serial on pi USED
                           "SERIAL_PI2": '100000006901c2ec',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:66:b5',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:66:82'})  # unused

        self.setupList.append({"SERIAL": '00044',
                           "SERIAL_PI1": '10000000300eebfc',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000d0e51619',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:75:ee',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:75:4d'})  # unused

        self.setupList.append({"SERIAL": '00045',
                           "SERIAL_PI1": '1000000089f019f8',  # CPU serial on pi USED
                           "SERIAL_PI2": '1000000005f4a0d1',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:27:36:ed',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:74:64'})  # unused

        self.setupList.append({"SERIAL": '00046',
                           "SERIAL_PI1": '100000007f345879',  # CPU serial on pi USED
                           "SERIAL_PI2": '1000000051a3f3bd',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:74:f3',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:75:fa'})  # unused

        self.setupList.append({"SERIAL": '00047',
                           "SERIAL_PI1": '10000000049e22e7',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000bb3addd7',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:76:45',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:77:0a'})  # unused

        self.setupList.append({"SERIAL": '00048',
                           "SERIAL_PI1": '100000001a1e6caa',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000d7ce2989',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:75:ce',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:77:94'})  # unused

        self.setupList.append({"SERIAL": '00049',
                           "SERIAL_PI1": '10000000181cf25d',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000bcbd2a8c',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:4a:92',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:4a:d4'})  # unused

        self.setupList.append({"SERIAL": '00050',
                           "SERIAL_PI1": '1000000042a5fff4',  # CPU serial on pi USED
                           "SERIAL_PI2": '100000005d00fa58',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:75:68',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:74:36'})  # unused

        self.setupList.append({"SERIAL": '00051',
                           "SERIAL_PI1": '10000000938e30a6',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000e7a13972',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:49:ff',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:75:b9'})  # unused

        self.setupList.append({"SERIAL": '00052',
                           "SERIAL_PI1": '10000000e81d3e52',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000975c2ead',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:77:d0',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:77:91'})  # unused

        self.setupList.append({"SERIAL": '00053',
                           "SERIAL_PI1": '10000000447ed13a',  # CPU serial on pi USED
                           "SERIAL_PI2": '1000000098e65b08',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:76:ec',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:76:3f'})  # unused

        self.setupList.append({"SERIAL": '00054',
                           "SERIAL_PI1": '1000000001e474be',  # CPU serial on pi USED
                           "SERIAL_PI2": '100000007607c7bd',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:27:0d:a9',  # unused
                           "MAC_PI2": 'dc:a6:32:27:36:24'})  # unused

        self.setupList.append({"SERIAL": '00055',
                           "SERIAL_PI1": '100000002f205f25',  # CPU serial on pi USED
                           "SERIAL_PI2": '1000000080f2112e',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:27:36:ba',  # unused
                           "MAC_PI2": 'dc:a6:32:27:37:1d'})  # unused


        self.setupList.append({"SERIAL": '00056',
                           "SERIAL_PI1": '100000009c1590b5',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000896a449d',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:76:68',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:48:9c'})  # unused

        self.setupList.append({"SERIAL": '00057',
                           "SERIAL_PI1": '10000000a71a2aff',  # CPU serial on pi USED
                           "SERIAL_PI2": '1000000081122d7a',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:77:30',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:76:36'})  # unused

        self.setupList.append({"SERIAL": '00058',
                           "SERIAL_PI1": '10000000d6d6f18a',  # CPU serial on pi USED
                           "SERIAL_PI2": '100000006e509348',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:74:a9',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:73:ca'})  # unused

        self.setupList.append({"SERIAL": '00059',
                           "SERIAL_PI1": '100000000cf6a567',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000c6452e91',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:74:2c',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:74:c1'})  # unused

        self.setupList.append({"SERIAL": '00060',
                           "SERIAL_PI1": '10000000c52b6db5',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000f4c16445',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:76:79',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:2c:89'})  # unused

        self.setupList.append({"SERIAL": '00061',
                           "SERIAL_PI1": '10000000121840da',  # CPU serial on pi USED
                           "SERIAL_PI2": '100000004e6296aa',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:55:85',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:74:76'})  # unused

        self.setupList.append({"SERIAL": '00062',
                               "SERIAL_PI1": '1000000051d361a0',  # CPU serial on pi USED
                               "SERIAL_PI2": '1000000020d3ddb7',  # CPU serial on pi USED
                               "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                               "BT_MAC_PROJ": '',  # Needed by pi1
                               "CIRCLE_PITCH": '6.000',  # mm
                               "IP_PI1": '169.254.30.155',
                               "IP_PI2": '169.254.71.46',
                               "BT_MAC_PI1": '',  # Needed by proj
                               "BT_MAC_PI2": '',  # unused
                               "MAC_PI1": 'dc:a6:32:0d:66:1a',  # unused
                               "MAC_PI2": 'dc:a6:32:0d:75:a1'})  # unused

        self.setupList.append({"SERIAL": '00063',
                               "SERIAL_PI1": '10000000c793e784',  # CPU serial on pi USED
                               "SERIAL_PI2": '10000000cbe85ff4',  # CPU serial on pi USED
                               "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                               "BT_MAC_PROJ": '',  # Needed by pi1
                               "CIRCLE_PITCH": '6.000',  # mm
                               "IP_PI1": '169.254.30.155',
                               "IP_PI2": '169.254.71.46',
                               "BT_MAC_PI1": '',  # Needed by proj
                               "BT_MAC_PI2": '',  # unused
                               "MAC_PI1": 'dc:a6:32:0d:74:43',  # unused
                               "MAC_PI2": 'dc:a6:32:0d:75:01'})  # unused

        self.setupList.append({"SERIAL": '00064',
                               "SERIAL_PI1": '10000000b82d53df',  # CPU serial on pi USED
                               "SERIAL_PI2": '1000000026a96fc3',  # CPU serial on pi USED
                               "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                               "BT_MAC_PROJ": '',  # Needed by pi1
                               "CIRCLE_PITCH": '6.000',  # mm
                               "IP_PI1": '169.254.30.155',
                               "IP_PI2": '169.254.71.46',
                               "BT_MAC_PI1": '',  # Needed by proj
                               "BT_MAC_PI2": '',  # unused
                               "MAC_PI1": 'dc:a6:32:0d:66:61',  # unused
                               "MAC_PI2": 'dc:a6:32:0d:73:f1'})  # unused

        self.setupList.append({"SERIAL": '00065',
                               "SERIAL_PI1": '10000000222ec446',  # CPU serial on pi USED
                               "SERIAL_PI2": '100000009e544ccb',  # CPU serial on pi USED
                               "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                               "BT_MAC_PROJ": '',  # Needed by pi1
                               "CIRCLE_PITCH": '6.000',  # mm
                               "IP_PI1": '169.254.30.155',
                               "IP_PI2": '169.254.71.46',
                               "BT_MAC_PI1": '',  # Needed by proj
                               "BT_MAC_PI2": '',  # unused
                               "MAC_PI1": 'dc:a6:32:0d:75:7c',  # unused
                               "MAC_PI2": 'dc:a6:32:0d:74:af'})  # unused

        self.setupList.append({"SERIAL": '00066',
                               "SERIAL_PI1": '100000001a5c47a9',  # CPU serial on pi USED
                               "SERIAL_PI2": '10000000e0e41ace',  # CPU serial on pi USED
                               "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                               "BT_MAC_PROJ": '',  # Needed by pi1
                               "CIRCLE_PITCH": '6.000',  # mm
                               "IP_PI1": '169.254.30.155',
                               "IP_PI2": '169.254.71.46',
                               "BT_MAC_PI1": '',  # Needed by proj
                               "BT_MAC_PI2": '',  # unused
                               "MAC_PI1": 'dc:a6:32:0d:74:d3',  # unused
                               "MAC_PI2": 'dc:a6:32:0d:2c:6e'})  # unused

        self.setupList.append({"SERIAL": '00067',
                               "SERIAL_PI1": '10000000278d5b0a',  # CPU serial on pi USED
                               "SERIAL_PI2": '10000000a03706ce',  # CPU serial on pi USED
                               "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                               "BT_MAC_PROJ": '',  # Needed by pi1
                               "CIRCLE_PITCH": '6.000',  # mm
                               "IP_PI1": '169.254.30.155',
                               "IP_PI2": '169.254.71.46',
                               "BT_MAC_PI1": '',  # Needed by proj
                               "BT_MAC_PI2": '',  # unused
                               "MAC_PI1": 'dc:a6:32:0d:77:19',  # unused
                               "MAC_PI2": 'dc:a6:32:0d:75:d2'})  # unused

        self.setupList.append({"SERIAL": '00068',
                               'SERIAL_PI1': '10000000b309af39',
                               'SERIAL_PI2': '1000000063fb152f',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:3d:e1:fe',
                               'MAC_PI2': 'dc:a6:32:37:a4:15'})

        self.setupList.append({"SERIAL": '00069',
                               "SERIAL_PI1": '10000000ea4353ed',  # CPU serial on pi USED
                               "SERIAL_PI2": '100000001b8ea0e2',  # CPU serial on pi USED
                               "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                               "BT_MAC_PROJ": '',  # Needed by pi1
                               "CIRCLE_PITCH": '6.000',  # mm
                               "IP_PI1": '169.254.30.155',
                               "IP_PI2": '169.254.71.46',
                               "BT_MAC_PI1": '',  # Needed by proj
                               "BT_MAC_PI2": '',  # unused
                               "MAC_PI1": 'dc:a6:32:0d:75:26',  # unused
                               "MAC_PI2": 'dc:a6:32:0d:74:bb'})  # unused

        self.setupList.append({"SERIAL": '00070',
                               "SERIAL_PI1": '100000005d0da8b3',  # CPU serial on pi USED
                               "SERIAL_PI2": '100000004e310f06',  # CPU serial on pi USED
                               "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                               "BT_MAC_PROJ": '',  # Needed by pi1
                               "CIRCLE_PITCH": '6.000',  # mm
                               "IP_PI1": '169.254.30.155',
                               "IP_PI2": '169.254.71.46',
                               "BT_MAC_PI1": '',  # Needed by proj
                               "BT_MAC_PI2": '',  # unused
                               "MAC_PI1": 'dc:a6:32:0d:66:70',  # unused
                               "MAC_PI2": 'dc:a6:32:0d:74:00'})  # unused

        self.setupList.append({"SERIAL": '00071',
                               "SERIAL_PI1": '10000000819f5d6f',  # CPU serial on pi USED
                               "SERIAL_PI2": '10000000a6e9e503',  # CPU serial on pi USED
                               "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                               "BT_MAC_PROJ": '',  # Needed by pi1
                               "CIRCLE_PITCH": '6.000',  # mm
                               "IP_PI1": '169.254.30.155',
                               "IP_PI2": '169.254.71.46',
                               "BT_MAC_PI1": '',  # Needed by proj
                               "BT_MAC_PI2": '',  # unused
                               "MAC_PI1": 'dc:a6:32:27:12:7f',  # unused
                               "MAC_PI2": 'dc:a6:32:27:36:9f'})  # unused

        self.setupList.append({"SERIAL": '00072',
                           "SERIAL_PI1": '10000000e0360089',  # CPU serial on pi USED
                           "SERIAL_PI2": '100000008803ea79',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:74:52',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:76:4e'})  # unused

        self.setupList.append({"SERIAL": '00073',
                           "SERIAL_PI1": '10000000754d170f',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000a0e25815',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:27:15:66',  # unused
                           "MAC_PI2": 'dc:a6:32:27:37:3e'})  # unused

        self.setupList.append({"SERIAL": '00074',
                               "SERIAL_PI1": '10000000cb01aed3',  # CPU serial on pi USED
                               "SERIAL_PI2": '1000000096869040',  # CPU serial on pi USED
                               "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                               "BT_MAC_PROJ": '',  # Needed by pi1
                               "CIRCLE_PITCH": '6.000',  # mm
                               "IP_PI1": '169.254.30.155',
                               "IP_PI2": '169.254.71.46',
                               "BT_MAC_PI1": '',  # Needed by proj
                               "BT_MAC_PI2": '',  # unused
                               "MAC_PI1": 'dc:a6:32:0d:75:3b',  # unused
                               "MAC_PI2": 'dc:a6:32:0d:74:ea'})  # unused

        self.setupList.append({"SERIAL": '00075',
                               "SERIAL_PI1": '100000005fa69f33',  # CPU serial on pi USED
                               "SERIAL_PI2": '10000000b9633c2f',  # CPU serial on pi USED
                               "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                               "BT_MAC_PROJ": '',  # Needed by pi1
                               "CIRCLE_PITCH": '6.000',  # mm
                               "IP_PI1": '169.254.30.155',
                               "IP_PI2": '169.254.71.46',
                               "BT_MAC_PI1": '',  # Needed by proj
                               "BT_MAC_PI2": '',  # unused
                               "MAC_PI1": 'dc:a6:32:0d:75:ad',  # unused
                               "MAC_PI2": 'dc:a6:32:0d:76:3c'})  # unused

        self.setupList.append({"SERIAL": '00076',
                               "SERIAL_PI1": '1000000036293a7f',  # CPU serial on pi USED
                               "SERIAL_PI2": '10000000799277d6',  # CPU serial on pi USED
                               "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                               "BT_MAC_PROJ": '',  # Needed by pi1
                               "CIRCLE_PITCH": '6.000',  # mm
                               "IP_PI1": '169.254.30.155',
                               "IP_PI2": '169.254.71.46',
                               "BT_MAC_PI1": '',  # Needed by proj
                               "BT_MAC_PI2": '',  # unused
                               "MAC_PI1": 'dc:a6:32:0d:77:e8',  # unused
                               "MAC_PI2": 'dc:a6:32:0d:75:59'})  # unused

        self.setupList.append({"SERIAL": '00077',
                               "SERIAL_PI1": '100000001df81a9f',  # CPU serial on pi USED
                               "SERIAL_PI2": '10000000c3aace32',  # CPU serial on pi USED
                               "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                               "BT_MAC_PROJ": '',  # Needed by pi1
                               "CIRCLE_PITCH": '6.000',  # mm
                               "IP_PI1": '169.254.30.155',
                               "IP_PI2": '169.254.71.46',
                               "BT_MAC_PI1": '',  # Needed by proj
                               "BT_MAC_PI2": '',  # unused
                               "MAC_PI1": 'dc:a6:32:0d:74:8e',  # unused
                               "MAC_PI2": 'dc:a6:32:0d:75:b3'})  # unused

        self.setupList.append({"SERIAL": '00078',
                               "SERIAL_PI1": '100000006c0e4333',  # CPU serial on pi USED
                               "SERIAL_PI2": '10000000c1515cd5',  # CPU serial on pi USED
                               "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                               "BT_MAC_PROJ": '',  # Needed by pi1
                               "CIRCLE_PITCH": '6.000',  # mm
                               "IP_PI1": '169.254.30.155',
                               "IP_PI2": '169.254.71.46',
                               "BT_MAC_PI1": '',  # Needed by proj
                               "BT_MAC_PI2": '',  # unused
                               "MAC_PI1": 'dc:a6:32:0d:76:74',  # unused
                               "MAC_PI2": 'dc:a6:32:0d:74:f0'})  # unused

        self.setupList.append({"SERIAL": '00079',
                               "SERIAL_PI1": '100000008e1595b5',  # CPU serial on pi USED
                               "SERIAL_PI2": '1000000006754bb2',  # CPU serial on pi USED
                               "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                               "BT_MAC_PROJ": '',  # Needed by pi1
                               "CIRCLE_PITCH": '6.000',  # mm
                               "IP_PI1": '169.254.30.155',
                               "IP_PI2": '169.254.71.46',
                               "BT_MAC_PI1": '',  # Needed by proj
                               "BT_MAC_PI2": '',  # unused
                               "MAC_PI1": 'dc:a6:32:0d:73:e8',  # unused
                               "MAC_PI2": 'dc:a6:32:0d:75:15'})  # unused

        self.setupList.append({"SERIAL": '00080',
                               "SERIAL_PI1": '100000009f606b29',  # CPU serial on pi USED
                               "SERIAL_PI2": '10000000526b585c',  # CPU serial on pi USED
                               "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                               "BT_MAC_PROJ": '',  # Needed by pi1
                               "CIRCLE_PITCH": '6.000',  # mm
                               "IP_PI1": '169.254.30.155',
                               "IP_PI2": '169.254.71.46',
                               "BT_MAC_PI1": '',  # Needed by proj
                               "BT_MAC_PI2": '',  # unused
                               "MAC_PI1": 'dc:a6:32:0d:76:06',  # unused
                               "MAC_PI2": 'dc:a6:32:0d:77:27'})  # unused

        self.setupList.append({"SERIAL": '00081',
                               "SERIAL_PI1": '10000000a577ce37',  # CPU serial on pi USED
                               "SERIAL_PI2": '1000000031c5c3fb',  # CPU serial on pi USED
                               "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                               "BT_MAC_PROJ": '',  # Needed by pi1
                               "CIRCLE_PITCH": '6.000',  # mm
                               "IP_PI1": '169.254.30.155',
                               "IP_PI2": '169.254.71.46',
                               "BT_MAC_PI1": '',  # Needed by proj
                               "BT_MAC_PI2": '',  # unused
                               "MAC_PI1": 'dc:a6:32:0d:35:8f',  # unused
                               "MAC_PI2": 'dc:a6:32:0d:75:a4'})  # unused

        self.setupList.append({"SERIAL": '00082',
                           "SERIAL_PI1": '10000000280f6e7f',  # CPU serial on pi USED
                           "SERIAL_PI2": '100000005ad967d8',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:27:38:34',  # unused
                           "MAC_PI2": 'dc:a6:32:27:37:4c'})  # unused

        self.setupList.append({"SERIAL": '00083',
                           "SERIAL_PI1": '10000000e51c6af4',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000f30cc8c9',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:2c:53',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:76:21'})  # unused

        self.setupList.append({"SERIAL": '00084',
                           "SERIAL_PI1": '100000007ec5aca4',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000bcc520be',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:75:11',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:77:16'})  # unused

        self.setupList.append({"SERIAL": '00085',
                           "SERIAL_PI1": '10000000c6deaf60',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000db40836a',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:74:97',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:73:a3'})  # unused

        self.setupList.append({"SERIAL": '00086',
                           "SERIAL_PI1": '10000000ca3d69fe',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000be9a66ad',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:76:e6',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:4a:69'})  # unused

        self.setupList.append({"SERIAL": '00087',
                           "SERIAL_PI1": '100000003444517b',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000df104b73',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:74:9a',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:73:fd'})  # unused

        self.setupList.append({"SERIAL": '00088',
                           "SERIAL_PI1": '10000000d8efb4cb',  # CPU serial on pi USED
                           "SERIAL_PI2": '100000007b1725be',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:76:7d',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:75:e2'})  # unused

        self.setupList.append({"SERIAL": '00089',
                           "SERIAL_PI1": '100000003d4b88a0',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000204e1308',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:76:15',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:74:67'})  # unused

        self.setupList.append({"SERIAL": '00090',
                           "SERIAL_PI1": '1000000096364cb3',  # CPU serial on pi USED
                           "SERIAL_PI2": '1000000007a9bb69',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:0d:75:08',  # unused
                           "MAC_PI2": 'dc:a6:32:0d:74:3a'})  # unused

        self.setupList.append({"SERIAL": '00091',
                           "SERIAL_PI1": '100000001fdbe258',  # CPU serial on pi USED
                           "SERIAL_PI2": '1000000019c4d672',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:29:f2:6a',  # unused
                           "MAC_PI2": 'dc:a6:32:29:f1:8d'})  # unused

        self.setupList.append({"SERIAL": '00092',
                           "SERIAL_PI1": '10000000d4b4a889',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000f6533d0e',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:29:dd:c1',  # unused
                           "MAC_PI2": 'dc:a6:32:29:f1:c2'})  # unused

        self.setupList.append({"SERIAL": '00093',
                           "SERIAL_PI1": '1000000084916a6f',  # CPU serial on pi USED
                           "SERIAL_PI2": '100000009bcc686b',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:29:f1:80',  # unused
                           "MAC_PI2": 'dc:a6:32:29:f1:c8'})  # unused

        self.setupList.append({"SERIAL": '00094',
                           "SERIAL_PI1": '100000009b815383',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000dd3f6c7e',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:29:f1:0e',  # unused
                           "MAC_PI2": 'dc:a6:32:29:ee:c2'})  # unused

        self.setupList.append({"SERIAL": '00095',
                           "SERIAL_PI1": '100000001212c376',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000255b742c',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:29:68:88',  # unused
                           "MAC_PI2": 'dc:a6:32:29:ec:9d'})  # unused

        self.setupList.append({"SERIAL": '00096',
                           "SERIAL_PI1": '10000000065f88c1',  # CPU serial on pi USED
                           "SERIAL_PI2": '100000000ae0e6aa',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:29:71:81',  # unused
                           "MAC_PI2": 'dc:a6:32:29:dc:a7'})  # unused

        self.setupList.append({"SERIAL": '00097',
                           "SERIAL_PI1": '100000002e38a732',  # CPU serial on pi USED
                           "SERIAL_PI2": '100000006733a06c',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:29:f1:62',  # unused
                           "MAC_PI2": 'dc:a6:32:29:e6:d3'})  # unused

        self.setupList.append({"SERIAL": '00098',
                           "SERIAL_PI1": '10000000334c681f',  # CPU serial on pi USED
                           "SERIAL_PI2": '100000008d54e5f9',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:29:ef:82',  # unused
                           "MAC_PI2": 'dc:a6:32:29:da:78'})  # unused

        self.setupList.append({"SERIAL": '00099',
                           "SERIAL_PI1": '100000007286ad13',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000570a3f76',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:29:f1:08',  # unused
                           "MAC_PI2": 'dc:a6:32:29:f1:24'})  # unused

        self.setupList.append({"SERIAL": '00100',
                           "SERIAL_PI1": '10000000a7a43123',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000c17002f6',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:29:6d:d6',  # unused
                           "MAC_PI2": 'dc:a6:32:29:f2:25'})  # unused

        self.setupList.append({"SERIAL": '00101',
                           "SERIAL_PI1": '100000005356dc8c',  # CPU serial on pi USED
                           "SERIAL_PI2": '1000000053478d9e',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:29:eb:b6',  # unused
                           "MAC_PI2": 'dc:a6:32:29:f1:77'})  # unused

        self.setupList.append({"SERIAL": '00102',
                           "SERIAL_PI1": '1000000076ce5857',  # CPU serial on pi USED
                           "SERIAL_PI2": '100000009a9ced80',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:29:f1:56',  # unused
                           "MAC_PI2": 'dc:a6:32:29:f0:ed'})  # unused

        self.setupList.append({"SERIAL": '00103',
                           "SERIAL_PI1": '10000000da788251',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000fc1cbd1e',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:29:f1:ce',  # unused
                           "MAC_PI2": 'dc:a6:32:29:f1:05'})  # unused

        self.setupList.append({"SERIAL": '00104',
                           "SERIAL_PI1": '100000006d44c66a',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000ca250ed0',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:29:f1:2c',  # unused
                           "MAC_PI2": 'dc:a6:32:29:75:ef'})  # unused

        self.setupList.append({"SERIAL": '00105',
                           "SERIAL_PI1": '10000000dac311c0',  # CPU serial on pi USED
                           "SERIAL_PI2": '1000000031ff2dec',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:29:f1:68',  # unused
                           "MAC_PI2": 'dc:a6:32:29:f1:6b'})  # unused
        self.setupList.append({"SERIAL": '00106',
                           "SERIAL_PI1": '10000000f9ad12a3',  # CPU serial on pi USED
                           "SERIAL_PI2": '10000000f7c54a4c',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:2a:0f:4d',  # unused
                           "MAC_PI2": 'dc:a6:32:2a:0e:f6'})  # unused
        self.setupList.append({"SERIAL": '00107',
                           "SERIAL_PI1": '1000000075af52dd',  # CPU serial on pi USED
                           "SERIAL_PI2": '100000006f54dfe6',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:2a:0e:51',  # unused
                           "MAC_PI2": 'dc:a6:32:2a:0a:16'})  # unused
        self.setupList.append({"SERIAL": '00108',
                           "SERIAL_PI1": '10000000258ce34e',  # CPU serial on pi USED
                           "SERIAL_PI2": '1000000037a60cff',  # CPU serial on pi USED
                           "BT_UUID_PI1": 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',  # Needed by pi1 and proj
                           "BT_MAC_PROJ": '',  # Needed by pi1
                           "CIRCLE_PITCH": '6.000',  # mm
                           "IP_PI1": '169.254.30.155',
                           "IP_PI2": '169.254.71.46',
                           "BT_MAC_PI1": '',  # Needed by proj
                           "BT_MAC_PI2": '',  # unused
                           "MAC_PI1": 'dc:a6:32:2a:0a:72',  # unused
                           "MAC_PI2": 'dc:a6:32:2a:0e:72'})  # unused

        self.setupList.append({"SERIAL": '00109',
                            'SERIAL_PI1': '10000000750c4365',
                            'SERIAL_PI2': '1000000043608050',
                            'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                            'BT_MAC_PROJ': '',
                            'CIRCLE_PITCH': '6.000',
                            'IP_PI1': '169.254.30.155',
                            'IP_PI2': '169.254.71.46',
                            'BT_MAC_PI1': '',
                            'BT_MAC_PI2': '',
                            'MAC_PI1': 'dc:a6:32:2a:0f:11',
                            'MAC_PI2': 'dc:a6:32:2a:0e:ab'})

        self.setupList.append({"SERIAL": '00110',
                    'SERIAL_PI1': '100000004645da81',
                    'SERIAL_PI2': '10000000af25c1b5',
                    'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                    'BT_MAC_PROJ': '',
                    'CIRCLE_PITCH': '6.000',
                    'IP_PI1': '169.254.30.155',
                    'IP_PI2': '169.254.71.46',
                    'BT_MAC_PI1': '',
                    'BT_MAC_PI2': '',
                    'MAC_PI1': 'dc:a6:32:2a:09:a1',
                    'MAC_PI2': 'dc:a6:32:2a:0e:de',
                   'PROJ_MODEL': 'C6',
                   'LEVELLER': 'ARD',
                   'LENSES': '6mm',
                   'TYPE': 'DENTAL',
                   'WIFI_READY': 'Y'})
        self.setupList.append({"SERIAL": '00111',
                'SERIAL_PI1': '10000000d76c98a6',
                'SERIAL_PI2': '1000000070cd64da',
                'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                'BT_MAC_PROJ': '',
                'CIRCLE_PITCH': '6.000',
                'IP_PI1': '169.254.30.155',
                'IP_PI2': '169.254.71.46',
                'BT_MAC_PI1': '',
                'BT_MAC_PI2': '',
                'MAC_PI1': 'dc:a6:32:2a:0a:3a',
                'MAC_PI2': 'dc:a6:32:2a:07:ac'})

        self.setupList.append({"SERIAL": '00112',
                'SERIAL_PI1': '10000000085d2d75',
                'SERIAL_PI2': '10000000e60b9d35',
                'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                'BT_MAC_PROJ': '',
                'CIRCLE_PITCH': '6.000',
                'IP_PI1': '169.254.30.155',
                'IP_PI2': '169.254.71.46',
                'BT_MAC_PI1': '',
                'BT_MAC_PI2': '',
                'MAC_PI1': 'dc:a6:32:2a:0a:34',
                'MAC_PI2': 'dc:a6:32:2a:09:6e'})

        self.setupList.append({"SERIAL": '00113',
                'SERIAL_PI1': '10000000187602c1',
                'SERIAL_PI2': '1000000045be6047',
                'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                'BT_MAC_PROJ': '',
                'CIRCLE_PITCH': '6.000',
                'IP_PI1': '169.254.30.155',
                'IP_PI2': '169.254.71.46',
                'BT_MAC_PI1': '',
                'BT_MAC_PI2': '',
                'MAC_PI1': 'dc:a6:32:29:f1:d4',
                'MAC_PI2': 'dc:a6:32:29:d9:22'})

        self.setupList.append({'SERIAL': '00114',
                               'SERIAL_PI1': '100000003f88403a',
                               'SERIAL_PI2': '10000000ec6b2dad',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:2a:0a:8c',
                               'MAC_PI2': 'dc:a6:32:2a:08:e4',
                               'LEVELLER': 'ARD',
                               'LENSES': '3mm',
                               'TYPE': 'DENTAL'})

        self.setupList.append({"SERIAL": '00115',
                'SERIAL_PI1': '10000000cbda06ef',
                'SERIAL_PI2': '100000000ddb4be0',
                'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                'BT_MAC_PROJ': '',
                'CIRCLE_PITCH': '6.000',
                'IP_PI1': '169.254.30.155',
                'IP_PI2': '169.254.71.46',
                'BT_MAC_PI1': '',
                'BT_MAC_PI2': '',
                'MAC_PI1': 'dc:a6:32:2a:0e:ae',
                'MAC_PI2': 'dc:a6:32:2a:01:2b'})
        self.setupList.append({"SERIAL": '00116',
                'SERIAL_PI1': '1000000008b74e75',
                'SERIAL_PI2': '10000000a7669fb7',
                'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                'BT_MAC_PROJ': '',
                'CIRCLE_PITCH': '6.000',
                'IP_PI1': '169.254.30.155',
                'IP_PI2': '169.254.71.46',
                'BT_MAC_PI1': '',
                'BT_MAC_PI2': '',
                'MAC_PI1': 'dc:a6:32:2a:0e:d6',
                'MAC_PI2': 'dc:a6:32:2a:08:db'})
        self.setupList.append({"SERIAL": '00117',
                'SERIAL_PI1': '1000000094d4a0e8',
                'SERIAL_PI2': '10000000b4e23941',
                'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                'BT_MAC_PROJ': '',
                'CIRCLE_PITCH': '6.000',
                'IP_PI1': '169.254.30.155',
                'IP_PI2': '169.254.71.46',
                'BT_MAC_PI1': '',
                'BT_MAC_PI2': '',
                'MAC_PI1': 'dc:a6:32:2a:0d:c1',
                'MAC_PI2': 'dc:a6:32:2a:08:d8'})

        self.setupList.append({"SERIAL": '00118',
                'SERIAL_PI1': '100000006146c764',
                'SERIAL_PI2': '10000000c2de11fa',
                'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                'BT_MAC_PROJ': '',
                'CIRCLE_PITCH': '6.000',
                'IP_PI1': '169.254.30.155',
                'IP_PI2': '169.254.71.46',
                'BT_MAC_PI1': '',
                'BT_MAC_PI2': '',
                'MAC_PI1': 'dc:a6:32:29:f1:98',
                'MAC_PI2': 'dc:a6:32:29:f0:cc'})

        self.setupList.append({"SERIAL": '00119',
                            'SERIAL_PI1': '10000000818c3eff',
                            'SERIAL_PI2': '100000007f0c71e6',
                            'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                            'BT_MAC_PROJ': '',
                            'CIRCLE_PITCH': '6.000',
                            'IP_PI1': '169.254.30.155',
                            'IP_PI2': '169.254.71.46',
                            'BT_MAC_PI1': '',
                            'BT_MAC_PI2': '',
                            'MAC_PI1': 'dc:a6:32:2a:0e:75',
                            'MAC_PI2': 'dc:a6:32:2a:08:9c'})

        self.setupList.append({"SERIAL": '00120',
                            'SERIAL_PI1': '10000000de8354e8',
                            'SERIAL_PI2': '100000002538d67d',
                            'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                            'BT_MAC_PROJ': '',
                            'CIRCLE_PITCH': '6.000',
                            'IP_PI1': '169.254.30.155',
                            'IP_PI2': '169.254.71.46',
                            'BT_MAC_PI1': '',
                            'BT_MAC_PI2': '',
                            'MAC_PI1': 'dc:a6:32:2a:0e:cc',
                            'MAC_PI2': 'dc:a6:32:2a:0e:bf'})

        self.setupList.append({"SERIAL": '00121',
                            'SERIAL_PI1': '10000000a89a8e7d',
                            'SERIAL_PI2': '100000003e0e7f88',
                            'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                            'BT_MAC_PROJ': '',
                            'CIRCLE_PITCH': '6.000',
                            'IP_PI1': '169.254.30.155',
                            'IP_PI2': '169.254.71.46',
                            'BT_MAC_PI1': '',
                            'BT_MAC_PI2': '',
                            'MAC_PI1': 'dc:a6:32:2a:09:44',
                            'MAC_PI2': 'dc:a6:32:2a:0e:f0'})

        self.setupList.append({"SERIAL": '00122',
                                   'SERIAL_PI1': '10000000e42f7e63',
                                   'SERIAL_PI2': '10000000507058cb',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:06:ce',
                                   'MAC_PI2': 'dc:a6:32:2a:0e:96'})
        self.setupList.append({"SERIAL": '00123',
                                   'SERIAL_PI1': '100000008e6681ce',
                                   'SERIAL_PI2': '100000006af5deba',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:0f:29',
                                   'MAC_PI2': 'dc:a6:32:2a:09:20'})
        self.setupList.append({"SERIAL": '00124',
                                   'SERIAL_PI1': '1000000060285395',
                                   'SERIAL_PI2': '100000003b36cd7d',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:0e:db',
                                   'MAC_PI2': 'dc:a6:32:2a:14:ba'})

        self.setupList.append({"SERIAL": '00125',
                                   'SERIAL_PI1': '10000000e169422a',
                                   'SERIAL_PI2': '100000006b60aeb7',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:0f:35',
                                   'MAC_PI2': 'dc:a6:32:2a:07:13'})
        self.setupList.append({"SERIAL": '00126',
                                   'SERIAL_PI1': '100000009ff1c608',
                                   'SERIAL_PI2': '10000000c9bf1507',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:0f:78',
                                   'MAC_PI2': 'dc:a6:32:2a:0e:9e'})
        self.setupList.append({"SERIAL": '00127',
                                   'SERIAL_PI1': '1000000019e8c5f9',
                                   'SERIAL_PI2': '1000000068a71198',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:0f:6b',
                                   'MAC_PI2': 'dc:a6:32:2a:10:10'})
        self.setupList.append({"SERIAL": '00128',
                                   'SERIAL_PI1': '10000000ad57605b',
                                   'SERIAL_PI2': '100000002df2ed49',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:14:ab',
                                   'MAC_PI2': 'dc:a6:32:2a:16:52'})

        self.setupList.append({"SERIAL": '00129',
                                   'SERIAL_PI1': '10000000b6524877',
                                   'SERIAL_PI2': '10000000e295eb64',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:16:58',
                                   'MAC_PI2': 'dc:a6:32:2a:12:77'})
        self.setupList.append({"SERIAL": '00130',
                                   'SERIAL_PI1': '10000000b4d29000',
                                   'SERIAL_PI2': '10000000faf7ddf1',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:12:4d',
                                   'MAC_PI2': 'dc:a6:32:2a:14:a8'})
        self.setupList.append({"SERIAL": '00131',
                                   'SERIAL_PI1': '10000000d1249e38',
                                   'SERIAL_PI2': '100000007e0fec86',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:16:46',
                                   'MAC_PI2': 'dc:a6:32:2a:15:a1'})
        self.setupList.append({"SERIAL": '00132',
                                   'SERIAL_PI1': '10000000c8206002',
                                   'SERIAL_PI2': '100000006f13669c',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:15:4a',
                                   'MAC_PI2': 'dc:a6:32:2a:14:2a'})
        self.setupList.append({"SERIAL": '00133',
                                   'SERIAL_PI1': '1000000063db09a2',
                                   'SERIAL_PI2': '100000001843881b',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:12:59',
                                   'MAC_PI2': 'dc:a6:32:2a:15:92'})
        self.setupList.append({"SERIAL": '00134',
                                   'SERIAL_PI1': '10000000092346f0',
                                   'SERIAL_PI2': '10000000d0718dd6',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:17:f9',
                                   'MAC_PI2': 'dc:a6:32:2a:15:20'})
        self.setupList.append({"SERIAL": '00135',
                                   'SERIAL_PI1': '10000000e4df7642',
                                   'SERIAL_PI2': '100000002cb60302',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:15:d1',
                                   'MAC_PI2': 'dc:a6:32:2a:11:fc'})
        self.setupList.append({"SERIAL": '00136',
                                   'SERIAL_PI1': '10000000c6176f49',
                                   'SERIAL_PI2': '100000000a1e8445',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:14:4e',
                                   'MAC_PI2': 'dc:a6:32:2a:14:cf'})
        self.setupList.append({"SERIAL": '00137',
                                   'SERIAL_PI1': '100000009ca2afb7',
                                   'SERIAL_PI2': '1000000033f53e96',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:12:02',
                                   'MAC_PI2': 'dc:a6:32:2a:15:e5'})
        self.setupList.append({"SERIAL": '00138',
                                   'SERIAL_PI1': '100000000ffeab00',
                                   'SERIAL_PI2': '100000001a52bda0',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:0f:b0',
                                   'MAC_PI2': 'dc:a6:32:2a:16:91'})
        self.setupList.append({"SERIAL": '00139',
                                   'SERIAL_PI1': '10000000ac2d771c',
                                   'SERIAL_PI2': '1000000051ecbe6e',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:11:87',
                                   'MAC_PI2': 'dc:a6:32:2a:15:74'})
        self.setupList.append({"SERIAL": '00140',
                                   'SERIAL_PI1': '10000000b68c7dff',
                                   'SERIAL_PI2': '10000000b95e6635',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:11:c8',
                                   'MAC_PI2': 'dc:a6:32:2a:15:bf',
                                   'PROJ_MODEL': 'C6',
                                   'LEVELLER': 'ARD',
                                   'LENSES': '6mm',
                                   'TYPE': 'DENTAL',
                                   'WIFI_READY': 'Y'})
        self.setupList.append({"SERIAL": '00141',
                                   'SERIAL_PI1': '1000000096e2a788',
                                   'SERIAL_PI2': '10000000537d5584',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:12:44',
                                   'MAC_PI2': 'dc:a6:32:2a:15:c5'})

        self.setupList.append({"SERIAL": '00142',
                                   'SERIAL_PI1': '100000009a827ba2',
                                   'SERIAL_PI2': '10000000804baf92',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:15:a9',
                                   'MAC_PI2': 'dc:a6:32:2a:16:3d'})
        self.setupList.append({"SERIAL": '00143',
                                   'SERIAL_PI1': '10000000406943bd',
                                   'SERIAL_PI2': '10000000c5f54309',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:0a:7f',
                                   'MAC_PI2': 'dc:a6:32:2a:16:a5'})
        self.setupList.append({"SERIAL": '00144',
                                   'SERIAL_PI1': '10000000c25bf85a',
                                   'SERIAL_PI2': '10000000176ecca9',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:16:42',
                                   'MAC_PI2': 'dc:a6:32:2a:12:a4'})
        self.setupList.append({"SERIAL": '00145',
                                   'SERIAL_PI1': '10000000940e67e4',
                                   'SERIAL_PI2': '10000000a29891a8',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:12:0e',
                                   'MAC_PI2': 'dc:a6:32:2a:11:57'})
        self.setupList.append({'SERIAL': '00146',
                               'SERIAL_PI1': '100000008a7f4b95',
                               'SERIAL_PI2': '10000000abb7a104',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:9a:61:5c',
                               'MAC_PI2': 'e4:5f:01:9a:60:78',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '7'})
        self.setupList.append({"SERIAL": '00147',#eluxe I think
                               'SERIAL_PI1': '1000000082ae4ea5',
                               'SERIAL_PI2': '10000000acb46272',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:2a:15:7a',
                               'MAC_PI2': 'dc:a6:32:2a:14:c0',
                               'PROJ_MODEL': 'C6',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '7'})

        self.setupList.append({"SERIAL": '00148',
                                   'SERIAL_PI1': '1000000040c5c19f',
                                   'SERIAL_PI2': '10000000cda5da4a',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:05:e4',
                                   'MAC_PI2': 'dc:a6:32:2a:11:66'})

        self.setupList.append({"SERIAL": '00149',
                                   'SERIAL_PI1': '10000000229802ed',
                                   'SERIAL_PI2': '1000000043b3538c',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3d:e0:84',
                                   'MAC_PI2': 'dc:a6:32:3d:ec:99'})
        self.setupList.append({"SERIAL": '00150',
                                   'SERIAL_PI1': '100000008b0abafb',
                                   'SERIAL_PI2': '100000001283e92b',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3d:e3:4b',
                                   'MAC_PI2': 'dc:a6:32:2a:16:6d'})
        self.setupList.append({"SERIAL": '00151',
                                   'SERIAL_PI1': '100000005c10205d',
                                   'SERIAL_PI2': '100000007f98499a',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:0e:f5',
                                   'MAC_PI2': 'dc:a6:32:2a:11:ae'})
        self.setupList.append({"SERIAL": '00152',
                                   'SERIAL_PI1': '10000000a2f5f40f',
                                   'SERIAL_PI2': '100000000008154f',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3d:e2:07',
                                   'MAC_PI2': 'dc:a6:32:3d:ea:80'})
        self.setupList.append({"SERIAL": '00153',
                                   'SERIAL_PI1': '10000000fe48c111',
                                   'SERIAL_PI2': '10000000a0c98d9c',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:2a:14:93',
                                   'MAC_PI2': 'dc:a6:32:2a:12:b6'})
        self.setupList.append({"SERIAL": '00154',
                                   'SERIAL_PI1': '1000000007b119eb',
                                   'SERIAL_PI2': '1000000051006884',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3d:e1:26',
                                   'MAC_PI2': 'dc:a6:32:3d:ef:47'})
        self.setupList.append({"SERIAL": '00155',
                                   'SERIAL_PI1': '100000000e5b67fc',
                                   'SERIAL_PI2': '100000004b54d3bb',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3d:ea:2a',
                                   'MAC_PI2': 'dc:a6:32:3d:e8:c7'})
        self.setupList.append({"SERIAL": '00156',
                                  'SERIAL_PI1': '10000000e03672a9',
                                   'SERIAL_PI2': '10000000f80c1c7b',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3e:2c:0d',
                                   'MAC_PI2': 'dc:a6:32:36:54:c6'})

        self.setupList.append({"SERIAL": '00157',
                                   'SERIAL_PI1': '100000003d5385df',
                                   'SERIAL_PI2': '10000000ed4e8b7b',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3d:ed:fb',
                                   'MAC_PI2': 'dc:a6:32:3d:ec:72'})
        self.setupList.append({"SERIAL": '00158',
                                  'SERIAL_PI1': '10000000148758c4',
                                   'SERIAL_PI2': '10000000be51cc64',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3e:14:f0',
                                   'MAC_PI2': 'dc:a6:32:3d:f8:60'})
        self.setupList.append({"SERIAL": '00159',
                                  'SERIAL_PI1': '10000000d840557c',
                                   'SERIAL_PI2': '100000005f4e3408',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:37:8a:83',
                                   'MAC_PI2': 'dc:a6:32:36:54:a2'})
        self.setupList.append({"SERIAL": '00160',
                                   'SERIAL_PI1': '10000000a0d09217',
                                   'SERIAL_PI2': '10000000af9ce234',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3d:e3:0f',
                                   'MAC_PI2': 'dc:a6:32:3d:eb:97'})
        self.setupList.append({"SERIAL": '00161',
                                   'SERIAL_PI1': '10000000e631b86f',
                                   'SERIAL_PI2': '1000000082829ded',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3d:eb:14',
                                   'MAC_PI2': 'dc:a6:32:3d:e2:2b'})
        self.setupList.append({"SERIAL": '00162',
                                   'SERIAL_PI1': '10000000832f1e51',
                                   'SERIAL_PI2': '10000000b7623b69',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3d:e4:56',
                                   'MAC_PI2': 'dc:a6:32:3d:e3:b7'})
        self.setupList.append({"SERIAL": '00163',
                                   'SERIAL_PI1': '10000000d1052ae8',
                                   'SERIAL_PI2': '10000000ff9d0583',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:37:96:b6',
                                   'MAC_PI2': 'dc:a6:32:3d:ea:b6'})
        self.setupList.append({"SERIAL": '00164',
                                   'SERIAL_PI1': '10000000645aae49',
                                   'SERIAL_PI2': '100000005dca0bc8',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3d:ec:5e',
                                   'MAC_PI2': 'dc:a6:32:2a:15:29'})
        self.setupList.append({"SERIAL": '00165',
                                    'SERIAL_PI1': '100000005feeb2f2',
                                    'SERIAL_PI2': '100000002120eb08',
                                    'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                    'BT_MAC_PROJ': '',
                                    'CIRCLE_PITCH': '6.000',
                                    'IP_PI1': '169.254.30.155',
                                    'IP_PI2': '169.254.71.46',
                                    'BT_MAC_PI1': '',
                                    'BT_MAC_PI2': '',
                                    'MAC_PI1': 'dc:a6:32:3d:e9:00',
                                    'MAC_PI2': 'dc:a6:32:29:85:4c'})
        self.setupList.append({"SERIAL": '00166',
                                   'SERIAL_PI1': '10000000869b9bbd',
                                   'SERIAL_PI2': '10000000490eb163',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3d:ef:72',
                                   'MAC_PI2': 'dc:a6:32:3d:f8:21'})
        self.setupList.append({"SERIAL": '00167',
                                   'SERIAL_PI1': '100000002f629f8d',
                                   'SERIAL_PI2': '10000000b0f82379',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3d:ea:94',
                                   'MAC_PI2': 'dc:a6:32:3d:e3:89'})
        self.setupList.append({"SERIAL": '00168',
                                   'SERIAL_PI1': '10000000747860aa',
                                   'SERIAL_PI2': '10000000ae7760d3',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3d:e3:97',
                                   'MAC_PI2': 'dc:a6:32:3d:ee:0b'})
        self.setupList.append({"SERIAL": '00169',
                                   'SERIAL_PI1': '100000009214fee7',
                                   'SERIAL_PI2': '10000000ac619c38',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3e:01:cd',
                                   'MAC_PI2': 'dc:a6:32:3d:ee:d0'})
        self.setupList.append({"SERIAL": '00170',
                                   'SERIAL_PI1': '10000000def2e53d',
                                   'SERIAL_PI2': '1000000052ae0dfd',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3d:ed:c5',
                                   'MAC_PI2': 'dc:a6:32:17:5f:37'})
        self.setupList.append({"SERIAL": '00171',
                                   'SERIAL_PI1': '10000000443c7633',
                                   'SERIAL_PI2': '10000000197cfb22',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3d:ea:33',
                                   'MAC_PI2': 'dc:a6:32:3d:e1:98'})
        self.setupList.append({'SERIAL': '00172',
                               'SERIAL_PI1': '10000000552a4c37',
                               'SERIAL_PI2': '10000000d07600a9',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:ca:f9:f4',
                               'MAC_PI2': 'dc:a6:32:ca:fa:0f',
                               'PROJ_MODEL': 'C6',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})

        self.setupList.append({"SERIAL": '00173',
                                   'SERIAL_PI1': '10000000abcc94bd',
                                   'SERIAL_PI2': '1000000054ae31a5',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3d:e2:6a',
                                   'MAC_PI2': 'dc:a6:32:3d:f1:b5'})
        self.setupList.append({"SERIAL": '00174',
                                   'SERIAL_PI1': '10000000e91e6f7d',
                                   'SERIAL_PI2': '10000000742d024f',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3e:29:17',
                                   'MAC_PI2': 'dc:a6:32:3e:1e:cb'})
        self.setupList.append({"SERIAL": '00175',
                                   'SERIAL_PI1': '10000000b8694141',
                                   'SERIAL_PI2': '10000000d74f60f4',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3d:c7:be',
                                   'MAC_PI2': 'dc:a6:32:3d:e2:eb'})

        self.setupList.append({"SERIAL": '00176',
                                   'SERIAL_PI1': '10000000a2ed1b13',
                                   'SERIAL_PI2': '1000000052d1f5ff',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3d:e4:9e',
                                   'MAC_PI2': 'dc:a6:32:3d:f7:ac'})
        self.setupList.append({"SERIAL": '00177',
                                   'SERIAL_PI1': '1000000075c07505',
                                   'SERIAL_PI2': '10000000d5ccbd61',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:37:8c:ff',
                                   'MAC_PI2': 'dc:a6:32:3e:27:6c'})
        self.setupList.append({"SERIAL": '00178',
                                   'SERIAL_PI1': '10000000155362c5',
                                   'SERIAL_PI2': '100000003ba43e45',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3d:e2:6d',
                                   'MAC_PI2': 'dc:a6:32:3d:e1:6c'})
        self.setupList.append({"SERIAL": '00179',
                                   'SERIAL_PI1': '10000000b13e0d55',
                                   'SERIAL_PI2': '10000000a4889017',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3d:e4:17',
                                   'MAC_PI2': 'dc:a6:32:3d:e2:be'})
        self.setupList.append({"SERIAL": '00180',
                                   'SERIAL_PI1': '10000000f0efbe1a',
                                   'SERIAL_PI2': '10000000c7ecb684',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3e:25:24',
                                   'MAC_PI2': 'dc:a6:32:3d:e1:a7'})
        self.setupList.append({"SERIAL": '00181',
                                   'SERIAL_PI1': '100000009f2d151b',
                                   'SERIAL_PI2': '1000000033d04834',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:35:a6:b1',
                                   'MAC_PI2': 'dc:a6:32:3d:ea:d2'})

        self.setupList.append({'SERIAL': '00182',
                               'SERIAL_PI1': '10000000dde3d8ee',
                               'SERIAL_PI2': '1000000014e42a75',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:3e:01:42',
                               'MAC_PI2': 'dc:a6:32:3e:14:c5',
                               'PROJ_MODEL': 'C6',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})

        self.setupList.append({"SERIAL": '00183',
                                   'SERIAL_PI1': '1000000098e195b3',
                                   'SERIAL_PI2': '100000001e5c78bb',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:36:55:08',
                                   'MAC_PI2': 'dc:a6:32:3d:ed:ed'})
        self.setupList.append({"SERIAL": '00184',
                                   'SERIAL_PI1': '10000000fd38104f',
                                   'SERIAL_PI2': '10000000036c42da',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:37:93:05',
                                   'MAC_PI2': 'dc:a6:32:3e:26:50'})
        self.setupList.append({"SERIAL": '00185',
                                   'SERIAL_PI1': '10000000aa7ffdf6',
                                   'SERIAL_PI2': '1000000075d7ab09',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:38:d5:31',
                                   'MAC_PI2': 'dc:a6:32:37:92:a3'})
        self.setupList.append({"SERIAL": '00186',
                                   'SERIAL_PI1': '1000000068a00267',
                                   'SERIAL_PI2': '10000000d5e1b807',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:1f:85:45',
                                   'MAC_PI2': 'dc:a6:32:3e:02:ce'})
        self.setupList.append({"SERIAL": '00187',
                                   'SERIAL_PI1': '1000000080677d31',
                                   'SERIAL_PI2': '10000000b5ed33a2',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:3e:29:5a',
                                   'MAC_PI2': 'dc:a6:32:38:d9:30'})
        self.setupList.append({"SERIAL": '00188',
                                   'SERIAL_PI1': '10000000c05d928b',
                                   'SERIAL_PI2': '10000000df3abf2f',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:1f:8f:77',
                                   'MAC_PI2': 'dc:a6:32:3d:e4:05'})
        self.setupList.append({"SERIAL": '00189',
                                   'SERIAL_PI1': '10000000a131d70d',
                                   'SERIAL_PI2': '10000000c60fdce8',
                                   'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                                   'BT_MAC_PROJ': '',
                                   'CIRCLE_PITCH': '6.000',
                                   'IP_PI1': '169.254.30.155',
                                   'IP_PI2': '169.254.71.46',
                                   'BT_MAC_PI1': '',
                                   'BT_MAC_PI2': '',
                                   'MAC_PI1': 'dc:a6:32:37:a3:89',
                                   'MAC_PI2': 'dc:a6:32:3d:e9:78'})
        self.setupList.append({"SERIAL": '00190',
                               'SERIAL_PI1': '1000000087899063',
                               'SERIAL_PI2': '1000000073ee2c96',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:37:a5:48',
                               'MAC_PI2': 'dc:a6:32:3e:27:9a'})
        self.setupList.append({'SERIAL': '00191',
                               'SERIAL_PI1': '10000000a2f7b667',
                               'SERIAL_PI2': '10000000e0e237b2',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:3d:e9:ab',
                               'MAC_PI2': 'dc:a6:32:3d:f6:95'})
        self.setupList.append({'SERIAL': '00192',
                               'SERIAL_PI1': '1000000024b795c0',
                               'SERIAL_PI2': '10000000d2127583',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:37:a4:f4',
                               'MAC_PI2': 'dc:a6:32:3e:14:e6'})
        self.setupList.append({'SERIAL': '00193',
                               'SERIAL_PI1': '1000000052afef86',
                               'SERIAL_PI2': '10000000216d4044',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:3d:ea:75',
                               'MAC_PI2': 'dc:a6:32:37:b8:34',
                               'PROJ_MODEL': 'C6',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00194',
                               'SERIAL_PI1': '10000000e7760874',
                               'SERIAL_PI2': '1000000072e20a96',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:3d:e1:bc',
                               'MAC_PI2': 'dc:a6:32:37:97:2b'})
        self.setupList.append({'SERIAL': '00195',
                               'SERIAL_PI1': '10000000c4af0eb0',
                               'SERIAL_PI2': '100000007a3ef320',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:3d:f5:09',
                               'MAC_PI2': 'dc:a6:32:33:20:f0'})
        self.setupList.append({'SERIAL': '00196',
                               'SERIAL_PI1': '10000000945470fc',
                               'SERIAL_PI2': '100000001630e6b2',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:3d:e3:9f',
                               'MAC_PI2': 'dc:a6:32:36:57:22'})
        self.setupList.append({'SERIAL': '00197',
                               'SERIAL_PI1': '10000000c258634e',
                               'SERIAL_PI2': '100000009a2e0dc4',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:1f:8e:09',
                               'MAC_PI2': 'dc:a6:32:3d:e3:9c'})
        self.setupList.append({'SERIAL': '00198',
                               'SERIAL_PI1': '1000000066c2d666',
                               'SERIAL_PI2': '10000000ae7e0a6d',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:37:9b:5a',
                               'MAC_PI2': 'dc:a6:32:3d:ea:16'})
        self.setupList.append({'SERIAL': '00199',
                               'SERIAL_PI1': '10000000fb7bb851',
                               'SERIAL_PI2': '10000000e45e52db',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:3e:12:b7',
                               'MAC_PI2': 'dc:a6:32:3d:e3:7b'})
        self.setupList.append({'SERIAL': '00200',
                               'SERIAL_PI1': '100000006f39df2f',
                               'SERIAL_PI2': '1000000044664e3e',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:3d:ee:85',
                               'MAC_PI2': 'dc:a6:32:3d:e0:b8'})
        self.setupList.append({'SERIAL': '00201',
                               'SERIAL_PI1': '10000000ec178081',
                               'SERIAL_PI2': '100000002330669b',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:ca:fa:21',
                               'MAC_PI2': 'dc:a6:32:ca:fa:c3'})
        self.setupList.append({'SERIAL': '00202',
                               'SERIAL_PI1': '10000000355678bb',
                               'SERIAL_PI2': '100000006843450f',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:ca:f9:94',
                               'MAC_PI2': 'dc:a6:32:ca:fa:18',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'MARKER',
                               'LENSES': '3mm',
                               'TYPE': 'BSB',
                               'WIFI_READY': 'Y'})  # PROJ MODEL FIELD ADDED FROM HERE ON
        #new style from here - didn't work due to missing fields - added missing fields back
        self.setupList.append({'SERIAL': '00203',
                               'SERIAL_PI1': '1000000080db69a1',
                               'SERIAL_PI2': '1000000043621f83',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'MAC_PI1': 'dc:a6:32:ca:fa:8d',
                               'MAC_PI2': 'dc:a6:32:ca:f0:0d',
                               'BT_MAC_PROJ': '',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'PROJ_MODEL':'C6_V2'})
        self.setupList.append({'SERIAL': '00204',
                               'SERIAL_PI1': '10000000d5013e8b',
                               'SERIAL_PI2': '100000006dfdde38',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'MAC_PI1': 'dc:a6:32:ca:fa:d2',
                               'MAC_PI2': 'dc:a6:32:ca:fa:27',
                               'BT_MAC_PROJ': '',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'PROJ_MODEL':'C6_V2'})
        self.setupList.append({'SERIAL': '00205',
                               'SERIAL_PI1': '10000000dd3c7727',
                               'SERIAL_PI2': '100000007465bf8d',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'MAC_PI1': 'dc:a6:32:ca:f9:d6',
                               'MAC_PI2': 'dc:a6:32:ca:f9:bb',
                               'BT_MAC_PROJ': '',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'PROJ_MODEL': 'C6'})
        self.setupList.append({'SERIAL': '00206',
                               'SERIAL_PI1': '1000000020ec2ce4',
                               'SERIAL_PI2': '100000005f84e75f',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'MAC_PI1': 'dc:a6:32:ca:fa:9c',
                               'MAC_PI2': 'dc:a6:32:ca:e0:56',
                               'BT_MAC_PROJ': '',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'PROJ_MODEL': 'C6'})
        self.setupList.append({'SERIAL': '00207',
                               'SERIAL_PI1': '100000004edc7dac',
                               'SERIAL_PI2': '10000000428a5a4a',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'MAC_PI1': 'dc:a6:32:ca:f9:f7',
                               'MAC_PI2': 'dc:a6:32:ca:fa:db',
                               'BT_MAC_PROJ': '',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'PROJ_MODEL': 'C6'})
        self.setupList.append({'SERIAL': '00208',
                               'SERIAL_PI1': '10000000a8b8a8f0',
                               'SERIAL_PI2': '10000000b0b2ba51',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'MAC_PI1': 'dc:a6:32:ca:fa:93',
                               'MAC_PI2': 'dc:a6:32:ca:f9:82',
                               'BT_MAC_PROJ': '',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'PROJ_MODEL': 'C6_V2'})
        self.setupList.append({'SERIAL': '00209',
                               'SERIAL_PI1': '100000007adae503',
                               'SERIAL_PI2': '10000000bde6376c',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'MAC_PI1': 'dc:a6:32:ca:e5:f9',
                               'MAC_PI2': 'dc:a6:32:ca:fa:b4',
                               'BT_MAC_PROJ': '',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'PROJ_MODEL': 'C6_V2',
                                'LEVELLER': 'ARD',
                                'LENSES': '6mm',
                                'TYPE': 'DENTAL',
                                'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00210',
                               'SERIAL_PI1': '1000000041423b4a',
                               'SERIAL_PI2': '10000000da31e677',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'MAC_PI1': 'dc:a6:32:ca:fa:3e',
                               'MAC_PI2': 'dc:a6:32:ca:fa:75',
                               'BT_MAC_PROJ': '',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'PROJ_MODEL': 'C6_V2',
                                'LEVELLER': 'ARD',
                                'LENSES': '6mm',
                                'TYPE': 'DENTAL',
                                'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00211',
                               'SERIAL_PI1': '100000009908bfdb',
                               'SERIAL_PI2': '10000000169d502f',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'MAC_PI1': 'dc:a6:32:ca:fa:d3',
                               'MAC_PI2': 'dc:a6:32:ca:f9:c1',
                               'BT_MAC_PROJ': '',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})

        self.setupList.append({'SERIAL': '00212',#v4 prototype
                               'SERIAL_PI1': '10000000705d5672',
                               'SERIAL_PI2': '100000007a7c0e70',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'MAC_PI1': 'dc:a6:32:ca:e7:e5',
                               'MAC_PI2': 'dc:a6:32:ca:e9:03',
                               'BT_MAC_PROJ': '',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER':'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})

        self.setupList.append({'SERIAL': '00213',
                               'SERIAL_PI1': '1000000001d828d9',
                               'SERIAL_PI2': '10000000439a149a',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'MAC_PI1': 'dc:a6:32:ca:f9:eb',
                               'MAC_PI2': 'dc:a6:32:ca:f9:a1',
                               'BT_MAC_PROJ': '',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                              'PROJ_MODEL': 'C6_V2',
                                'LEVELLER': 'ARD',
                                'LENSES': '6mm',
                                'TYPE': 'DENTAL',
                                'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00214',
                               'SERIAL_PI1': '100000002a90d800',
                               'SERIAL_PI2': '1000000077712d0d',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:ca:fa:1e',
                               'MAC_PI2': 'dc:a6:32:ca:fa:2a',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00215',
                               'SERIAL_PI1': '1000000044ce0509',
                               'SERIAL_PI2': '100000006bb5b0be',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'MAC_PI1': 'dc:a6:32:ca:fa:f6',
                               'MAC_PI2': 'dc:a6:32:ca:fa:57',
                               'BT_MAC_PROJ': '',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '7'})
        self.setupList.append({'SERIAL': '00216',#metal camera holders
                               'SERIAL_PI1': '10000000649db2bf',
                               'SERIAL_PI2': '10000000a3572a82',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'MAC_PI1': 'dc:a6:32:ca:fa:51',
                               'MAC_PI2': 'dc:a6:32:ca:fa:9f',
                               'BT_MAC_PROJ': '',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'PROJ_MODEL': 'C6'})#TODO Is it

        self.setupList.append({'SERIAL': '00217',
                               'SERIAL_PI1': '10000000559a0f78',
                               'SERIAL_PI2': '1000000002d9f2de',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:ca:f9:40',
                               'MAC_PI2': 'dc:a6:32:ca:fa:48'})
        self.setupList.append({'SERIAL': '00218',
                               'SERIAL_PI1': '10000000b06cc8b6',
                               'SERIAL_PI2': '1000000070813d40',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:ca:f9:e2',
                               'MAC_PI2': 'dc:a6:32:ca:f9:8c'})
        self.setupList.append({'SERIAL': '00219',
                               'SERIAL_PI1': '100000003897e06e',
                               'SERIAL_PI2': '100000007acac0ce',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:ca:fa:99',
                               'MAC_PI2': 'dc:a6:32:ca:f9:91'})
        self.setupList.append({'SERIAL': '00220',
                               'SERIAL_PI1': '1000000044a79693',
                               'SERIAL_PI2': '10000000edcf534f',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:ca:fa:ae',
                               'MAC_PI2': 'dc:a6:32:ca:fa:42'})
        self.setupList.append({'SERIAL': '00221',
                               'SERIAL_PI1': '100000000c7efdc5',
                               'SERIAL_PI2': '10000000a56d2c7a',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:9a:5f:d0',
                               'MAC_PI2': 'e4:5f:01:9a:5b:9a',
                               'PROJ_MODEL': 'C6',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})

        self.setupList.append({'SERIAL': '00222',
                               'SERIAL_PI1': '10000000a63af1b1',
                               'SERIAL_PI2': '100000008513ae33',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:ca:f9:97',
                               'MAC_PI2': 'dc:a6:32:ca:f9:4f'})
        self.setupList.append({'SERIAL': '00223',
                               'SERIAL_PI1': '10000000d2a993d2',
                               'SERIAL_PI2': '10000000b5fd3b42',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:ca:f9:e3',
                               'MAC_PI2': 'dc:a6:32:ca:fa:45'})
        self.setupList.append({'SERIAL': '00224',
                               'SERIAL_PI1': '10000000d9cd2834',
                               'SERIAL_PI2': '1000000020714548',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:ca:fa:78',
                               'MAC_PI2': 'dc:a6:32:ca:f9:5f'})
        self.setupList.append({'SERIAL': '00225',
                               'SERIAL_PI1': '1000000052e37121',
                               'SERIAL_PI2': '10000000aae4f725',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:ca:f9:ac',
                               'MAC_PI2': 'dc:a6:32:ca:f9:ca'})

        self.setupList.append({'SERIAL': '00226',
                               'SERIAL_PI1': '1000000042e7f5c4',
                               'SERIAL_PI2': '10000000d9cf1b82',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:ca:fa:24',
                               'MAC_PI2': 'dc:a6:32:ca:fa:5a',
                               'PROJ_MODEL': 'C6',
                               "LEVELLER": 'ARD',
                               "LENSES": '6mm',
                               "TYPE": 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '7'})

        self.setupList.append({'SERIAL': '00227',
                               'SERIAL_PI1': '100000003b70cafa',
                               'SERIAL_PI2': '100000002206aa2e',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:ca:e5:00',
                               'MAC_PI2': 'dc:a6:32:ca:fa:7b'})
        self.setupList.append({'SERIAL': '00228',
                               'SERIAL_PI1': '10000000aecd9681',
                               'SERIAL_PI2': '10000000e909bac8',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:ca:fa:03',
                               'MAC_PI2': 'dc:a6:32:ca:f9:88'})
        self.setupList.append({'SERIAL': '00229',
                               'SERIAL_PI1': '1000000070d080cf',
                               'SERIAL_PI2': '100000001ca36db0',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:ca:fa:54',
                               'MAC_PI2': 'dc:a6:32:ca:fa:10',
                               'PROJ_MODEL': 'C6',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})

        self.setupList.append({'SERIAL': '00230',
                               'SERIAL_PI1': '10000000ca5514bb',
                               'SERIAL_PI2': '10000000b5e57e28',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:38:c8',
                               'MAC_PI2': 'dc:a6:32:f2:38:f4',
                               'PROJ_MODEL':'C6_V2'})
        self.setupList.append({'SERIAL': '00231',
                               'SERIAL_PI1': '10000000a6be9175',
                               'SERIAL_PI2': '10000000dfdd60f9',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:38:c1',
                               'MAC_PI2': 'dc:a6:32:f2:33:a2',
                               'PROJ_MODEL':'C6_V2'})

        self.setupList.append({'SERIAL': '00232',
                               'SERIAL_PI1': '10000000e2183abe',
                               'SERIAL_PI2': '1000000006183f82',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:36:a5',
                               'MAC_PI2': 'dc:a6:32:f2:38:67',
                               'PROJ_MODEL': 'C6_V2'})
        self.setupList.append({'SERIAL': '00233',
                               'SERIAL_PI1': '100000000850bfa0',
                               'SERIAL_PI2': '1000000081ca0728',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:37:2f',
                               'MAC_PI2': 'dc:a6:32:f2:35:0b',
                               'PROJ_MODEL': 'C6_V2'})
        self.setupList.append({'SERIAL': '00234',
                               'SERIAL_PI1': '10000000fd3c9ff1',
                               'SERIAL_PI2': '100000002dd7f616',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:38:4f',
                               'MAC_PI2': 'dc:a6:32:f2:38:a9'})
        self.setupList.append({'SERIAL': '00235',
                               'SERIAL_PI1': '100000000be2a912',
                               'SERIAL_PI2': '10000000b5172ff7',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:38:97',
                               'MAC_PI2': 'dc:a6:32:f2:38:42',
                               'PROJ_MODEL': 'C6',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})

        self.setupList.append({'SERIAL': '00236',
                               'SERIAL_PI1': '10000000216bc86f',
                               'SERIAL_PI2': '10000000cd8b344e',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:37:09',
                               'MAC_PI2': 'dc:a6:32:f2:38:ac',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00237',
                               'SERIAL_PI1': '1000000072877a77',
                               'SERIAL_PI2': '100000007a8fe492',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:36:da',
                               'MAC_PI2': 'dc:a6:32:f2:34:89',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00238',
                               'SERIAL_PI1': '1000000084bcff48',
                               'SERIAL_PI2': '100000006ffd64eb',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:38:b8',
                               'MAC_PI2': 'dc:a6:32:f2:39:02',
                               'PROJ_MODEL': 'C6_V2'})
        self.setupList.append({'SERIAL': '00239',
                               'SERIAL_PI1': '100000005dd16d9c',
                               'SERIAL_PI2': '10000000fb842322',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:38:2b',
                               'MAC_PI2': 'dc:a6:32:f2:38:a0',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00240',#metal holders, prusa has
                               'SERIAL_PI1': '100000008ce530c9',
                               'SERIAL_PI2': '10000000fb60e2ef',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:39:51',
                               'MAC_PI2': 'e4:5f:01:9a:5f:d6',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '7'})
        self.setupList.append({'SERIAL': '00241',
                               'SERIAL_PI1': '10000000c77373b1',
                               'SERIAL_PI2': '100000008ee88b1c',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:37:fb',
                               'MAC_PI2': 'dc:a6:32:f2:37:f8',
                               'PROJ_MODEL': 'C6_V2'})
        self.setupList.append({'SERIAL': '00242',
                               'SERIAL_PI1': '100000004da364e3',
                               'SERIAL_PI2': '100000005e156e9a',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:38:1c',
                               'MAC_PI2': 'dc:a6:32:f2:37:9c',
                               'PROJ_MODEL': 'C6_V2'})
        self.setupList.append({'SERIAL': '00243',
                               'SERIAL_PI1': '1000000073590d79',
                               'SERIAL_PI2': '100000003867b84b',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:38:64',
                               'MAC_PI2': 'dc:a6:32:f2:38:3d',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00244',
                               'SERIAL_PI1': '10000000b6bd97c8',
                               'SERIAL_PI2': '100000003d0429a2',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:ca:f9:69',
                               'MAC_PI2': 'dc:a6:32:ca:f9:34',
                               'PROJ_MODEL': 'C6_V2'})

        self.setupList.append({'SERIAL': '00245',
                               'SERIAL_PI1': '100000008b4e70d3',
                               'SERIAL_PI2': '10000000f0c08fc4',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:1a:a9',
                               'MAC_PI2': 'dc:a6:32:f2:37:dd',
                               'PROJ_MODEL': 'C6_V2'})

        self.setupList.append({'SERIAL': '00246',
                               'SERIAL_PI1': '1000000015134209',
                               'SERIAL_PI2': '100000004d9467ad',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:e7:0b:bd',
                               'MAC_PI2': 'dc:a6:32:f2:37:fc',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00247',
                               'SERIAL_PI1': '100000003dcae0d9',
                               'SERIAL_PI2': '10000000940d7e49',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:39:21',
                               'MAC_PI2': 'dc:a6:32:f2:37:cb',
                               'PROJ_MODEL': 'C6_V2'})
        self.setupList.append({'SERIAL': '00248',
                               'SERIAL_PI1': '10000000a06d3b31',
                               'SERIAL_PI2': '10000000102bceda',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:38:0c',
                               'MAC_PI2': 'dc:a6:32:e7:0b:a7',
                                'PROJ_MODEL': 'C6_V2'})
        self.setupList.append({'SERIAL': '00249',
                               'SERIAL_PI1': '10000000a3c42b6f',
                               'SERIAL_PI2': '100000003333d1bd',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:e7:0b:60',
                               'MAC_PI2': 'dc:a6:32:e7:0b:c6',
                              'PROJ_MODEL': 'C6_V2',
                              'LEVELLER': 'ARD',
                              'LENSES': '6mm',
                              'TYPE': 'DENTAL',
                              'WIFI_READY': 'Y',
                               'CODE': '15'})
        self.setupList.append({'SERIAL': '00250',
                               'SERIAL_PI1': '100000004037ac5b',
                               'SERIAL_PI2': '10000000d8e4f9da',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:e6:fd:68',
                               'MAC_PI2': 'dc:a6:32:e7:0b:86',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00251',
                               'SERIAL_PI1': '1000000085c09f05',
                               'SERIAL_PI2': '100000003a2ad2ad',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:e7:0b:3b',
                               'MAC_PI2': 'dc:a6:32:e6:bd:bd',
                                'PROJ_MODEL': 'C6_V2'})
        self.setupList.append({'SERIAL': '00252',
                               'SERIAL_PI1': '10000000a954fc8d',
                               'SERIAL_PI2': '100000009d1f623a',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:38:ee',
                               'MAC_PI2': 'dc:a6:32:f2:13:3b',
                                'PROJ_MODEL': 'C6_V2'})
        self.setupList.append({'SERIAL': '00253',
                               'SERIAL_PI1': '1000000035ca6d94',
                               'SERIAL_PI2': '100000002c855dc4',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:e7:09:fc',
                               'MAC_PI2': 'dc:a6:32:e7:0b:80',
                               'PROJ_MODEL': 'C6'})
        self.setupList.append({'SERIAL': '00254',
                               'SERIAL_PI1': '10000000be4371bf',
                               'SERIAL_PI2': '10000000cd2ca613',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:38:7c',
                               'MAC_PI2': 'dc:a6:32:f2:39:1e',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'GP',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00255',
                               'SERIAL_PI1': '10000000b5ab977e',
                               'SERIAL_PI2': '1000000017060a4b',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:37:b9',
                               'MAC_PI2': 'dc:a6:32:f2:38:5c',
                               'PROJ_MODEL': 'C6_V2'})
        self.setupList.append({'SERIAL': '00256',
                               'SERIAL_PI1': '10000000e5812541',
                               'SERIAL_PI2': '1000000038111cb1',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:38:91',
                               'MAC_PI2': 'dc:a6:32:f2:38:eb',
                               'PROJ_MODEL': 'C6',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00257',
                               'SERIAL_PI1': '10000000a46eb376',
                               'SERIAL_PI2': '100000002ad57554',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:e7:09:8b',
                               'MAC_PI2': 'dc:a6:32:e7:0b:d8',
                               'PROJ_MODEL': 'C6'})
        self.setupList.append({'SERIAL': '00258',
                               'SERIAL_PI1': '10000000f879d427',
                               'SERIAL_PI2': '100000007b8927d4',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:e7:0b:db',
                               'MAC_PI2': 'dc:a6:32:e6:ff:ee',
                               'PROJ_MODEL': 'C6'})
        self.setupList.append({'SERIAL': '00259',
                               'SERIAL_PI1': '100000004524b330',
                               'SERIAL_PI2': '100000001ecdbecd',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:e7:0a:0c',
                               'MAC_PI2': 'dc:a6:32:e7:0a:0f',
                               'PROJ_MODEL': 'C6_V2'})
        self.setupList.append({'SERIAL': '00260',
                               'SERIAL_PI1': '100000009b9a183e',
                               'SERIAL_PI2': '1000000059ad4297',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:e7:08:c3',
                               'MAC_PI2': 'dc:a6:32:e7:0c:0d',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '15'})
        self.setupList.append({'SERIAL': '00261',
                               'SERIAL_PI1': '100000006aa7af20',
                               'SERIAL_PI2': '100000007ac4b050',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:e7:0b:96',
                               'MAC_PI2': 'dc:a6:32:e7:0b:99',
                               'PROJ_MODEL': 'C6_V2',
                               "LEVELLER": 'ARD',
                               "LENSES": '6mm',
                               "TYPE": 'DENTAL',
                               'WIFI_READY': 'Y'})

        self.setupList.append({'SERIAL': '00262',
                               'SERIAL_PI1': '1000000077850f7d',
                               'SERIAL_PI2': '10000000eabae5cf',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:01:c0:4d',
                               'MAC_PI2': 'dc:a6:32:01:5c:97',
                               'PROJ_MODEL': 'C6_V2',
                               "LEVELLER": 'ARD',
                               "LENSES": '6mm',
                               "TYPE": 'DENTAL',
                               'WIFI_READY': 'Y'})

        self.setupList.append({'SERIAL': '00263',
                               'SERIAL_PI1': '10000000899969d5',
                               'SERIAL_PI2': '100000005a33189c',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:b6:fb',
                               'MAC_PI2': 'dc:a6:32:9f:b6:95',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'GP',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00264',
                               'SERIAL_PI1': '10000000bad995da',
                               'SERIAL_PI2': '1000000042ef6c0f',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:01:63:82',
                               'MAC_PI2': 'dc:a6:32:01:b3:39',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00265',
                               'SERIAL_PI1': '100000004ce9c381',
                               'SERIAL_PI2': '1000000012041648',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:01:66:7d',
                               'MAC_PI2': 'dc:a6:32:01:c0:20',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'GP',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00266',
                               'SERIAL_PI1': '10000000915a6683',
                               'SERIAL_PI2': '10000000f1b7ee90',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:01:65:e1',
                               'MAC_PI2': 'dc:a6:32:01:5c:70',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'GP',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00267',
                               'SERIAL_PI1': '1000000081b053a9',
                               'SERIAL_PI2': '100000001e42c0ba',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:b6:e6',
                               'MAC_PI2': 'dc:a6:32:9f:b7:13',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00268',
                               'SERIAL_PI1': '100000003bcb485a',
                               'SERIAL_PI2': '10000000e8de0f69',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:dc:ab',
                               'MAC_PI2': 'dc:a6:32:9f:dc:86',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'GP',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00269',
                               'SERIAL_PI1': '10000000a4b5a2aa',
                               'SERIAL_PI2': '100000007d02d78a',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:b6:f2',
                               'MAC_PI2': 'dc:a6:32:9f:b7:0a',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'GP',
                               'WIFI_READY': 'Y',
                               'CODE':'7'})
        self.setupList.append({'SERIAL': '00270',
                               'SERIAL_PI1': '10000000b959950a',
                               'SERIAL_PI2': '10000000b763e64e',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:dc:a8',
                               'MAC_PI2': 'dc:a6:32:9f:dc:93',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00271',
                               'SERIAL_PI1': '100000005410207c',
                               'SERIAL_PI2': '10000000154884ab',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:dc:12',
                               'MAC_PI2': 'dc:a6:32:9f:b6:b6',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})

        self.setupList.append({'SERIAL': '00272',
                               'SERIAL_PI1': '1000000036012287',
                               'SERIAL_PI2': '10000000baf50541',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:e7:01:11',
                               'MAC_PI2': 'dc:a6:32:e7:0b:fa',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00273',
                               'SERIAL_PI1': '1000000096c1f3c0',
                               'SERIAL_PI2': '1000000077b3c13a',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:e7:0b:1e',
                               'MAC_PI2': 'dc:a6:32:e6:d3:2a',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00274',
                               'SERIAL_PI1': '10000000d0e4e081',
                               'SERIAL_PI2': '1000000083861a45',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:e7:00:ba',
                               'MAC_PI2': 'dc:a6:32:e7:0b:f1',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'GP',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00275',
                               'SERIAL_PI1': '10000000d09d6f43',
                               'SERIAL_PI2': '1000000017150326',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:e7:0b:6f',
                               'MAC_PI2': 'dc:a6:32:e7:0b:c3',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00276',
                               'SERIAL_PI1': '100000002bec2fd8',
                               'SERIAL_PI2': '10000000675f4c12',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:e7:0b:fd',
                               'MAC_PI2': 'dc:a6:32:e7:0b:cc',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'GP',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00277',
                               'SERIAL_PI1': '10000000647cf924',
                               'SERIAL_PI2': '10000000228a1efe',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:e7:0b:15',
                               'MAC_PI2': 'dc:a6:32:e7:0b:57',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00278',
                               'SERIAL_PI1': '100000000305783b',
                               'SERIAL_PI2': '100000007b2bdf0b',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:37:74',
                               'MAC_PI2': 'dc:a6:32:f2:39:3c',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'GP',
                               'WIFI_READY': 'Y',
                               'CODE': '7'})
        self.setupList.append({'SERIAL': '00279',
                               'SERIAL_PI1': '100000007d85025d',
                               'SERIAL_PI2': '100000003b3c32d8',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:e7:09:95',
                               'MAC_PI2': 'dc:a6:32:e7:09:ec',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'GP',
                               'WIFI_READY': 'Y',
                               'CODE': '7'})
        self.setupList.append({'SERIAL': '00280',
                               'SERIAL_PI1': '1000000051050596',
                               'SERIAL_PI2': '10000000750c0ab4',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:e7:0b:32',
                               'MAC_PI2': 'dc:a6:32:e7:0c:05',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'GP',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00281',
                               'SERIAL_PI1': '10000000b360ff93',
                               'SERIAL_PI2': '100000009c12b0eb',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:37:6b',
                               'MAC_PI2': 'dc:a6:32:f2:38:55',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})

        self.setupList.append({'SERIAL': '00282',
                               'SERIAL_PI1': '10000000275b05e3',
                               'SERIAL_PI2': '100000004a587188',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:b7:0d',
                               'MAC_PI2': 'dc:a6:32:9f:b6:ec',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})

        self.setupList.append({'SERIAL': '00283',
                               'SERIAL_PI1': '100000001d4b7ad0',
                               'SERIAL_PI2': '10000000c770f92c',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:e7:0b:50',
                               'MAC_PI2': 'dc:a6:32:e7:06:07',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '7'})
        self.setupList.append({'SERIAL': '00284',
                               'SERIAL_PI1': '10000000766c572e',
                               'SERIAL_PI2': '10000000767aa8cb',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:e7:0b:7b',
                               'MAC_PI2': 'dc:a6:32:e7:0b:2f',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00285',
                               'SERIAL_PI1': '100000008daf9a35',
                               'SERIAL_PI2': '10000000cbba16b6',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:dc:90',
                               'MAC_PI2': 'dc:a6:32:9f:dc:71',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00286',
                               'SERIAL_PI1': '100000008510c890',
                               'SERIAL_PI2': '100000001b7922c5',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:ae:2e',
                               'MAC_PI2': 'dc:a6:32:9f:c2:0e',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00287',
                               'SERIAL_PI1': '100000004b4ab033',
                               'SERIAL_PI2': '1000000070facee4',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:c0:b5',
                               'MAC_PI2': 'dc:a6:32:9f:dc:a2',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00288',
                               'SERIAL_PI1': '100000007a1ecf2c',
                               'SERIAL_PI2': '10000000f880c3cf',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:dc:61',
                               'MAC_PI2': 'dc:a6:32:9f:ae:7f',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00289',
                               'SERIAL_PI1': '10000000dc3cdaf4',
                               'SERIAL_PI2': '1000000012ac0fe1',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:e7:0b:d0',
                               'MAC_PI2': 'dc:a6:32:e7:09:ff',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00290',
                               'SERIAL_PI1': '10000000490686ee',
                               'SERIAL_PI2': '10000000b7f8f736',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:e7:0b:a2',
                               'MAC_PI2': 'dc:a6:32:e7:0b:90',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00291',
                               'SERIAL_PI1': '10000000816a526e',
                               'SERIAL_PI2': '10000000c08a628b',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:e7:0b:a5',
                               'MAC_PI2': 'dc:a6:32:e7:0b:ba',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})


        self.setupList.append({'SERIAL': '00292',
                               'SERIAL_PI1': '10000000b0d64a8a',
                               'SERIAL_PI2': '10000000f0ddb48c',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:dc:c9',
                               'MAC_PI2': 'dc:a6:32:9f:b6:ce',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'GP',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00293',
                               'SERIAL_PI1': '10000000d46e3e2c',
                               'SERIAL_PI2': '10000000bd596c7e',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:b6:a7',
                               'MAC_PI2': 'dc:a6:32:9f:b6:9e',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'GP',
                               'WIFI_READY': 'Y',
                               'CODE': '7'})
        self.setupList.append({'SERIAL': '00294',
                               'SERIAL_PI1': '1000000092301652',
                               'SERIAL_PI2': '100000000ceea827',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9b:87:23',
                               'MAC_PI2': 'dc:a6:32:9f:dc:cf',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'GP',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00295',
                               'SERIAL_PI1': '10000000ed772ce0',
                               'SERIAL_PI2': '100000006cbc1b48',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:b6:c2',
                               'MAC_PI2': 'dc:a6:32:9f:b6:98',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00296',
                               'SERIAL_PI1': '100000008abe38f4',
                               'SERIAL_PI2': '10000000ab1d45b6',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:dc:c0',
                               'MAC_PI2': 'dc:a6:32:9f:b6:d7',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00297',
                               'SERIAL_PI1': '10000000e7faade9',
                               'SERIAL_PI2': '10000000240b8e31',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:dc:ca',
                               'MAC_PI2': 'dc:a6:32:9f:b6:c5',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'GP',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00298',
                               'SERIAL_PI1': '100000004ee8b17a',
                               'SERIAL_PI2': '1000000056408a6d',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:bf:a4',
                               'MAC_PI2': 'dc:a6:32:9f:b6:e3',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'GP',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00299',
                               'SERIAL_PI1': '10000000d19ea5df',
                               'SERIAL_PI2': '100000005704c2a1',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:b7:22',
                               'MAC_PI2': 'dc:a6:32:9f:dc:36',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'GP',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00300',
                               'SERIAL_PI1': '10000000d672b74c',
                               'SERIAL_PI2': '100000006c781bfa',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:b6:8c',
                               'MAC_PI2': 'dc:a6:32:9f:b6:e9',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'GP',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00301',
                               'SERIAL_PI1': '10000000e276cb8b',
                               'SERIAL_PI2': '1000000016030386',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:b3:4a',
                               'MAC_PI2': 'dc:a6:32:9f:b6:da',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'GP',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00302',
                               'SERIAL_PI1': '10000000f56fe84c',
                               'SERIAL_PI2': '10000000bf21042c',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:43:e7:03',
                               'MAC_PI2': 'dc:a6:32:44:42:b8',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00303',
                               'SERIAL_PI1': '100000006c4e32d2',
                               'SERIAL_PI2': '1000000032bb932e',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:b2:f3',
                               'MAC_PI2': 'dc:a6:32:9f:b2:93',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'GP',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00304',
                               'SERIAL_PI1': '1000000030096d24',
                               'SERIAL_PI2': '10000000670f4d71',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:b2:d5',
                               'MAC_PI2': 'dc:a6:32:9f:b6:83',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'GP',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00305',
                               'SERIAL_PI1': '10000000c736d386',
                               'SERIAL_PI2': '1000000075dd5fde',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:b6:c6',
                               'MAC_PI2': 'dc:a6:32:9f:b6:92',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'GP',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00306',
                               'SERIAL_PI1': '10000000b8a968f5',
                               'SERIAL_PI2': '100000000a4abb6e',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:b1:b5',
                               'MAC_PI2': 'dc:a6:32:9f:b2:cf',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00307',
                               'SERIAL_PI1': '10000000c8689dad',
                               'SERIAL_PI2': '10000000ab50cbca',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:b2:a1',
                               'MAC_PI2': 'dc:a6:32:9f:b6:77',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00308',
                               'SERIAL_PI1': '1000000003dcb2c4',
                               'SERIAL_PI2': '10000000853dc457',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:44:11:53',
                               'MAC_PI2': 'dc:a6:32:9f:b6:b3',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00309',
                               'SERIAL_PI1': '100000004ff72b68',
                               'SERIAL_PI2': '10000000707ad53e',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:b6:ac',
                               'MAC_PI2': 'dc:a6:32:9f:b6:aa',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00310',
                               'SERIAL_PI1': '100000006284e39a',
                               'SERIAL_PI2': '100000007ef32ff4',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:b2:e7',
                               'MAC_PI2': 'dc:a6:32:9f:ae:49',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00311',
                               'SERIAL_PI1': '10000000b3937261',
                               'SERIAL_PI2': '100000008daf7805',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:38:22',
                               'MAC_PI2': 'dc:a6:32:e7:08:1a',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'MARKER',
                               'LENSES': '3mm',
                               'TYPE': 'BSB',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00312',#ELUXE
                               'SERIAL_PI1': '100000008ad6817f',
                               'SERIAL_PI2': '10000000f91da5b7',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:86:7d:cc',
                               'MAC_PI2': 'e4:5f:01:86:8f:83',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               "CODE": '6' })


        self.setupList.append({'SERIAL': '00314',
                               'SERIAL_PI1': '10000000e588985e',
                               'SERIAL_PI2': '1000000011e7c597',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:86:82:f8',
                               'MAC_PI2': 'e4:5f:01:86:81:08',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '7'})

        self.setupList.append({'SERIAL': '00315',
                               'SERIAL_PI1': '100000009e35538a',
                               'SERIAL_PI2': '100000006f01ba22',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:b6:6e',
                               'MAC_PI2': 'dc:a6:32:9f:b6:a1',
                               'PROJ_MODEL': 'C6',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00316',
                               'SERIAL_PI1': '100000001d722401',
                               'SERIAL_PI2': '1000000018b77376',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:b6:8f',
                               'MAC_PI2': 'dc:a6:32:9f:b2:ea',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00317',
                               'SERIAL_PI1': '10000000bc54a648',
                               'SERIAL_PI2': '100000001ed693fc',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:38:82',
                               'MAC_PI2': 'dc:a6:32:59:49:50',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'GP',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00318',
                               'SERIAL_PI1': '10000000f0bc7aae',
                               'SERIAL_PI2': '1000000032c07e58',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:85:9b:d3',
                               'MAC_PI2': 'dc:a6:32:59:49:44',
                               'PROJ_MODEL': 'C6_V2',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00319',
                               'SERIAL_PI1': '100000000e521394',
                               'SERIAL_PI2': '10000000893c9070',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:9f:b6:bc',
                               'MAC_PI2': 'dc:a6:32:9f:b2:d8',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00320',
                               'SERIAL_PI1': '100000007b75f043',
                               'SERIAL_PI2': '1000000093b75e05',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:7a:d9:ec',
                               'MAC_PI2': 'e4:5f:01:7a:da:07',
                               'PROJ_MODEL': 'C6',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00321',
                               'SERIAL_PI1': '100000005d5c1a17',
                               'SERIAL_PI2': '1000000082e96caf',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:9a:5f:25',
                               'MAC_PI2': 'e4:5f:01:9a:60:96',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})

        self.setupList.append({'SERIAL': '00322',
                               'SERIAL_PI1': '10000000d51154fb',
                               'SERIAL_PI2': '1000000099680cdb',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:7a:da:25',
                               'MAC_PI2': 'e4:5f:01:9a:60:98',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00323',
                               'SERIAL_PI1': '100000009261e050',
                               'SERIAL_PI2': '1000000054ab610c',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:f2:38:74',
                               'MAC_PI2': 'dc:a6:32:f2:38:dd',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})

        self.setupList.append({'SERIAL': '00325',
                               'SERIAL_PI1': '10000000a4f47b4a',
                               'SERIAL_PI2': '10000000eece842b',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'dc:a6:32:e7:0b:9f',
                               'MAC_PI2': 'dc:a6:32:e7:0b:47',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})

        self.setupList.append({'SERIAL': '00326',
                               'SERIAL_PI1': '100000002e474290',
                               'SERIAL_PI2': '1000000014686232',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:9a:60:60',
                               'MAC_PI2': 'e4:5f:01:7a:d9:dd',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00327',
                               'SERIAL_PI1': '1000000093f49809',
                               'SERIAL_PI2': '10000000dfaffb26',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:9a:60:aa',
                               'MAC_PI2': 'e4:5f:01:7a:d9:b9',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '7'})
        self.setupList.append({'SERIAL': '00328',
                               'SERIAL_PI1': '100000008882fe9e',
                               'SERIAL_PI2': '10000000f14f6968',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:9a:60:a4',
                               'MAC_PI2': 'e4:5f:01:9a:5e:79',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00329',
                               'SERIAL_PI1': '10000000330a109c',
                               'SERIAL_PI2': '100000000b2adf63',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:9a:5f:c0',
                               'MAC_PI2': 'e4:5f:01:9a:5e:35',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00330',
                               'SERIAL_PI1': '100000003372ab5b',
                               'SERIAL_PI2': '100000001b20a25e',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:8f:e6:c8',
                               'MAC_PI2': 'e4:5f:01:8f:b6:99',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00331',
                               'SERIAL_PI1': '100000009d41eb1a',
                               'SERIAL_PI2': '10000000bf9bccfd',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:9a:5f:8b',
                               'MAC_PI2': 'e4:5f:01:9a:60:57',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00332',
                               'SERIAL_PI1': '100000005218fceb',
                               'SERIAL_PI2': '10000000d2e89cee',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:9a:60:31',
                               'MAC_PI2': 'e4:5f:01:9a:60:5a',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00333',
                               'SERIAL_PI1': '100000009329aa42',
                               'SERIAL_PI2': '10000000b57c1b0e',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:7a:d9:f8',
                               'MAC_PI2': 'e4:5f:01:7a:d9:fe',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00334',
                               'SERIAL_PI1': '100000000510b92c',
                               'SERIAL_PI2': '10000000ab7ae0ca',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:7a:da:0a',
                               'MAC_PI2': 'e4:5f:01:9a:60:c1',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00335',
                               'SERIAL_PI1': '100000001eb79205',
                               'SERIAL_PI2': '1000000073616c3c',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:9a:60:d1',
                               'MAC_PI2': 'e4:5f:01:9a:60:41',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00336',
                               'SERIAL_PI1': '1000000076f0a81d',
                               'SERIAL_PI2': '100000007aea20f6',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:9a:60:1f',
                               'MAC_PI2': 'e4:5f:01:9a:5e:7d',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})

        self.setupList.append({'SERIAL': '00337',
                               'SERIAL_PI1': '10000000051e3f5b',
                               'SERIAL_PI2': '1000000065fb8d11',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:9a:60:e5',
                               'MAC_PI2': 'e4:5f:01:9a:60:54',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '7'})

        self.setupList.append({'SERIAL': '00339',
                               'SERIAL_PI1': '10000000031cd122',
                               'SERIAL_PI2': '10000000068fbec4',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:8f:e8:aa',
                               'MAC_PI2': 'e4:5f:01:8f:e6:71',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})

        self.setupList.append({'SERIAL': '00340',
                               'SERIAL_PI1': '10000000f430f35e',
                               'SERIAL_PI2': '10000000b8da0128',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:9a:60:d4',
                               'MAC_PI2': 'e4:5f:01:9a:5f:46',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})

        self.setupList.append({'SERIAL': '00341',
                               'SERIAL_PI1': '1000000016d3bf43',
                               'SERIAL_PI2': '10000000eacefe9b',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:9a:60:f7',
                               'MAC_PI2': 'e4:5f:01:7a:da:0d',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00342',
                               'SERIAL_PI1': '10000000d46bf4a0',
                               'SERIAL_PI2': '100000005ecd885c',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:9a:60:68',
                               'MAC_PI2': 'e4:5f:01:9a:60:48',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})

        self.setupList.append({'SERIAL': '00343',
                               'SERIAL_PI1': '1000000012af8db7',
                               'SERIAL_PI2': '1000000064ad6fe2',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:9a:60:c0',
                               'MAC_PI2': 'e4:5f:01:9a:60:0a',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})

        self.setupList.append({'SERIAL': '00344',
                               'SERIAL_PI1': '10000000ce16790b',
                               'SERIAL_PI2': '10000000b9f0bb27',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:84:4f:de',
                               'MAC_PI2': 'e4:5f:01:9a:5f:a6',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00345',#eluxe
                               'SERIAL_PI1': '1000000027d1881d',
                               'SERIAL_PI2': '10000000b2d4aa29',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:8f:e6:89',
                               'MAC_PI2': 'e4:5f:01:8f:aa:d5',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '0'})
        self.setupList.append({'SERIAL': '00347',
                               'SERIAL_PI1': '1000000070e444d4',
                               'SERIAL_PI2': '10000000c80d7b1d',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:bf:2c:7a',
                               'MAC_PI2': 'e4:5f:01:bf:27:7c',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00348',
                               'SERIAL_PI1': '100000002f932f78',
                               'SERIAL_PI2': '100000000509e99a',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:7a:d9:e3',
                               'MAC_PI2': 'e4:5f:01:7a:d9:d1',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00349',
                               'SERIAL_PI1': '10000000d11db4a7',
                               'SERIAL_PI2': '1000000082a1d506',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:bf:2b:4e',
                               'MAC_PI2': 'e4:5f:01:7a:da:17',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00350',
                               'SERIAL_PI1': '100000000a55effc',
                               'SERIAL_PI2': '10000000ce28a944',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:bf:2b:4b',
                               'MAC_PI2': 'e4:5f:01:bf:2a:91',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00351',
                               'SERIAL_PI1': '100000008b8aa708',
                               'SERIAL_PI2': '1000000045b4ffdd',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:bf:2b:1b',
                               'MAC_PI2': 'e4:5f:01:7a:da:13',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00352',
                               'SERIAL_PI1': '10000000fc2faa70',
                               'SERIAL_PI2': '10000000116957f5',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:9a:60:b8',
                               'MAC_PI2': 'e4:5f:01:bf:2b:37',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00353',
                               'SERIAL_PI1': '10000000f61739c6',
                               'SERIAL_PI2': '100000003edee7f8',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:9a:60:0d',
                               'MAC_PI2': 'e4:5f:01:9a:5f:e8',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00354',
                               'SERIAL_PI1': '10000000fd5cdce7',
                               'SERIAL_PI2': '100000008199846d',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:7a:d9:e9',
                               'MAC_PI2': 'e4:5f:01:7a:d9:d7',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00355',
                               'SERIAL_PI1': '1000000041ce3f6f',
                               'SERIAL_PI2': '100000008ca29890',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:7a:d9:ef',
                               'MAC_PI2': 'e4:5f:01:7a:da:10',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00356',
                               'SERIAL_PI1': '100000006f1fdeb4',
                               'SERIAL_PI2': '1000000031689060',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:50:18',
                               'MAC_PI2': 'e4:5f:01:ce:50:54',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})
        self.setupList.append({'SERIAL': '00357',
                               'SERIAL_PI1': '10000000883f37ac',
                               'SERIAL_PI2': '1000000065f84d54',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:7a:d9:e0',
                               'MAC_PI2': 'e4:5f:01:bf:2b:21',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE':'14'})#metal holders, gp and dental, no pg
        self.setupList.append({'SERIAL': '00358',
                               'SERIAL_PI1': '10000000d5fe0111',
                               'SERIAL_PI2': '1000000060f0e6a2',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4f:ee',
                               'MAC_PI2': 'e4:5f:01:ce:50:3f',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00359',
                               'SERIAL_PI1': '10000000289f3b32',
                               'SERIAL_PI2': '100000009002b7ae',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:7a:d0:07',
                               'MAC_PI2': 'e4:5f:01:7a:cf:96',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00360',
                               'SERIAL_PI1': '1000000003ac3b51',
                               'SERIAL_PI2': '10000000d2e2a2de',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:bf:2b:ab',
                               'MAC_PI2': 'e4:5f:01:7a:da:1c',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00361',
                               'SERIAL_PI1': '100000006f2655cf',
                               'SERIAL_PI2': '1000000000d29bb5',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:50:36',
                               'MAC_PI2': 'e4:5f:01:ce:50:15',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00362',
                               'SERIAL_PI1': '100000008d4ded56',
                               'SERIAL_PI2': '1000000006b1ed29',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:bf:2b:7b',
                               'MAC_PI2': 'e4:5f:01:9e:84:89',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00363',
                               'SERIAL_PI1': '100000009dbf0dd6',
                               'SERIAL_PI2': '10000000f9fb6266',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:50:84',
                               'MAC_PI2': 'e4:5f:01:ce:50:66',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00364',
                               'SERIAL_PI1': '10000000c6e06cd9',
                               'SERIAL_PI2': '1000000057f6ba80',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:bf:2b:00',
                               'MAC_PI2': 'e4:5f:01:bf:2b:57',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '15'})
        self.setupList.append({'SERIAL': '00365',
                               'SERIAL_PI1': '100000008b89c239',
                               'SERIAL_PI2': '10000000cea4f09b',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:50:90',
                               'MAC_PI2': 'e4:5f:01:ce:50:8a',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00366',
                               'SERIAL_PI1': '100000000cecb210',
                               'SERIAL_PI2': '10000000214afe30',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:50:6f',
                               'MAC_PI2': 'e4:5f:01:ce:50:60',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00367',
                               'SERIAL_PI1': '10000000841d9308',
                               'SERIAL_PI2': '1000000082a86ec7',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:bf:2b:27',
                               'MAC_PI2': 'e4:5f:01:7a:d9:74',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00368',
                               'SERIAL_PI1': '10000000d16e9fbb',
                               'SERIAL_PI2': '10000000f48c6111',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:7a:da:00',
                               'MAC_PI2': 'e4:5f:01:7a:da:1f',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00369',
                               'SERIAL_PI1': '10000000dc7c7de0',
                               'SERIAL_PI2': '10000000a5914ffb',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:7a:da:31',
                               'MAC_PI2': 'e4:5f:01:b3:2e:6f',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00371',
                               'SERIAL_PI1': '1000000024c680aa',
                               'SERIAL_PI2': '10000000de187701',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4f:fd',
                               'MAC_PI2': 'e4:5f:01:ce:4f:f7',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00372',
                               'SERIAL_PI1': '10000000ee041a3e',
                               'SERIAL_PI2': '100000009c7b2a27',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4e:d4',
                               'MAC_PI2': 'e4:5f:01:ce:50:9c',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00373',
                               'SERIAL_PI1': '100000004e774ba8',
                               'SERIAL_PI2': '10000000faed8549',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:50:0c',
                               'MAC_PI2': 'e4:5f:01:ce:50:72',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00374',
                               'SERIAL_PI1': '100000008ed6c3eb',
                               'SERIAL_PI2': '1000000065a60569',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4f:67',
                               'MAC_PI2': 'e4:5f:01:ce:4f:7c',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00375',
                               'SERIAL_PI1': '10000000a015655c',
                               'SERIAL_PI2': '10000000a75dae22',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:50:2a',
                               'MAC_PI2': 'e4:5f:01:ce:50:7b',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00376',
                               'SERIAL_PI1': '10000000e6cc73a4',
                               'SERIAL_PI2': '10000000be6570c2',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4f:be',
                               'MAC_PI2': 'e4:5f:01:ce:4f:d0',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00377',
                               'SERIAL_PI1': '10000000662799e3',
                               'SERIAL_PI2': '100000002652716d',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:50:00',
                               'MAC_PI2': 'e4:5f:01:ce:50:93',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00378',
                               'SERIAL_PI1': '100000007fdc90cc',
                               'SERIAL_PI2': '100000004a68c89e',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:50:42',
                               'MAC_PI2': 'e4:5f:01:ce:50:4e',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00379',
                               'SERIAL_PI1': '10000000e287a2f0',
                               'SERIAL_PI2': '10000000f3799028',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4f:d3',
                               'MAC_PI2': 'e4:5f:01:ce:4f:ca',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00380',
                               'SERIAL_PI1': '100000004770bacb',
                               'SERIAL_PI2': '10000000bd4d5b7e',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:50:09',
                               'MAC_PI2': 'e4:5f:01:ce:50:1b',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00381',
                               'SERIAL_PI1': '10000000d93c292a',
                               'SERIAL_PI2': '100000003bbe634f',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:50:03',
                               'MAC_PI2': 'e4:5f:01:ce:50:5a',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00382',
                               'SERIAL_PI1': '1000000085d4856c',
                               'SERIAL_PI2': '100000002709a412',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:bf:2b:87',
                               'MAC_PI2': 'e4:5f:01:bf:2b:d2',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00383',
                               'SERIAL_PI1': '1000000096db30f8',
                               'SERIAL_PI2': '1000000086e899d9',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:50:27',
                               'MAC_PI2': 'e4:5f:01:ce:50:24',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00384',
                               'SERIAL_PI1': '100000008a913d87',
                               'SERIAL_PI2': '100000006da9de0a',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4f:16',
                               'MAC_PI2': 'e4:5f:01:ce:4f:b2',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00385',
                               'SERIAL_PI1': '10000000a03c94aa',
                               'SERIAL_PI2': '10000000fed00c5a',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4f:b8',
                               'MAC_PI2': 'e4:5f:01:ce:4f:73',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00386',
                               'SERIAL_PI1': '1000000021e6714f',
                               'SERIAL_PI2': '10000000f18ca5a0',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4f:a3',
                               'MAC_PI2': 'e4:5f:01:ce:50:30',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00387',
                               'SERIAL_PI1': '10000000a2b63094',
                               'SERIAL_PI2': '100000008655abf7',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4f:8e',
                               'MAC_PI2': 'e4:5f:01:ce:4f:b5',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00388',
                               'SERIAL_PI1': '100000008f0da87d',
                               'SERIAL_PI2': '10000000fd029147',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:50:06',
                               'MAC_PI2': 'e4:5f:01:ce:4f:f1',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '000389',
                               'SERIAL_PI1': '10000000c7b2f623',
                               'SERIAL_PI2': '1000000011b3380c',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4d:ae',
                               'MAC_PI2': 'e4:5f:01:ce:4f:91',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00390',
                               'SERIAL_PI1': '100000003f88e027',
                               'SERIAL_PI2': '100000003d00de90',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4f:88',
                               'MAC_PI2': 'e4:5f:01:ce:4f:a0',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00391',
                               'SERIAL_PI1': '10000000ff279b78',
                               'SERIAL_PI2': '10000000cacff265',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:50:2b',
                               'MAC_PI2': 'e4:5f:01:ce:50:1d',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00392',
                               'SERIAL_PI1': '100000006519e030',
                               'SERIAL_PI2': '1000000088a69687',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4f:e8',
                               'MAC_PI2': 'e4:5f:01:ce:4f:e5',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00393',
                               'SERIAL_PI1': '100000006603987e',
                               'SERIAL_PI2': '1000000030afd78d',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:50:51',
                               'MAC_PI2': 'e4:5f:01:ce:50:4b',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00394',
                               'SERIAL_PI1': '1000000073e6f1c6',
                               'SERIAL_PI2': '100000002ae3e753',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4f:dc',
                               'MAC_PI2': 'e4:5f:01:ce:4f:c3',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00395',
                               'SERIAL_PI1': '10000000c932662d',
                               'SERIAL_PI2': '100000000f68f950',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4f:28',
                               'MAC_PI2': 'e4:5f:01:ce:4f:df',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00396',
                               'SERIAL_PI1': '1000000075dc9c51',
                               'SERIAL_PI2': '10000000d4b3d732',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:50:6c',
                               'MAC_PI2': 'e4:5f:01:ce:50:44',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})
        self.setupList.append({'SERIAL': '00397',
                               'SERIAL_PI1': '100000003fc7f24a',
                               'SERIAL_PI2': '10000000494c39b4',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4f:31',
                               'MAC_PI2': 'e4:5f:01:ce:4e:ef',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '00398',
                               'SERIAL_PI1': '100000008632795b',
                               'SERIAL_PI2': '1000000065b300d8',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4f:6a',
                               'MAC_PI2': 'e4:5f:01:ce:4f:70',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '00399',
                               'SERIAL_PI1': '10000000428949ba',
                               'SERIAL_PI2': '10000000d4596693',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4e:08',
                               'MAC_PI2': 'e4:5f:01:ce:4d:ba',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '00400',
                               'SERIAL_PI1': '10000000db4a4e18',
                               'SERIAL_PI2': '10000000b9b52741',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4f:6d',
                               'MAC_PI2': 'e4:5f:01:ce:4f:55',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '00401',
                               'SERIAL_PI1': '10000000dcb44a1a',
                               'SERIAL_PI2': '1000000077dd3f47',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4f:94',
                               'MAC_PI2': 'e4:5f:01:ce:4e:f2',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '00402',
                               'SERIAL_PI1': '100000002351d16c',
                               'SERIAL_PI2': '10000000b3225d77',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4f:64',
                               'MAC_PI2': 'e4:5f:01:ce:4d:ed',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '00403',
                               'SERIAL_PI1': '1000000008e86dee',
                               'SERIAL_PI2': '100000000d0d80e4',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4f:8b',
                               'MAC_PI2': 'e4:5f:01:ce:4f:76',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '00404',
                               'SERIAL_PI1': '10000000b934834c',
                               'SERIAL_PI2': '10000000809b8126',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4f:46',
                               'MAC_PI2': 'e4:5f:01:ce:4f:99',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '00405',
                               'SERIAL_PI1': '100000009343f3e9',
                               'SERIAL_PI2': '10000000a0ee3f74',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4f:7f',
                               'MAC_PI2': 'e4:5f:01:ce:4f:ad',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '00406',
                               'SERIAL_PI1': '10000000b3a5a2ac',
                               'SERIAL_PI2': '1000000006cfa8b3',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4d:87',
                               'MAC_PI2': 'e4:5f:01:ce:4f:ac',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '00407',
                               'SERIAL_PI1': '10000000d5b45a9b',
                               'SERIAL_PI2': '100000002a370d8e',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4f:9d',
                               'MAC_PI2': 'e4:5f:01:ce:4f:85',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '15'})

        self.setupList.append({'SERIAL': '00408',
                               'SERIAL_PI1': '10000000d447ac50',
                               'SERIAL_PI2': '10000000ddde5d0d',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4f:40',
                               'MAC_PI2': 'e4:5f:01:ce:4f:52',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '15'})

        self.setupList.append({'SERIAL': '05002',
                               'SERIAL_PI1': '1000000008354dd3',
                               'SERIAL_PI2': '10000000eddb6d31',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:7e:1b:02',
                               'MAC_PI2': 'e4:5f:01:a4:0d:7d',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y'})

        self.setupList.append({'SERIAL': '05003',#eluxe built
                               'SERIAL_PI1': '100000009aa552d9',
                               'SERIAL_PI2': '10000000750a7528',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:a4:17:46',
                               'MAC_PI2': 'd8:3a:dd:a4:17:2e',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})#14 is all but pg

        self.setupList.append({'SERIAL': '05004',
                               'SERIAL_PI1': '10000000aaa10f5c',
                               'SERIAL_PI2': '1000000051423093',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:a4:16:83',
                               'MAC_PI2': 'd8:3a:dd:a4:16:b8',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05005',
                               'SERIAL_PI1': '10000000cf865f2d',
                               'SERIAL_PI2': '1000000004890c1e',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:a4:16:86',
                               'MAC_PI2': 'd8:3a:dd:a4:15:6c',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05006',
                               'SERIAL_PI1': '1000000012cf7e4c',
                               'SERIAL_PI2': '10000000686ccf25',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:a4:16:a7',
                               'MAC_PI2': 'd8:3a:dd:a4:16:c7',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05007',
                               'SERIAL_PI1': '10000000f359ef2f',
                               'SERIAL_PI2': '10000000ede2f799',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:a4:16:29',
                               'MAC_PI2': 'd8:3a:dd:a4:16:ad',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05008',
                               'SERIAL_PI1': '10000000f6625252',
                               'SERIAL_PI2': '1000000099627885',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:a4:16:7a',
                               'MAC_PI2': 'd8:3a:dd:a4:17:2b',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05009',
                               'SERIAL_PI1': '10000000d898dfd9',
                               'SERIAL_PI2': '10000000f805d06e',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:a4:15:b7',
                               'MAC_PI2': 'd8:3a:dd:a4:16:99',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05010',
                               'SERIAL_PI1': '1000000093044723',
                               'SERIAL_PI2': '10000000ed9a3be3',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:a4:16:dc',
                               'MAC_PI2': 'e4:5f:01:ce:50:87',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05011',
                               'SERIAL_PI1': '1000000000e24926',
                               'SERIAL_PI2': '10000000dbacd04a',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:a4:16:65',
                               'MAC_PI2': 'd8:3a:dd:a4:15:f6',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05012',
                               'SERIAL_PI1': '100000000033fb08',
                               'SERIAL_PI2': '10000000ca051e86',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:a4:17:1d',
                               'MAC_PI2': 'd8:3a:dd:a4:16:6b',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05013',
                               'SERIAL_PI1': '100000004ef82de3',
                               'SERIAL_PI2': '1000000048606af3',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:a4:16:c2',
                               'MAC_PI2': 'd8:3a:dd:a4:17:3a',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05014',
                               'SERIAL_PI1': '10000000e13ce517',
                               'SERIAL_PI2': '100000001f4016cb',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:a4:16:7f',
                               'MAC_PI2': 'd8:3a:dd:a4:14:a3',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05015',
                               'SERIAL_PI1': '100000000af222b2',
                               'SERIAL_PI2': '100000004be52434',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:a4:16:bc',
                               'MAC_PI2': 'd8:3a:dd:a4:15:fd',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05016',
                               'SERIAL_PI1': '10000000da2ebf7a',
                               'SERIAL_PI2': '10000000f4e1c458',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:a4:16:d7',
                               'MAC_PI2': 'd8:3a:dd:a4:17:07',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05017',
                               'SERIAL_PI1': '100000009f52ff78',
                               'SERIAL_PI2': '1000000074443f2b',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:a4:16:e9',
                               'MAC_PI2': 'd8:3a:dd:a4:17:1f',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05018',
                               'SERIAL_PI1': '10000000530e7747',
                               'SERIAL_PI2': '100000003de1d5bd',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:a4:16:c5',
                               'MAC_PI2': 'd8:3a:dd:a4:16:fe',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05019',
                               'SERIAL_PI1': '10000000f616a2ef',
                               'SERIAL_PI2': '1000000003c41c7f',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:a4:16:75',
                               'MAC_PI2': 'd8:3a:dd:a4:10:aa',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05020',
                               'SERIAL_PI1': '1000000011a9faf8',
                               'SERIAL_PI2': '10000000cd3f3886',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',

                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ec:b3:47',
                               'MAC_PI2': 'd8:3a:dd:ec:af:11',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05021',
                               'SERIAL_PI1': '100000001d5c0d8f',
                               'SERIAL_PI2': '1000000059704c45',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',

                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ec:b1:b3',
                               'MAC_PI2': 'd8:3a:dd:ec:b3:0f',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05022',
                               'SERIAL_PI1': '100000006ae1112a',
                               'SERIAL_PI2': '100000000e14f2e6',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',

                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:a4:14:71',
                               'MAC_PI2': 'd8:3a:dd:a4:17:0d',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05023',
                               'SERIAL_PI1': '10000000cc71e109',
                               'SERIAL_PI2': '10000000f7c08328',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4f:19',
                               'MAC_PI2': 'e4:5f:01:ce:4f:5b',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05024',
                               'SERIAL_PI1': '10000000bba98731',
                               'SERIAL_PI2': '10000000d775a7b2',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ec:97:cd',
                               'MAC_PI2': 'd8:3a:dd:ec:b2:8b',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05025',
                               'SERIAL_PI1': '10000000314e30ef',
                               'SERIAL_PI2': '10000000c7ffb169',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ec:95:42',
                               'MAC_PI2': 'd8:3a:dd:ec:46:e3',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05026',
                               'SERIAL_PI1': '10000000863e31d2',
                               'SERIAL_PI2': '10000000ddc2c378',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ec:b2:df',
                               'MAC_PI2': 'd8:3a:dd:ec:b2:3a',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05027',
                               'SERIAL_PI1': '10000000fda90345',
                               'SERIAL_PI2': '100000003b5558ca',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:a4:17:3d',
                               'MAC_PI2': 'd8:3a:dd:a4:16:f1',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05028',
                               'SERIAL_PI1': '1000000063811fa6',
                               'SERIAL_PI2': '10000000dd7639da',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ec:b3:97',
                               'MAC_PI2': 'd8:3a:dd:ec:b2:6d',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05029',
                               'SERIAL_PI1': '100000006f331013',
                               'SERIAL_PI2': '100000009d454a43',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ec:b3:9d',
                               'MAC_PI2': 'd8:3a:dd:ec:b3:24',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05030',
                               'SERIAL_PI1': '1000000069ff4115',
                               'SERIAL_PI2': '1000000016cae91f',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ec:b0:e1',
                               'MAC_PI2': 'd8:3a:dd:ec:b2:06',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05031',
                               'SERIAL_PI1': '10000000bf50867e',
                               'SERIAL_PI2': '100000000662874e',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ec:b2:85',
                               'MAC_PI2': 'd8:3a:dd:ec:b1:e8',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05032',
                               'SERIAL_PI1': '1000000061c2d679',
                               'SERIAL_PI2': '10000000ff596c02',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:ce:4f:25',
                               'MAC_PI2': 'e4:5f:01:ce:4f:4c',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05033',
                               'SERIAL_PI1': '10000000fd406176',
                               'SERIAL_PI2': '1000000061b19a26',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ec:b3:94',
                               'MAC_PI2': 'd8:3a:dd:ec:b3:c7',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05034',
                               'SERIAL_PI1': '100000001cda7188',
                               'SERIAL_PI2': '100000006603aa6c',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ec:b4:c2',
                               'MAC_PI2': 'd8:3a:dd:ec:b1:5e',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05035',
                               'SERIAL_PI1': '10000000ba3b447f',
                               'SERIAL_PI2': '10000000e77f92ff',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ec:b4:b7',
                               'MAC_PI2': 'd8:3a:dd:ec:b2:0f',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05036',
                               'SERIAL_PI1': '10000000ad0fa731',
                               'SERIAL_PI2': '1000000000ab42e9',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ec:b5:06',
                               'MAC_PI2': 'd8:3a:dd:ec:b2:d6',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05037',
                               'SERIAL_PI1': '10000000d24fcb57',
                               'SERIAL_PI2': '10000000d8857138',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ec:b2:a0',
                               'MAC_PI2': 'd8:3a:dd:ec:b3:33',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05038',
                               'SERIAL_PI1': '100000006d2eea3a',
                               'SERIAL_PI2': '100000004e22a56a',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ec:b5:ca',
                               'MAC_PI2': 'd8:3a:dd:ec:b4:79',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05039',
                               'SERIAL_PI1': '10000000c226c312',
                               'SERIAL_PI2': '100000001bba10a0',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ec:b4:7c',
                               'MAC_PI2': 'd8:3a:dd:ec:b5:1c',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05040',
                               'SERIAL_PI1': '10000000f306a165',
                               'SERIAL_PI2': '100000002ea507ab',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ec:b4:f3',
                               'MAC_PI2': 'd8:3a:dd:ec:b5:5e',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05041',
                               'SERIAL_PI1': '10000000891ecffe',
                               'SERIAL_PI2': '100000003e226803',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ec:b4:5b',
                               'MAC_PI2': 'd8:3a:dd:ec:b4:0c',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05042',
                               'SERIAL_PI1': '100000006a6f2a7e',
                               'SERIAL_PI2': '100000007445fa67',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ec:ae:6c',
                               'MAC_PI2': 'd8:3a:dd:ec:b2:55',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05043',
                               'SERIAL_PI1': '100000007c642b32',
                               'SERIAL_PI2': '10000000cb86c395',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:a4:17:31',
                               'MAC_PI2': 'd8:3a:dd:a4:16:53',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05044',
                               'SERIAL_PI1': '1000000039736d96',
                               'SERIAL_PI2': '10000000756cbbae',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ec:b4:41',
                               'MAC_PI2': 'd8:3a:dd:ec:b3:e5',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05045',
                               'SERIAL_PI1': '10000000dd123133',
                               'SERIAL_PI2': '100000007c5dfba7',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ec:b1:9a',
                               'MAC_PI2': 'd8:3a:dd:ec:b4:03',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05046',
                               'SERIAL_PI1': '10000000b3602266',
                               'SERIAL_PI2': '100000009070545c',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ec:b5:9c',
                               'MAC_PI2': 'd8:3a:dd:ec:b4:a6',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05047',
                               'SERIAL_PI1': '1000000011379f2f',
                               'SERIAL_PI2': '1000000068039fe8',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ec:b1:55',
                               'MAC_PI2': 'd8:3a:dd:ec:b4:a1',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05048',
                               'SERIAL_PI1': '10000000015b4a5d',
                               'SERIAL_PI2': '100000006be786eb',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:7c:26:48',
                               'MAC_PI2': '2c:cf:67:7c:23:e8',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05049',
                               'SERIAL_PI1': '1000000094500efb',
                               'SERIAL_PI2': '1000000087a30e45',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ec:b3:c8',
                               'MAC_PI2': 'd8:3a:dd:ec:b4:12',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05050',
                               'SERIAL_PI1': '100000007c7c04cc',
                               'SERIAL_PI2': '100000007f9237b9',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:7c:27:bc',
                               'MAC_PI2': '2c:cf:67:7c:27:2d',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05051',
                               'SERIAL_PI1': '100000001a48328b',
                               'SERIAL_PI2': '10000000374720cd',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:7c:23:be',
                               'MAC_PI2': '2c:cf:67:7c:25:e7',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05052',
                               'SERIAL_PI1': '10000000c50b71c5',
                               'SERIAL_PI2': '1000000093ace269',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:7c:27:7a',
                               'MAC_PI2': '2c:cf:67:7a:78:47',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05053',
                               'SERIAL_PI1': '10000000c9175718',
                               'SERIAL_PI2': '10000000267146a3',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:7a:76:5e',
                               'MAC_PI2': '2c:cf:67:7c:26:e8',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05054',
                               'SERIAL_PI1': '100000008a53c382',
                               'SERIAL_PI2': '10000000ec9d4b89',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:7c:28:1c',
                               'MAC_PI2': '2c:cf:67:7c:26:d0',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05055',
                               'SERIAL_PI1': '10000000f7f1d4a8',
                               'SERIAL_PI2': '1000000052d4ba14',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:7c:26:89',
                               'MAC_PI2': '2c:cf:67:7c:26:f3',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05056',
                               'SERIAL_PI1': '10000000df979225',
                               'SERIAL_PI2': '10000000850d7c38',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:7c:28:6d',
                               'MAC_PI2': '2c:cf:67:7c:28:03',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05057',
                               'SERIAL_PI1': '10000000f6ecfa36',
                               'SERIAL_PI2': '100000001de20391',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:7c:22:f5',
                               'MAC_PI2': '2c:cf:67:7a:79:12',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05058',
                               'SERIAL_PI1': '100000003db7c1d1',
                               'SERIAL_PI2': '10000000da8dc1d8',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:7c:23:90',
                               'MAC_PI2': '2c:cf:67:7c:27:b6',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '005081',
                               'SERIAL_PI1': '1000000081f4dfdc',
                               'SERIAL_PI2': '10000000ae33fabe',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:a6:65:35',
                               'MAC_PI2': '2c:cf:67:a6:63:b9',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '005082',
                               'SERIAL_PI1': '10000000ca1c8e93',
                               'SERIAL_PI2': '1000000045f5658f',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:a6:66:e3',
                               'MAC_PI2': '2c:cf:67:a6:63:36',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '005083',
                               'SERIAL_PI1': '100000006c519520',
                               'SERIAL_PI2': '1000000040b385e9',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:a6:65:52',
                               'MAC_PI2': '2c:cf:67:a6:65:99',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '005084',
                               'SERIAL_PI1': '10000000f0e29a62',
                               'SERIAL_PI2': '10000000380b8f86',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:a6:60:59',
                               'MAC_PI2': '2c:cf:67:7c:24:31',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '005085',
                               'SERIAL_PI1': '100000005fa74f34',
                               'SERIAL_PI2': '10000000573a5555',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:7c:28:cf',
                               'MAC_PI2': '2c:cf:67:a6:66:28',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05086',
                               'SERIAL_PI1': '1000000045f6dd38',
                               'SERIAL_PI2': '100000003bd47a79',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:a6:66:5f',
                               'MAC_PI2': '2c:cf:67:a6:65:dc',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05087',
                               'SERIAL_PI1': '10000000de352f3d',
                               'SERIAL_PI2': '1000000066031db5',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:a6:66:3e',
                               'MAC_PI2': '2c:cf:67:7c:24:dc',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05088',
                               'SERIAL_PI1': '1000000027330213',
                               'SERIAL_PI2': '100000001e2fe562',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:a6:63:0b',
                               'MAC_PI2': '2c:cf:67:a6:62:9a',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05089',
                               'SERIAL_PI1': '10000000b900bae0',
                               'SERIAL_PI2': '10000000c6b066aa',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:a6:64:39',
                               'MAC_PI2': '2c:cf:67:a6:63:7b',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05090',
                               'SERIAL_PI1': '1000000020cd4d86',
                               'SERIAL_PI2': '100000009d186fa3',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:7a:77:25',
                               'MAC_PI2': '2c:cf:67:7c:28:5c',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05091',
                               'SERIAL_PI1': '10000000ae37d227',
                               'SERIAL_PI2': '100000008dfb6663',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:7c:23:8e',
                               'MAC_PI2': '2c:cf:67:7c:28:04',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05092',
                               'SERIAL_PI1': '100000000585e683',
                               'SERIAL_PI2': '10000000b89703ae',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:a6:4a:79',
                               'MAC_PI2': '2c:cf:67:a6:65:f7',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05093',
                               'SERIAL_PI1': '10000000447ddef4',
                               'SERIAL_PI2': '10000000a5155bc6',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:7a:78:e3',
                               'MAC_PI2': '2c:cf:67:a6:61:87',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05094',
                               'SERIAL_PI1': '10000000b0b376f5',
                               'SERIAL_PI2': '1000000029cdc54c',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:a6:64:65',
                               'MAC_PI2': '2c:cf:67:a6:64:ca',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05095',
                               'SERIAL_PI1': '1000000054b3d966',
                               'SERIAL_PI2': '1000000048c01eac',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:a6:64:92',
                               'MAC_PI2': '2c:cf:67:9c:32:f2',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05096',
                               'SERIAL_PI1': '10000000a89f3ab1',
                               'SERIAL_PI2': '100000006cf25f28',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:a6:63:6a',
                               'MAC_PI2': '2c:cf:67:a6:65:74',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05097',
                               'SERIAL_PI1': '10000000c9a4458e',
                               'SERIAL_PI2': '1000000068f18242',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:a6:63:e2',
                               'MAC_PI2': '2c:cf:67:a6:64:4a',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05098',
                               'SERIAL_PI1': '10000000f9b8020f',
                               'SERIAL_PI2': '10000000e668df00',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:a6:66:fd',
                               'MAC_PI2': '2c:cf:67:a6:63:42',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05099',
                               'SERIAL_PI1': '10000000bb2fa19d',
                               'SERIAL_PI2': '10000000baee2bf6',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:1d:84:a3',
                               'MAC_PI2': '88:a2:9e:1d:85:36',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05100',
                               'SERIAL_PI1': '10000000c6b7ab51',
                               'SERIAL_PI2': '100000007ff34da0',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:1d:84:d6',
                               'MAC_PI2': '88:a2:9e:1d:83:c9',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05101',
                               'SERIAL_PI1': '1000000051d90ee5',
                               'SERIAL_PI2': '10000000a804686a',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:1d:84:df',
                               'MAC_PI2': '88:a2:9e:1d:84:be',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05102',
                               'SERIAL_PI1': '10000000b2e632b0',
                               'SERIAL_PI2': '100000009b8a2daa',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:1d:84:6d',
                               'MAC_PI2': '88:a2:9e:1d:84:f4',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05103',
                               'SERIAL_PI1': '100000006958e2d2',
                               'SERIAL_PI2': '10000000b0b3ee2c',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:1d:83:e0',
                               'MAC_PI2': '88:a2:9e:1d:84:70',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05104',
                               'SERIAL_PI1': '100000002b54d7f5',
                               'SERIAL_PI2': '10000000cdaa8bd1',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:1d:84:4f',
                               'MAC_PI2': '88:a2:9e:1d:84:73',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05105',
                               'SERIAL_PI1': '10000000eb4f8899',
                               'SERIAL_PI2': '10000000f40c03b1',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:1d:84:af',
                               'MAC_PI2': '88:a2:9e:1d:84:a6',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05106',
                               'SERIAL_PI1': '100000005fda624a',
                               'SERIAL_PI2': '10000000bdedd9a2',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:1d:84:dc',
                               'MAC_PI2': '88:a2:9e:1d:84:55',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05107',
                               'SERIAL_PI1': '100000005beb0d3c',
                               'SERIAL_PI2': '100000009ade61a3',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:1d:83:f5',
                               'MAC_PI2': '88:a2:9e:1d:84:fa',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05108',
                               'SERIAL_PI1': '100000004caccfd5',
                               'SERIAL_PI2': '10000000c6b0f507',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:1d:84:0d',
                               'MAC_PI2': '88:a2:9e:1d:84:e5',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05109',
                               'SERIAL_PI1': '1000000059cb47ef',
                               'SERIAL_PI2': '1000000051057ed1',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:1d:84:eb',
                               'MAC_PI2': '88:a2:9e:1d:84:69',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05110',
                               'SERIAL_PI1': '1000000018fabc52',
                               'SERIAL_PI2': '10000000d4bb4df4',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:1d:84:c4',
                               'MAC_PI2': '88:a2:9e:1d:84:e2',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05111',
                               'SERIAL_PI1': '1000000067b00ce8',
                               'SERIAL_PI2': '10000000ec40a71a',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:1d:84:9d',
                               'MAC_PI2': '88:a2:9e:1d:84:2b',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05112',
                               'SERIAL_PI1': '10000000a90126f9',
                               'SERIAL_PI2': '1000000063700a15',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:1d:84:ee',
                               'MAC_PI2': '88:a2:9e:1d:84:d3',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05113',
                               'SERIAL_PI1': '10000000903ac091',
                               'SERIAL_PI2': '100000004476c0f6',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:1d:84:c1',
                               'MAC_PI2': '88:a2:9e:1d:84:8b',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05114',
                               'SERIAL_PI1': '100000009eb73aeb',
                               'SERIAL_PI2': '1000000012e415d9',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:1d:84:a9',
                               'MAC_PI2': '88:a2:9e:1d:84:28',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05115',
                               'SERIAL_PI1': '100000002f0775e5',
                               'SERIAL_PI2': '100000008da44b85',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:1d:84:88',
                               'MAC_PI2': '88:a2:9e:1d:84:64',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05116',
                               'SERIAL_PI1': '10000000a78ebaa1',
                               'SERIAL_PI2': '100000005f04835f',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:1d:84:b4',
                               'MAC_PI2': '88:a2:9e:1d:84:16',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05117',
                               'SERIAL_PI1': '10000000b27ffcc1',
                               'SERIAL_PI2': '100000003aef82a8',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '2c:cf:67:a6:63:95',
                               'MAC_PI2': '2c:cf:67:a6:63:39',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05118',
                               'SERIAL_PI1': '1000000040ae3afa',
                               'SERIAL_PI2': '10000000fadddaff',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:1d:84:3d',
                               'MAC_PI2': '88:a2:9e:1d:84:8e',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05119',
                               'SERIAL_PI1': '10000000da08c26e',
                               'SERIAL_PI2': '100000007ae49c3b',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:1d:84:82',
                               'MAC_PI2': '88:a2:9e:1d:84:7c',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05120',
                               'SERIAL_PI1': '100000000b67b2ae',
                               'SERIAL_PI2': '100000001bda9704',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:1d:84:9a',
                               'MAC_PI2': '88:a2:9e:1d:85:3f',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05121',
                               'SERIAL_PI1': '10000000d6e38f40',
                               'SERIAL_PI2': '10000000c02f51c4',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:1d:84:61',
                               'MAC_PI2': '88:a2:9e:1d:84:97',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05122',
                               'SERIAL_PI1': '100000000d764dd6',
                               'SERIAL_PI2': '1000000061d8ac6b',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:1d:84:90',
                               'MAC_PI2': '88:a2:9e:1d:83:f8',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05123',
                               'SERIAL_PI1': '1000000058ad375f',
                               'SERIAL_PI2': '100000003ed8da92',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:1d:84:bb',
                               'MAC_PI2': '88:a2:9e:1d:84:94',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05124',
                               'SERIAL_PI1': '10000000b4de3c11',
                               'SERIAL_PI2': '100000008fc1008e',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ec:b4:27',
                               'MAC_PI2': 'd8:3a:dd:ec:b4:f1',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05125',
                               'SERIAL_PI1': '1000000094ca32a2',
                               'SERIAL_PI2': '100000000622d17f',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:a9:2d:af',
                               'MAC_PI2': '88:a2:9e:a9:2c:ae',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05126',
                               'SERIAL_PI1': '100000005e0b82d3',
                               'SERIAL_PI2': '10000000dd17b429',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:a9:2c:f7',
                               'MAC_PI2': '88:a2:9e:a9:2c:e2',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05127',
                               'SERIAL_PI1': '100000005defc5f0',
                               'SERIAL_PI2': '100000001de9a658',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:a9:2e:47',
                               'MAC_PI2': '88:a2:9e:a8:da:ac',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05128',
                               'SERIAL_PI1': '10000000880fa2e6',
                               'SERIAL_PI2': '100000004686f502',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:a6:ab:76',
                               'MAC_PI2': '88:a2:9e:a6:b3:3c',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05129',
                               'SERIAL_PI1': '100000003e1f1501',
                               'SERIAL_PI2': '10000000baae002d',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:a8:bd:10',
                               'MAC_PI2': '88:a2:9e:a9:2d:d3',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05130',
                               'SERIAL_PI1': '100000001016200a',
                               'SERIAL_PI2': '10000000db932142',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:a9:2d:4e',
                               'MAC_PI2': '88:a2:9e:a9:2d:7b',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05131',
                               'SERIAL_PI1': '10000000048d3746',
                               'SERIAL_PI2': '100000008ab58527',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:a8:dc:48',
                               'MAC_PI2': '88:a2:9e:a9:2d:06',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05132',
                               'SERIAL_PI1': '1000000094bd9e25',
                               'SERIAL_PI2': '10000000d673e817',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:a9:2d:c1',
                               'MAC_PI2': '88:a2:9e:a9:29:f1',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05133',
                               'SERIAL_PI1': '1000000066dad7ed',
                               'SERIAL_PI2': '1000000082a9f3c6',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:a9:2d:90',
                               'MAC_PI2': '88:a2:9e:a8:db:c0',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05134',
                               'SERIAL_PI1': '10000000a538679d',
                               'SERIAL_PI2': '1000000082d29560',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:a9:2d:60',
                               'MAC_PI2': '88:a2:9e:a9:2c:9c',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05135',
                               'SERIAL_PI1': '100000003f2d70cc',
                               'SERIAL_PI2': '100000002fa3b9b4',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:a8:db:ea',
                               'MAC_PI2': '88:a2:9e:a8:be:38',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05136',
                               'SERIAL_PI1': '10000000e7096f16',
                               'SERIAL_PI2': '100000004c085230',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:a8:dc:4b',
                               'MAC_PI2': '88:a2:9e:a8:db:ab',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '05137',
                               'SERIAL_PI1': '1000000054c228e7',
                               'SERIAL_PI2': '1000000004574370',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': '88:a2:9e:a8:db:98',
                               'MAC_PI2': '88:a2:9e:a8:db:b4',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '14'})

        self.setupList.append({'SERIAL': '07001',
                               'SERIAL_PI1': '100000004467ffcd',
                               'SERIAL_PI2': '10000000ad85f384',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:8c:2e:74',
                               'MAC_PI2': 'e4:5f:01:8c:2e:71',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '3'})#2=dental only

        self.setupList.append({'SERIAL': '07002',
                               'SERIAL_PI1': '100000005da69a21',
                               'SERIAL_PI2': '1000000011f5ae02',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:7a:d9:e6',
                               'MAC_PI2': 'e4:5f:01:7a:d9:f2',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '2'})#2=dental only

        self.setupList.append({'SERIAL': '07003',
                               'SERIAL_PI1': '100000009e13cd91',
                               'SERIAL_PI2': '10000000e4b1403c',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:7a:d9:c8',
                               'MAC_PI2': 'e4:5f:01:9a:61:02',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '2'})#2=dental only

        self.setupList.append({'SERIAL': '07004',
                               'SERIAL_PI1': '1000000089fa072c',
                               'SERIAL_PI2': '100000004749a96e',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:d8:c4:26',
                               'MAC_PI2': 'e4:5f:01:d7:08:01',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '2'})#2=dental only
        self.setupList.append({'SERIAL': '07005',
                               'SERIAL_PI1': '100000007bc20d10',
                               'SERIAL_PI2': '10000000f0bfb14d',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:f2:c1:ea',
                               'MAC_PI2': 'e4:5f:01:f2:c3:0a',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '2'})#2=dental only

        self.setupList.append({'SERIAL': '07006',
                               'SERIAL_PI1': '100000004ab6498c',
                               'SERIAL_PI2': '10000000bf6d6eb0',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:f2:c5:18',
                               'MAC_PI2': 'e4:5f:01:ff:37:b5',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '2'})#2=dental only

        self.setupList.append({'SERIAL': '07007',
                               'SERIAL_PI1': '10000000b18ce9ff',
                               'SERIAL_PI2': '10000000d294401a',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:fe:f7:11',
                               'MAC_PI2': 'e4:5f:01:fe:f6:75',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '2'})#2=dental only

        self.setupList.append({'SERIAL': '07008',
                               'SERIAL_PI1': '100000007753747b',
                               'SERIAL_PI2': '100000004e9ca517',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:82:66:a2',
                               'MAC_PI2': 'e4:5f:01:ff:3a:7c',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '2'})#2=dental only
        self.setupList.append({'SERIAL': '07009', #AT ELUXE3D REQUEST
                               'SERIAL_PI1': '10000000a05e169a',
                               'SERIAL_PI2': '10000000dffff927',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'e4:5f:01:82:66:8d',
                               'MAC_PI2': 'd8:3a:dd:07:e7:b2',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '2'})#2=dental only
        self.setupList.append({'SERIAL': '07010',
                               'SERIAL_PI1': '10000000043e6a4d',
                               'SERIAL_PI2': '10000000c10b825e',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:12:4b:f5',
                               'MAC_PI2': 'd8:3a:dd:0d:d6:60',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY':'Y',
                               'CODE': '2'})#2=dental only

        self.setupList.append({'SERIAL': '07011',
                               'SERIAL_PI1': '100000009aa1262b',
                               'SERIAL_PI2': '10000000a5f5fcb0',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:12:47:27',
                               'MAC_PI2': 'd8:3a:dd:3e:e4:d7',
                               'PROJ_MODEL': 'C6_V3',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '2'})#2=dental only
        self.setupList.append({'SERIAL': '07012',
                               'SERIAL_PI1': '10000000cfced015',
                               'SERIAL_PI2': '1000000022bfac11',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:ed:ac:82',
                               'MAC_PI2': 'e4:5f:01:d8:c4:26',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '2'})  # 2=dental only

        self.setupList.append({'SERIAL': '07013',
                              'SERIAL_PI1': '10000000693ac846',
                              'SERIAL_PI2': '10000000749cf58f',
                              'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                              'BT_MAC_PROJ': '',
                              'CIRCLE_PITCH': '6.000',
                              'IP_PI1': '169.254.30.155',
                              'IP_PI2': '169.254.71.46',
                              'BT_MAC_PI1': '',
                              'BT_MAC_PI2': '',
                              'MAC_PI1': 'd8:3a:dd:3e:c5:f0',
                              'MAC_PI2': 'd8:3a:dd:ed:ae:08',
                              'PROJ_MODEL': 'C6_V2B',
                              'LEVELLER': 'ARD',
                              'LENSES': '6mm',
                              'TYPE': 'DENTAL',
                              'WIFI_READY': 'Y',
                              'CODE': '2'})

        self.setupList.append({'SERIAL': '07014',
                               'SERIAL_PI1': '100000005dd03777',
                               'SERIAL_PI2': '10000000da8bc7d3',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:f3:d7:25',
                               'MAC_PI2': '2c:cf:67:0f:f3:12',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '2'})

        self.setupList.append({'SERIAL': '07015',
                               'SERIAL_PI1': '10000000e1118acf',
                               'SERIAL_PI2': '10000000139874bd',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:d1:93:af',
                               'MAC_PI2': 'd8:3a:dd:f5:32:b8',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY': 'Y',
                               'CODE': '2'})

        self.setupList.append({'SERIAL': '07016',
                               'SERIAL_PI1': '10000000451aeb94',
                               'SERIAL_PI2': '1000000060e6544e',
                               'BT_UUID_PI1': 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc',
                               'BT_MAC_PROJ': '',
                               'CIRCLE_PITCH': '6.000',
                               'IP_PI1': '169.254.30.155',
                               'IP_PI2': '169.254.71.46',
                               'BT_MAC_PI1': '',
                               'BT_MAC_PI2': '',
                               'MAC_PI1': 'd8:3a:dd:c9:db:b5',
                               'MAC_PI2': 'd8:3a:dd:c9:d9:87',
                               'PROJ_MODEL': 'C6_V2B',
                               'LEVELLER': 'ARD',
                               'LENSES': '6mm',
                               'TYPE': 'DENTAL',
                               'WIFI_READY':'Y',
                               'CODE': '2'})

    def saveJSON(self):
        self.setupJSON = json.dumps(self.setupList)
        print(self.setupJSON)
        print('length of res', len(self.setupJSON))
        print('max length of res', raw.NOISE.shape[0])

        count=raw.NOISE.shape[0]-1
        data=np.zeros((len(self.setupJSON)),'uint8')
        for i in range(len(self.setupJSON)):
            data[i]=ord(self.setupJSON[i])+raw.NOISE[count]
            count-=1
            #print(ord(self.setupJSON[i]))
        #print(data)
        np.savez('resource.npz', data)
        if os.path.isfile('resource'):
            os.remove('resource')
        os.rename('resource.npz', 'resource')

    def loadJSON(self):
        file=np.load('resource')
        res=file['arr_0']

        count=raw.NOISE.shape[0]-1
        data=np.zeros((res.shape[0]),'uint8')
        JSON=''
        for i in range(res.shape[0]):
            #print(raw.NOISE[count])
            if res[i]<raw.NOISE[count]:
                data[i] = res[i] +256 - raw.NOISE[count]
            else:
                data[i]=res[i]-raw.NOISE[count]
            JSON+=chr(data[i])
            count-=1
            #print(ord(self.setupJSON[i]))
        #print(data)
        print(JSON)
        #PRINT PROJ APP JAVA CODE
        #dataDict = json.loads(JSON)
        #for data in dataDict:
        #    print('//private String BT_MAC_PI1 = "' + data['BT_MAC_PI1']+'"; //SERIAL ',data['SERIAL'])

    def makeUpdateForResource(self):
        shutil.copy('resource', 'main/resource')

        updateFilename = 'update.zip'  # update in update.py also
        UPDATE_PWD = b'nb*I2$jxMnNl60I+t&EE1GU0HbWert!'


        #with zipfile.ZipFile (updateFilename, 'w') as zip:
        #        zip.setpassword(UPDATE_PWD)
        #        zip.write('main/resource')

        # zip with password, .bat doesn't suffer windows permission error. Note: zipfile can not encrypt
        subprocess.call(['makeResourceUpdate.bat'])        #copy platefiles from: c:\Work-TupelGit\TeethUI\factoryTools\plateFiles\*.npz
        #subprocess.call(['"C:/Program Files/7-Zip/7z.exe" a  -r update.zip -w main/resource -p"nb*I2$jxMnNl60I+t&EE1GU0HbWert!"'])

        #TEST UPZIP
        #the_zip_file = zipfile.ZipFile(updateFilename)
        #the_zip_file.setpassword(UPDATE_PWD)
        #the_zip_file.extractall(path=None, members=None, pwd=UPDATE_PWD)
        #print('finish')

        print('resource file in tools folder - which will be copied into in obfuscated V2 files upon running obfuscateV2.sh')
        print('Copied also to main/resource, ready for zipping')

        #shutil.copy('update.zip', 'C:/Work/GoogleDrive/SharedFolders/ScannerSoftwareReleases/HWupdates/updateResource.zip')

        # shutil.copy('update.zip','C:/Users/mathe/My Drive (tupeluk@gmail.com)/SharedFolders/ScannerSoftwareReleases/HWupdates/updateResource.zip')
        # print('Copied new resource update.zip to C:/Users/mathe/My Drive (tupeluk@gmail.com)/SharedFolders/ScannerSoftwareReleases/HWupdates/updateResource.zip')

        shutil.copy('update.zip','D:/eLUXE3D/scannerFW/updateResource.zip')
        print('Copied new resource update.zip to D:/eLUXE3D/scannerFW/updateResource.zip')


    def adjustConstants(self):
        pass


    def makeNoise(self):
        noise=''
        for i in range(MAX_FILE_LENGTH):
            noise+=str(secrets.randbelow(255))+','
        noise = noise[:-1]
        file = open("raw.py", "w")
        file.write("import numpy as np\n")
        file.write("NOISE = np.array(("+noise+"), 'uint8')")
        file.close()
        exit()

    def makeExtraNoise(self):
        oldNoiseCount=raw.NOISE.shape[0]
        #extra noise
        noise=''
        for i in range(MAX_FILE_LENGTH-oldNoiseCount):
            noise+=str(secrets.randbelow(255))+','
        #add old noise at end (noise is read end to start)
        for i in range(raw.NOISE.shape[0]):
            noise+=str(raw.NOISE[i])+','
        noise = noise[:-1]
        file = open("raw2.py", "w")
        file.write("import numpy as np\n")
        file.write("NOISE = np.array(("+noise+"), 'uint8')")
        file.close()
        exit()

    def checkForDuplicateSerialNumbers(self):
        noOfSerials=len(self.setupList)
        thereWasADuplicate = False
        for i in range(noOfSerials):
            for j in range(noOfSerials):
                if i==j:
                    continue
                #print(self.setupList[i]['SERIAL'], self.setupList[j]['SERIAL'])
                if self.setupList[i]['SERIAL']==self.setupList[j]['SERIAL']:
                    print('DUPLICATE!!!', self.setupList[i]['SERIAL'], i,j)
                    thereWasADuplicate=True
                if self.setupList[i]['SERIAL_PI1']==self.setupList[j]['SERIAL_PI1']:
                    print('DUPLICATE!!!', self.setupList[i]['SERIAL'], i,j)
                    thereWasADuplicate=True
                if self.setupList[i]['SERIAL_PI2']==self.setupList[j]['SERIAL_PI2']:
                    print('DUPLICATE!!!', self.setupList[i]['SERIAL'], i,j)
                    thereWasADuplicate=True

        if thereWasADuplicate:
            exit()
        else:
            print('No duplicates')




if __name__ == "__main__":
    mSetup=setup()  # create list
    mSetup.checkForDuplicateSerialNumbers()  # check for duplicates
    #mSetup.makeNoise()#run once to get raw.py, then just use save and load
    #mSetup.makeExtraNoise()  # run once to get raw2.py, then just use save and load
    mSetup.saveJSON() # create resource file w/ some fillers (noise)
    mSetup.loadJSON() # load resource file and print contents
    mSetup.makeUpdateForResource()  # copy resource file into tools/main/, run makeResourceUpdate.bat to copy plate files from base location to software areas, create a zip file from the "main" folder called "update.zip" copy zip to updateResource.zip
    # which is placed on google drive for updating.



