import json#from enum import Enum
import numpy as np
import multiprocessing

class Control():
    #These variables can be shared globally.
    #each module must import constants, then they all see the same data.
    #but don't pass this data around, else funny affects can happen.  each module should access directly. See paper notes.

    #queues can wierdly go out of order, if it takes longer to queue item a than item b, b can get on first, and I think this caused freezes.
    #also if an object is modified whilst being put on a queue, the modified data can end up on the queue.
    #https://stackoverflow.com/questions/28593103/python-multiprocessing-queue-put-behavior
    #I use Manager.List with locks now.  It allows an item in the list to be deleted when the pc has acknowledged receipt.
    #Also it might avoid the order problem, and I use deepcopy so data can not be altered whilst it is being put on the queue.

    
    #classes
    mServer=None
    mCapture=None          # Camera 0 (left) – always Pi1/master camera
    mCaptureRight=None     # Camera 1 (right) – Pi5 only; replaces the slave Pi camera
    mRealTime= None
    mRealTimeRight=None    # Pi5 only: RealTimeProcessing for Camera 1
    mScanMaster=None
    mScanSlave=None
    mScanSlaveLocal=None   # Pi5 only: in-process ScanSlave instance for Camera 1
    mProjScreen=None
    #queues and flags
    decodeImageQ=None
    pcImageList=None
    imageLock=multiprocessing.Lock()
    mLanSender=None
    requestDoneEvent = None
    doneCommands = None
    newCommandDoneFlag = None
    calibPointsData = None
    calibrationDataReady = None
    cancelList = None

    

class DEBUG():
    #pi
    #SHOULD BE TRUE
    SYNC_CAMERAS=True
    USE_PLATE_NUMBERS=True
    #SHOULD BE FALSE
    SAVE_SCAN_IMAGES=False
    SAVE_CALIB_IMAGES=False
    PROJ_SCREEN_DEBUG_MODE=False#non full screen so can quit out if needed
    DEBUG_IMPORTS=False#set false for release
    DEBUG_NUMBER_IMAGES=False
    
def forcePlateFileUse():
    serialNumber=int(Info.SERIAL)
    print('serialNumber',serialNumber)
    if serialNumber>106:#TODO set serail numbers of machines that need qr code well.
        return True
    else:
        return False
    
class Info():
    PING_REPLY_CODE_MASTER='1_bw'
    PING_REPLY_CODE_SLAVE = '2_sx'
    SCANNER_NAME='Tupel 3D'
    HW_VERSION='5.00'#make sure in format x.xx
    SW_VERSION='0.00'
    MASTER_UNAME='TupelPi1'
    SLAVE_UNAME='TupelPi2'
    PI5_UNAME='TupelPi5'   # hostname for the single Raspberry Pi 5 unit
    SERIAL='1'
    SERIAL_PI1='TBD'
    SERIAL_PI2='TBD'
    SERIAL_PI1_ACTUAL = 'TBD'
    SERIAL_PI2_ACTUAL = 'TBD'
    MAC_PI1='TBD'
    MAC_PI2='TBD'
    BT_MAC_PI1='TBD'
    BT_MAC_PI2 = 'TBD'
    PROJ_MODEL='C6' #default is c6, only changed if resource file tells it to.
    LEVELLER='MARKER'#MARKER or ARD for ARDUINO (IR or magnetic levelling).If nothing in setup, then left as MARKER as default.
    LENSES='3mm'#default, can be '3mm' or '6mm'
    TYPE='BSB'#default BSB
    WIFI_READY='N'#default N, can be Y, N
    CODE='0'
    MSG=''

class BlueTooth():
    BT_UUID_PI1 = 'c37334f5-928f-4b6b-9c28-29a0fd2c49fc'#needs to match that in Android app
    #clientMac="94:65:2D:25:BE:D0"#OnePlus
    BT_MAC_PROJ='22:22:D9:93:76:3C'#rc1

class Motor():
    #tested ok on heavy load
    MAX_SPEED_V=125#deg per sec
    ACCEL_V = 250#120  # deg per sec per sec
    MAX_SPEED_H = 150# deg per sec
    ACCEL_H = 750  # deg per sec per sec, seems little effect on load carrying, speed is much more critical and high accel seems to shudder less.

class ScanType():
    SCAN_TYPE=5#holds scan type to be used from following options
    CAST=1
    IMPRESSION=2
    SINGLE=3
    TEST=4
    SINGLE_SHOT=5
    IMPRESSION_TWO_SIDED=6
    ARTICULATOR=7
    BITE=8
    OCCLUSION=9
    DIE = 10

class Protocol():
    #OLD IP CONNECTIONS
    #VIA ROUTER
    #TCP_IP = '192.168.0.24'#pi1 is .24 pi2 is .23, ethernet and wifi are different (mac address)
    #TCP_IP_PI2= '192.168.0.23'
    #VIA SWITCH DHCP
    #IP_PI1 = '169.254.59.237' #found from ipconfig or ifconfig linux
    #IP_PI2 = '169.254.145.169'
    #IP ADDRESSES FOR RELEASE SCANNERS
    IP_PI1 = '169.254.30.155'  # found from ipconfig or ifconfig linux, candidate release, my version #TODO put back and use this in all releases.
    IP_PI2 = '169.254.71.46'
    #FOR CONNECTING TO VERSION 2 DEVELOPMENT MODEL:
    #IP_PI1 = '169.254.98.0'
    #IP_PI2 = '169.254.211.66'

    TCP_PORT = 5005
    TCP_PORT_PI2 = 5005

    FILE_BUFFER_SIZE = 4*1024
    FACTORY_ZIP='main.zip'
    UPDATE_PWD=b'nb*I2$jxMnNl60I+t&EE1GU0HbWert!'
    HEADER='tD'#random code to identify message as for scanner
    CMD_PING='01'
    CMD_SCAN='02'
    CMD_CALIB='03'
    CMD_CANCEL='04'
    CMD_SHOT_FROM_PI1_TO_PC='05'
    CMD_SCAN_SHOT='06'
    CMD_MOVE='07'
    CMD_GET_SHOT_DATA='08'
    CMD_META_FROM_PI2_TO_PI1='09'
    CMD_CALIB_POINTS_FROM_PI2_TO_PI1='10'
    CMD_CALIB_DATA_FROM_PI1_TO_PI2='11'
    CMD_CHANGE_SETTINGS='12'
    CMD_PLAY_SOUND = '13'
    CMD_UPDATE_FIRMWARE = '14'
    CMD_REBOOT='15'
    CMD_PROJ_IMAGE = '16'
    CMD_GET_CAMERA_IMAGE='17'
    CMD_STOP_CAMERA_IMAGE = '18'
    CMD_FACTORY_RESET='19'
    CMD_MOTOR_POWER='20'
    CMD_GET_FOCUS_IMAGE='21'
    CMD_MOTOR_TO_ZERO='22'
    CMD_MOTOR_MOVE_TO='23'
    CMD_RESET_SCAN_DATA='24'
    CMD_SET_CHARGE_MODE='25'
    CMD_DIAGNOSIS_PING='26'
    CMD_FIX_DISK = '27'
    CMD_SYNC_CAMERA = '28'
    CMD_GET_CALIB_DATA='70'
    CMD_AUTO_EXP= '71'
    CMD_SET_CALIB_DATA='72'
    CMD_MOTOR_CALIB_OPTICAL_ZERO='73'
    CMD_MOTOR_MOVE_BY='74'
    CMD_MOTOR_SET_CURRENT_ANGLE_TO_ZERO='75'
    CMD_GET_PLATE_FILE='76'
    CMD_GET_MAG_READING='77'
    CMD_ENABLE_WIFI='78'
    CMD_DISABLE_WIFI = '79'
    CMD_SET_MSG = '80'
    CMD_GET_MSG = '81'

    #Intra1
    #CMD_GET_IMAGE_SET= '29'
    CMD_START_CAMERA='30'
    CMD_CAPTURE_REQUEST='31'
    CMD_GET_BUFFERED_IMAGE_SET='32'
    CMD_CAPTURE_IMAGE_SET= '33'
    CMD_DISCARD_IMAGE_SET='34'
    CMD_UPDATE_CAMERA_SETTINGS = '35'
    CMD_SHUTDOWN = '36'

    #control
    STATUS_READY='50'
    STATUS_BUSY='51'

    #replacing old serial commands
    CMD_SET_PI2_MODE = '60'
    CMD_DONE='61'
    
    CAPTURE_TIME_PI_1=None #used to communicate between different threads in different modules - seems to work well.
    CLOCK_OFFSET_BUFFER=[]#stores last 10 or so clock offset, the most accurate is the minimum, because this will be the reading that had lowest latency over network.  (LAN has sub msec latency, but sometimes can go up to 10msec latency).
    CLOCK_OFFSET=None

class Sounds():#TODO PLAY THROUGH PC
    START_PING='00'
    STOP_PING='01'
    PROCESSING='02'
    CALIBRATING='03'
    SCAN_COMPLETE='04'
    READY_TO_SCAN='05'
    SHUTTING_DOWN='06'
    MUSIC='08'
    CANCEL='09'
    CALIBRATION_FAILED='10'
    HIGH_AMBIENT_LIGHT='11'
    QR_NOT_FOUND='12'

    
class Serial():
    ARDUINO_PORT='/dev/ttyUSB0'
    #BAUD_RATE_PI=115200#1000000# 9600 is 12 msec for 9 byte message, 115200 is 1.1msec for 9 byte message, 1,000,000 is 0.5msec for 9 byte message, 100M is 24msec
    BAUD_RATE_ARDUINO = 9600


class Scanning():
    LEVEL_ANGLE=-32.4#optical angle sets platform to level with ground, this angle is called "level angle", such that at 0 degrees the platform is ~in line with cameras.
    #CAMERA SETTTINGS
    #CAPTURE_W=1856#must be multiple of 32 to match picamera resolutions, can be upto 1920 without changing sensor mode.
    #CAPTURE_H=1088#must be multiple of 16
    #PROCESS_W=1842
    #PROCESS_H=1080#TODO could resize to this process size and then crop to a narrower process size for speed, at the expense of narrower fov (which is not needed for teeth).  Could use wider fov to pick up markers off turntable now.
    RESIZE=None
    BIT_RATE=60000000
    JPG_QUALITY=90
    RESOLUTION = (1920, 1080)
    FRAME_RATE=30
    MAX_FRAME_RATE = 30 #29.6
    ISO_AUTO = True
    SCAN_AUTO_EXPOSURE = True
    ISO = 60
    EXPOSURE_TIME_SCAN = 33  # 17/2#2*25/3
    EXPOSURE_TIME_CALIB = 20  # 8.32#17/2#2*25/3#25/3 or 17 #good for no colour flicker from proj
    CAMERA_MODE = 1
    ZOOM_L = (0, 0, 1, 1)
    ZOOM_R = (0, 0, 1, 1)
    AUTO_EXPOSURE_LIST = [8.3, 16.7, 25.0, 33.2, 5 * 8.333, 6 * 8.333, 7 * 8.333, 8 * 8.333, 12 * 8.333, 16 * 8.333, 20 * 8.333, 24 * 8.333, 30 * 8.333, 36 * 8.333, 48 * 8.333]  # Ver 2 proj C6: multiples of 8.32 don't cause colour break up
    AUTO_EXPOSURE_TARGET_MAX=240
    AUTO_EXPOSURE_DOWNSCALE=50
    IMAGE_STACK=1
    IMAGE_STACK_CALIB = 5

    #LEVELLER
    START_TARGET=613#1201.2#1223.79 for serial 2, #1245.73 for serial 1, #should be level to ground #TODO update on calibration
    RMS_SYSTEM=0.0#temporarily stored after a calibration, read y diagnosis ping
    PLATE_NUMBER=0  #0 is special value to mean no plate number
    #CONNECTION
    TIMEOUT_CONNECT=3#seconds
    TIMEOUT_DATA = None  # seconds

    #SCAN SETTINGS
    DEFAULT_GROUND_PLANE=29#mm down from center of rotation
    GROUND_PLANE_SAFETY_MARGIN = 3  # mm cropped above measure ground plane to be sure not to get any ground in.
    FLOWER_END_RADIUS= 48
    COLOUR_SCAN=True
    SENSITIVITY=1
    SOUND=100
    CAMERA_SEPARATION_ANGLE=21#degrees, just estimate for calib object positioning
    SETTLE_TIME = 0.05  # sec
    SETTLE_TIME_VERT = 0.2  # sec

    #SCAN IMAGE SET UP - V2
    #images >=100: 101 means show image 1 and so on.  This means each image is uniquely labelled for missed image capture and sorting, but projScreen buffer is kept small.
    #SCAN_IMAGE_LIST = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]#assumes WHITE_MATCHING_PEAK_STRIP_INTENSITY is white image, need to update decode image array processing too.
    SCAN_IMAGE_ARRAY_FILENAMES=['s0000C6_V2', 's0001C6_V2','s0002C6_V2','s0003C6_V2','s0004C6_V2','s0005C6_V2','s0006C6_V2','s0007C6_V2','s0008C6_V2','s0009C6_V2',#indices 0-9
                                's0010C6_V2', 's0011C6_V2','s0012C6_V2','s0013C6_V2','s0014C6_V2','s0015C6_V2','s0016C6_V2','s0017C6_V2','s0018C6_V2','s0019C6_V2',#indices 10-19
                                's0020C6_V2', 's0021C6_V2','s0022C6_V2','s0023C6_V2','s0024C6_V2','s0025C6_V2','s0026C6_V2']#indices 20-26
    SCAN_IMAGE_ARRAY_FILENAMES_C6=['s0000', 's0001','s0002','s0003','s0004','s0005','s0006','s0007','s0008','s0009',#indices 0-9
                                's0010', 's0011','s0012','s0013','s0014','s0015','s0016','s0017','s0018','s0019',#indices 10-19
                                's0020', 's0021','s0022','s0023','s0024','s0025','s0026']#indices 20-26
    SCAN_IMAGE_ARRAY_FILENAMES_C6V2=['s0000C6_V2', 's0001C6_V2','s0002C6_V2','s0003C6_V2','s0004C6_V2','s0005C6_V2','s0006C6_V2','s0007C6_V2','s0008C6_V2','s0009C6_V2',#indices 0-9
                                's0010C6_V2', 's0011C6_V2','s0012C6_V2','s0013C6_V2','s0014C6_V2','s0015C6_V2','s0016C6_V2','s0017C6_V2','s0018C6_V2','s0019C6_V2',#indices 10-19
                                's0020C6_V2', 's0021C6_V2','s0022C6_V2','s0023C6_V2','s0024C6_V2','s0025C6_V2','s0026C6_V2']#indices 20-26
    SCAN_IMAGE_ARRAY_FILENAMES_C6V2B=['s0000C6_V2B', 's0001C6_V2B','s0002C6_V2B','s0003C6_V2B','s0004C6_V2B','s0005C6_V2B','s0006C6_V2B','s0007C6_V2B','s0008C6_V2B','s0009C6_V2B',#indices 0-9
                                's0010C6_V2B', 's0011C6_V2B','s0012C6_V2B','s0013C6_V2B','s0014C6_V2B','s0015C6_V2B','s0016C6_V2B','s0017C6_V2B','s0018C6_V2B','s0019C6_V2B',#indices 10-19
                                's0020C6_V2B', 's0021C6_V2B','s0022C6_V2B','s0023C6_V2B','s0024C6_V2B','s0025C6_V2B','s0026C6_V2B']#indices 20-26
    SCAN_IMAGE_ARRAY_FILENAMES_C6V3=['s0000C6_V3', 's0001C6_V3','s0002C6_V3','s0003C6_V3','s0004C6_V3','s0005C6_V3','s0006C6_V3','s0007C6_V3','s0008C6_V3','s0009C6_V3',#indices 0-9
                                's0010C6_V3', 's0011C6_V3','s0012C6_V3','s0013C6_V3','s0014C6_V3','s0015C6_V3','s0016C6_V3','s0017C6_V3','s0018C6_V3','s0019C6_V3',#indices 10-19
                                's0020C6_V3', 's0021C6_V3','s0022C6_V3','s0023C6_V3','s0024C6_V3','s0025C6_V3','s0026C6_V3']#indices 20-26
    SCAN_IMAGE_ARRAY_FILENAMES_C6V3_TEST=['s0000C6_V3', 's0001C6_V3','s0002C6_V3','s0003C6_V3','s0004C6_V3','s0005C6_V3','s0006C6_V3','s0007C6_V3','s0008C6_V3','s0009C6_V3',#indices 0-9
                                's0010C6_V3', 's0011C6_V3','s0012C6_V3','s0013C6_V3','s0014C6_V3','s0015C6_V3','s0016C6_V3','s0017C6_V3','s0018C6_V3','s0019C6_V3',#indices 10-19
                                's0020C6_V3', 's0021C6_V3','s0022C6_V3','s0023C6_V3','s0024C6_V3','s0025C6_V3','s0026C6_V3','s0027C6_V3', 's0028C6_V3','s0029C6_V3',
                                's0030C6_V3', 's0031C6_V3', 's0032C6_V3', 's0033C6_V3', 's0034C6_V3', 's0035C6_V3', 's0036C6_V3', 's0037C6_V3', 's0038C6_V3', 's0039C6_V3',
                                's0040C6_V3', 's0041C6_V3', 's0042C6_V3', 's0043C6_V3', 's0044C6_V3', 's0045C6_V3', 's0046C6_V3', 's0047C6_V3', 's0048C6_V3', 's0049C6_V3',
                                's0050C6_V3'          ]
    SCAN_IMAGE_ARRAY_FILENAMES_NUMBERS= ['n0000', 'n0001','n0002','n0003','n0004','n0005','n0006','n0007','n0008','n0009',#indices 0-9
                                'n0010', 'n0011','n0012','n0013','n0014','n0015','n0016','n0017','n0018','n0019',#indices 10-19
                                'n0020', 'n0021','n0022','n0023','n0024','n0025','n0026']#indices 20-26
    SCAN_IMAGE_LIST = [12,13,14,15,16,17,18,19,20,21,22,23,0,1,2,3,4,5,6,7,8,9,10,11,24]# fine sines last, so unaffected by wobble.  Assumes WHITE_MATCHING_PEAK_STRIP_INTENSITY is white image, and white is last image need to update decode image array processing too.
    SCAN_IMAGE_LIST_DEFAULT = [12,13,14,15,16,17,18,19,20,21,22,23,0,1,2,3,4,5,6,7,8,9,10,11,24]# fine sines last, so unaffected by wobble.  Assumes WHITE_MATCHING_PEAK_STRIP_INTENSITY is white image, and white is last image need to update decode image array processing too.
    SCAN_IMAGE_LIST_LOW_NOISE = [12,13,14,15,16,17,18,19,20,21,22,23,0,1,2,3,4,5,6,7,8,9,10,11,1000,1001,1002,1003,1004,1005,1006,1007,1008,1009,1010,1011,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,24]
    WHITE_MATCHING_PEAK_STRIP_INTENSITY = 24  # e.g. grey 190
    WHITE_IMAGE = 26
    IMAGE_SET_LENGTH = len(SCAN_IMAGE_LIST) - 1  # -1 as one image is white and not stored in array, white image should be last
    PROCESSING_IMAGE = 'magen'
    SCAN_STARTING_IMAGE = 'red__'
    WHITE_IMAGE_NO_BUFFER = 'q0255'
    WHITE_MATCHING_PEAK_STRIP_INTENSITY_NO_BUFFER = 's0024'
    IDLE_IMAGE = 'blue_'  # 'focus'

    #SCAN ANGLES
    SCAN_ANGLES = [[-32.4, 0], [-32.4, 40.5], [-32.4, 80.1], [-32.4, 120.6], [-32.4, 160.2], [-32.4, 200.7], [-32.4, 240.3], [-32.4, 280.8], [-32.4, 320.4], [-81.0, 0]]
    TOP_VIEW_SHOT_NUMBER_DIE = 9
    TOP_VIEW_SHOT_NUMBER_CAST = 9

    #MOTOR SETTINGS
    H_MOTOR_SPEED_CAST=250
    H_MOTOR_ACCEL_CAST=250
    V_MOTOR_SPEED_CAST=125
    V_MOTOR_ACCEL_CAST=125

    #PROJECTOR TIMINGS - set from PC
    LATENCY=25000#usec. default (C6).  Min latency possible.
    CAPTURE_START_DELAY_TARGET=50000#250000#usec
    IMAGE_SYNC_ERROR_MARGIN=54000#usec # 16msec is unreliable

    #MAG LEVEL
    MAG_LEVEL=701

class FringeMode():
    FRINGE_MODE=0#default - represents actual selected mode.
    P12_1C_PI_PROCESS=0
    P12_3C = 1
    P6_1C = 2
    P6_2C = 3
    P6_4C = 4
    CUSTOM=5


class Processing():
    CIRCLE_PITCH=6.0#mm
    EDGE_NOISE_REMOVAL=True
    MIN_INTENSITY=50#higher is less sensitive. TODO make sure ok for high ambient light. 0.0005 is enough for it to function, higher cut out bad data?
    MAX_GRADIENT = 10#10

class PCprocessing():
    PLY=True
    STL=False
    OBJ=False
                               
    MY_DOCS_DS_SCAN= ''
    RAW_DATA_PATH = 'RawData/'#raw data and settings will always be in MY_DOCS + RAW_DATA_PATH
    EXPORT_PATH = ''#'' on first run, changed to my docs during first run, if changed by user it is left alone.
    NUMBER_OF_DIE_HOLDERS=7
    RAW_EXT = '_RAW.ply'  # make 8 chars, extension of scan filename fresh from volume, ready for meshlab, make 8 chars
    PRE_EXT='_PRE.ply'#make 8 chars, extension of scan filename for pre processed - i.e. cleaned, smoothed, compressed etc. but not aligned.
    ALIGNMENT_LOW_RES_VOXEL_SIZE=0.5
    BIO_BIG_BOX_EMAIL=''
    LAB_PRONTO_USERNAME = ''
    LAB_PRONTO_MACHINE_CODE = '0'
    LAB_PRONTO_PHONE = ''
    LAB_PRONTO_TEST_MODE = True
    DATA_SHARE=True

def saveSettings():
    sensitivitySetUp()
    commandDict = {"COLOUR_SCAN": Scanning.COLOUR_SCAN,
                   "SOUND": Scanning.SOUND,
                   "SENSITIVITY": Scanning.SENSITIVITY,
                   "EDGE_NOISE_REMOVAL": Processing.EDGE_NOISE_REMOVAL,
                   "PLY": PCprocessing.PLY,
                   "STL": PCprocessing.STL,
                   "OBJ": PCprocessing.OBJ,
                   "EXPORT_FOLDER": PCprocessing.EXPORT_PATH,
                                          
                                                  
                   "BIO_BIG_BOX_EMAIL": PCprocessing.BIO_BIG_BOX_EMAIL,
                   "LAB_PRONTO_USERNAME": PCprocessing.LAB_PRONTO_USERNAME,
                   "LAB_PRONTO_MACHINE_CODE": PCprocessing.LAB_PRONTO_MACHINE_CODE,
                   "LAB_PRONTO_PHONE":PCprocessing.LAB_PRONTO_PHONE,
                   "DATA_SHARE":PCprocessing.DATA_SHARE}
    settingNameAndPath = os.path.join(PCprocessing.RAW_DATA_PATH, "settings.json")
    with open(settingNameAndPath, "w") as write_file:
        json.dump(commandDict, write_file)


def loadSettings():
    try:
                                                     
        settingNameAndPath=os.path.join(PCprocessing.RAW_DATA_PATH, "settings.json")
        with open(settingNameAndPath, "r") as read_file:
            commandDict = json.load(read_file)
        Scanning.COLOUR_SCAN = commandDict["COLOUR_SCAN"]
        Scanning.SOUND = commandDict["SOUND"]
        Scanning.SENSITIVITY = commandDict["SENSITIVITY"]
        Processing.EDGE_NOISE_REMOVAL = commandDict["EDGE_NOISE_REMOVAL"]
        PCprocessing.PLY = commandDict["PLY"]
        PCprocessing.STL = commandDict["STL"]
        PCprocessing.OBJ = commandDict["OBJ"]
        PCprocessing.EXPORT_PATH = commandDict["EXPORT_FOLDER"]
        PCprocessing.BIO_BIG_BOX_EMAIL = commandDict["BIO_BIG_BOX_EMAIL"]
        PCprocessing.LAB_PRONTO_USERNAME = commandDict["LAB_PRONTO_USERNAME"]
        PCprocessing.LAB_PRONTO_MACHINE_CODE = commandDict["LAB_PRONTO_MACHINE_CODE"]
        PCprocessing.LAB_PRONTO_PHONE = commandDict["LAB_PRONTO_PHONE"]
        PCprocessing.DATA_SHARE = commandDict["DATA_SHARE"]
        sensitivitySetUp()
    except Exception as e:
        print(e)
    if PCprocessing.EXPORT_PATH == '':#if first run, then set default export dir
        PCprocessing.EXPORT_PATH = os.path.join(PCprocessing.MY_DOCS_DS_SCAN, 'ExportData')

def sensitivitySetUp():
    if Scanning.SENSITIVITY == 0:  # Low
        Scanning.IMAGE_STACK = 1
        Processing.MIN_INTENSITY = 10000
        Processing.MAX_GRADIENT = 10
    if Scanning.SENSITIVITY == 1:  # Med
        Scanning.IMAGE_STACK = 1
        Processing.MIN_INTENSITY = 10
        Processing.MAX_GRADIENT = 10
    if Scanning.SENSITIVITY == 2:  # High
        Scanning.IMAGE_STACK = 3
        Processing.MIN_INTENSITY = 1
        Processing.MAX_GRADIENT = 10
