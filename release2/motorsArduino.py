import time
import opticalAngleMarker
import captureVideo
import constants
import serial
import RPi.GPIO as GPIO
import subprocess
import osCommands
if constants.DEBUG.PROJ_SCREEN_DEBUG_MODE:
    import projScreen  # pygame based - works in gui
else:
    import projScreenFB as projScreen  # direct screen access from CLI - much faster.

#TODO could I actually remove need for arduino by using better sleep command - https://stackoverflow.com/questions/17499837/python-time-sleep-vs-busy-wait-accuracy

class motorsArduino():
    MOTOR_V=0#0= vertical, 1=horizontal motor
    MOTOR_H=1
    GPIO_SLEEP_V = 27
    GPIO_SLEEP_H = 25
    DELIMITER=':'

    MIN_ANGLE_STEP_H=0.9
    MIN_ANGLE_STEP_V=1.8
    
    #MOVEMENT_IF_NO_DOT_FOUND=-14.4 #61.2#keep divisible by  3.6 deg
    MIN_CALIB_STEP=4*MIN_ANGLE_STEP_V#deg, 7.2deg for 1.8 deg stepper
    HALF_MIN_STEP_DISP=18#in optical disparity - should correspond to approx 3.6 degrees (MIN_CALIB_STEP/2).
    MAX_STEPS=6# max number of steps to find marker before giving up.
    
    def __init__(self):
        self.ser = serial.Serial(port=constants.Serial.ARDUINO_PORT,baudrate = constants.Serial.BAUD_RATE_ARDUINO,timeout=4)#,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=4)
        #self.ser = serial.Serial(port=constants.Serial.ARDUINO_PORT,baudrate = constants.Serial.BAUD_RATE_ARDUINO,timeout=4,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS)
        self.ser.flushInput()
        self.ser.flushOutput()

        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(motorsArduino.GPIO_SLEEP_V, GPIO.OUT)
        GPIO.setup(motorsArduino.GPIO_SLEEP_H, GPIO.OUT)
        
        self.motorNumber=0
        self.currentAngle=[0,0]
        
        time.sleep(1)#<0.5 means freezes as arduino misses first command

        #INITIALISE MOTORS
        self.powerOn(False, False)
        time.sleep(0.2)#speculative.  Might avoid doing things whilst power spike.
        success=self.pingArduino()
        if not success:
            self.reprogramArduino()
            
        self.setMotorNumber(motorsArduino.MOTOR_V)#always corrupts so send first command twice
        self.setSpeeds()

        self.setMotorNumber(motorsArduino.MOTOR_V)
        self.setCurrentAngleToZero()

        self.setMotorNumber(motorsArduino.MOTOR_H)
        self.setCurrentAngleToZero()

        self.mOpticalAngle=opticalAngleMarker.opticalAngleMarker()

    def setSpeeds(self):
        print('Motors: set speeds')
        self.setMotorNumber(motorsArduino.MOTOR_V)
        self.setMaxSpeed(constants.Motor.MAX_SPEED_V)
        self.setAccel(constants.Motor.ACCEL_V)

        self.setMotorNumber(motorsArduino.MOTOR_H)
        self.setMaxSpeed(constants.Motor.MAX_SPEED_H)
        self.setAccel(constants.Motor.ACCEL_H)
        
    def pingArduino(self):
        testMsg='MOTOR_NO0'
        success=self.write(testMsg)#always corrupts so send first command twice
        success=self.write(testMsg)
        return success
        
        
    def reprogramArduino(self):#sometimes power spikes can reset arduino and it can be saved by reprogramming
        try:
            if constants.Control.mProjScreen is not None:
                constants.Control.mProjScreen.showImageFromFile('red__')
            osCommands.setRW()
            
            command = "arduino --board arduino:avr:nano:cpu=atmega328old --port /dev/ttyUSB0 --upload scannerOwnMaths/scannerOwnMaths.ino"
            print(command)
            p = subprocess.check_output(command, shell=True).decode()
            print(p)
            if constants.Control.mProjScreen is not None:
                constants.Control.mProjScreen.showImageFromFile('magen')
        except Exception as e:
            print('arduino reprogram ERROR', e)
        osCommands.setRO()

    def powerOn(self, powerV, powerH):
        GPIO.output(motorsArduino.GPIO_SLEEP_V, powerV)# LOW is motor off
        time.sleep(0.2)
        GPIO.output(motorsArduino.GPIO_SLEEP_H, powerH)# LOW is motor off

    def write(self,msg):
        msg=msg+motorsArduino.DELIMITER
        print('SENDING', msg)
        try:
            self.ser.write(msg.encode())
            #self.ser.write(msg)
        except Exception as e:
            print('Serial write error', e)
        success=self.waitForReply()
        return success
    
    def writeAndRead(self,msg):
        msg=msg+motorsArduino.DELIMITER
        print('SENDING', msg)
        try:
            self.ser.write(msg.encode())
            #self.ser.write(msg)
        except Exception as e:
            print('Serial write error', e)
        msg=self.waitForReply(returnMsg=True)
        #success=self.waitForReply()
        return msg
            
    def waitForReply(self, returnMsg=False):
        msg=''
        dataByte=''
        timeoutCount=0
        while True:
            try:
                dataByte=self.ser.read().decode()
                if dataByte=='':
                    timeoutCount+=1
                    print('Arduino timeout', timeoutCount)
                    if timeoutCount>4:
                        return False
            except Exception as e:
                print('JM', e)
            if dataByte==motorsArduino.DELIMITER:
                break
            msg+=dataByte
        #print('REPLY  ', msg)
        if returnMsg:
            return msg
        return True

    def setMotorNumber(self, motorNumber):
        self.write('MOTOR_NO'+str(motorNumber))
        self.motorNumber=motorNumber

    def setMaxSpeed(self, degPerSec):
        command='MAX_SPD_'+self.floatToString(degPerSec)
        self.write(command)

    def setAccel(self, degPerSecPerSec):
        command='ACCEL___'+self.floatToString(degPerSecPerSec)
        self.write(command)

    def setCurrentAngleToZero(self):#be sure to set zero angle on multiple of 0.9 deg
        command='SET_POS_'+'00000.00'
        self.write(command)
        self.currentAngle[self.motorNumber]=0
        
    def setCurrentAngleTo(self, angle):#be sure to set zero angle on multiple of 0.9 deg
        command='SET_POS_'+ self.floatToString(angle)
        self.write(command)
        self.currentAngle[self.motorNumber]=angle

    def moveToAngle(self, angle, shortestRoute=False):
        if shortestRoute:
            if abs(angle - self.currentAngle[motorsArduino.MOTOR_H]) > 180:
                option1 = self.currentAngle[motorsArduino.MOTOR_H] + 360
                option2 = self.currentAngle[motorsArduino.MOTOR_H] - 360
                if abs(angle - option1) < abs(angle - option2):
                    self.currentAngle[motorsArduino.MOTOR_H] = option1
                    self.setMotorNumber(motorsArduino.MOTOR_H)
                    self.setCurrentAngleTo(self.currentAngle[motorsArduino.MOTOR_H])
                else:
                    self.currentAngle[motorsArduino.MOTOR_H] = option2
                    self.setMotorNumber(motorsArduino.MOTOR_H)
                    self.setCurrentAngleTo(self.currentAngle[motorsArduino.MOTOR_H])
        command='MOVE_TO_'+self.floatToString(angle)
        self.write(command)
        self.currentAngle[self.motorNumber]=angle

    def moveByAngle(self, angle):
        command='MOVE_BY_'+self.floatToString(angle)
        self.write(command)
        self.currentAngle[self.motorNumber]+=angle

    def moveToTwoAngles(self, angleV, angleH, shortestRouteH=False):
            if shortestRouteH:
                if abs(angleH-self.currentAngle[motorsArduino.MOTOR_H])>180:
                    option1=self.currentAngle[motorsArduino.MOTOR_H]+360
                    option2=self.currentAngle[motorsArduino.MOTOR_H]-360
                    if abs(angleH-option1)<abs(angleH-option2):
                        self.currentAngle[motorsArduino.MOTOR_H]=option1
                        self.setMotorNumber(motorsArduino.MOTOR_H)
                        self.setCurrentAngleTo(self.currentAngle[motorsArduino.MOTOR_H])
                    else:
                        self.currentAngle[motorsArduino.MOTOR_H]=option2
                        self.setMotorNumber(motorsArduino.MOTOR_H)
                        self.setCurrentAngleTo(self.currentAngle[motorsArduino.MOTOR_H])
            command = 'MOV_TO_M' + self.floatToString(angleV) + '&' + self.floatToString(angleH)
            self.write(command)
            self.currentAngle[motorsArduino.MOTOR_V] = angleV
            self.currentAngle[motorsArduino.MOTOR_H]=angleH
        
    def getMag(self):#TODO repeated calls cause freezing - still needs fixing. May be need to reopen port if it fails. Or add delays.
        #if constants.Info.LEVELLER=='ARD':
        command='GET_MAG_'
        msg=self.writeAndRead(command)
        #print('msg',msg)
        try:
            val=int(msg)
        except Exception as e:
            print('getMag error:',e)
            val=0
        #else:
        #    val=0
            
        return val
        

    def moveByTwoAngles(self, angleV, angleH):#NOTE changes current selected motor.
        self.setMotorNumber(0)
        self.moveByAngle(angleV)
        self.setMotorNumber(1)
        self.moveByAngle(angleH)

    def moveToZero(self):
        if constants.Info.LEVELLER=='MARKER':
            self.moveToZeroMarker()
        else:
            self.moveToZeroArd()
            
    def moveToZeroArd(self):
        print('Mag level threshold:',constants.Scanning.MAG_LEVEL)
        self.setMotorNumber(0)#V
        levelList=[0,1,-2,3,-4,5,-6,7,-8,9,-10,11,-12]
        bestVal=0
        for step in levelList:
            angle=step*self.MIN_CALIB_STEP
            self.moveByAngle(angle)
            val=self.getMag()
            print('angle,val:',angle,val)
            if val>bestVal:
                bestVal=val
                bestAngle=self.currentAngle[0]#V
            if val>=constants.Scanning.MAG_LEVEL:
                break
        if val<constants.Scanning.MAG_LEVEL:#if didn't hit threshold, then set to best value found.
            self.moveToAngle(bestAngle)  
        self.setMotorNumber(motorsArduino.MOTOR_V)
        self.setCurrentAngleTo(constants.Scanning.LEVEL_ANGLE)
        return True
    
    def moveToZeroMarker(self):
        print('moveToZeroMarker: START_TARGET',constants.Scanning.START_TARGET)
        self.setMotorNumber(motorsArduino.MOTOR_V)
        self.mOpticalAngle.initialise()
        d=self.mOpticalAngle.getDisp()#note returns 1500 if not found
        score=abs(d-constants.Scanning.START_TARGET)
        if score<self.HALF_MIN_STEP_DISP:
            self.setCurrentAngleTo(constants.Scanning.LEVEL_ANGLE)
            self.mOpticalAngle.finish()
            print('error',score)
            return True
        if (d-constants.Scanning.START_TARGET)>0:#d too high, so angle too high.
            success=self.markerSearch(direction=1)
            if success:
                return True
            else:
                self.moveByAngle(self.MIN_CALIB_STEP*self.MAX_STEPS*2)#marker not found so move back the other way and retry.
                success=self.markerSearch(direction=1)
                if success:
                    return True
                else: #failed, motor is left in original position and return
                    self.setCurrentAngleTo(constants.Scanning.LEVEL_ANGLE)
                    self.mOpticalAngle.finish()
                    return False
        else:
            success=self.markerSearch(direction=-1)
            if success:
                return True
            else:
                self.moveByAngle(-self.MIN_CALIB_STEP*self.MAX_STEPS*2)#marker not found so move back the other way and retry.
                success=self.markerSearch(direction=-1)
                if success:
                    return True
                else: #failed, motor is left in original position and return
                    self.setCurrentAngleTo(constants.Scanning.LEVEL_ANGLE)
                    self.mOpticalAngle.finish()
                    return False

        #should never reach here
        self.setCurrentAngleTo(constants.Scanning.LEVEL_ANGLE)
        self.mOpticalAngle.finish()
        print('error',score)
        return True
    
    def markerSearch(self, direction):#direction -1 or +1.  +1 is clockwise looking from model to motor.
            stepCount=0
            d=self.mOpticalAngle.getDisp()
            score=abs(d-constants.Scanning.START_TARGET)
            while score>self.HALF_MIN_STEP_DISP:
                self.moveByAngle(-self.MIN_CALIB_STEP*direction)
                d=self.mOpticalAngle.getDisp()
                score=abs(d-constants.Scanning.START_TARGET)
                stepCount+=1
                if stepCount>self.MAX_STEPS:
                    return False
                
            self.setCurrentAngleTo(constants.Scanning.LEVEL_ANGLE)
            self.mOpticalAngle.finish()
            print('error',score)
            return True

    def calibOpticalMarkerZero(self):#NOT USED, had bugs now done on PC.
        #RECORD CURRENT OPTICAL MARKER POSITION AND SAVE (WE ASSUME USER HAS SET TABLE TO LEVEL)
        self.setMotorNumber(motorsArduino.MOTOR_H)
        self.setCurrentAngleToZero()#zeros python and arduino
        self.moveToAngle(-28.8)#move plate to side to reveal optical marker

        mOpticalAngle = opticalAngleMarker.opticalAngleMarker()
        mOpticalAngle.initialise()
        startTarget = mOpticalAngle.getDisp()
        mOpticalAngle.finish()

        self.moveToAngle(0.0)#move plate to side to reveal optical marker
        self.setMotorNumber(motorsArduino.MOTOR_V)
        self.setCurrentAngleTo(constants.Scanning.LEVEL_ANGLE)

        print('START_TARGET',startTarget)#NOW OPTICAL MARKER CALIB IS FINISHED
        #constants.Scanning.START_TARGET=startTarget#to store in constants, as it is not necessarily loaded from calibData
        return startTarget

                
    def antiHysteresis(self):
        self.moveByAngle(-self.MIN_CALIB_STEP)
        self.moveByAngle(self.MIN_CALIB_STEP)


    def getOpticalValue(self):
        return self.opticalAngle.getDisp()
    
    def floatToString(self, angle):
        return '{:08.2f}'.format(angle)

def testLeveller():
    constants.Scanning.START_TARGET=630
    constants.Control.mCapture=captureVideo.capture(preview=False)
    #mProjScreen=projScreen.projScreen()
    mMotors=motorsArduino()
    mMotors.powerOn(True, True)
    mMotors.setMotorNumber(motorsArduino.MOTOR_V)
    mMotors.moveToZero()#is always V movement
    
    
def test():
    mMotors=motorsArduino()
    mMotors.powerOn(True, True)
    mMotors.moveToZeroArd()
    exit()
    index=0
    while True:
        val=mMotors.getMag()
        print('val',val, index)
        time.sleep(0.005)
        index+=1
        
if __name__ == "__main__":
    #test()
    #exit()
    testLeveller()
    exit()
    #constants.Scanning.START_TARGET=671
    #constants.Control.mCapture=captureVideo.capture(preview=False)
    #mProjScreen=projScreen.projScreen()
    mMotors=motorsArduino()
    mMotors.powerOn(True, True)
    mMotors.setMotorNumber(motorsArduino.MOTOR_V)
    mMotors.moveToAngle(0)
    #mMotors.setCurrentAngleToZero()
    #mMotors.moveToZero(mProjScreen=mProjScreen, capture=constants.Control.mCapture)#is always V movement
    #mMotors.moveToTwoAngles(-48.6,0)
    exit()
    
    def test(mMotors):
        for i in range(2,30,6):
            #mMotors.setMotorNumber(motorsArduino.MOTOR_V)
            #mMotors.moveToAngle(i*3)
            #mMotors.setMotorNumber(motorsArduino.MOTOR_H)
            #mMotors.moveToAngle(i*7)
            mMotors.moveToTwoAngles(i*3, i*7)
            mMotors.moveToTwoAngles(i*1, i*3)
            print(i)
            #print(mMotors.currentAngle[0])
        
        
    #mBTserver=BTserver.BTserver()
    #mBTserver=None
    #constants.Control.mCapture=captureVideo.capture(preview=False)
    #constants.Control.mCapture=None
    #GPIO.cleanup()
    mMotors=motorsArduino()
    mMotors.setMotorNumber(motorsArduino.MOTOR_V)
    mMotors.powerOn(True, True)
    #mMotors.powerOn(False, False)
    #exit()
    #mMotors.moveToZero(BTserver=mBTserver, capture=constants.Control.mCapture)
    
    #mMotors.setMotorNumber(motorsArduino.MOTOR_V)
    #mMotors.moveToAngle(3)
            
    tick=time.perf_counter()
    test(mMotors)
    mMotors.moveToTwoAngles(0, 0)
    print('test time',time.perf_counter()-tick)
    
    #constants.Control.mCapture.closeCamera()
    mMotors.powerOn(False, False)
    exit()
    
    msg=""
    while True:
        msg=input("E")
        if msg=="E": break
        #for i in range(64):
        #    mMotorH.step()
        #mMotorH.moveToAngle(0)
        
        #mMotors.setMotorNumber(motorsArduino.MOTOR_H)
        mMotors.setMotorNumber(motorsArduino.MOTOR_V)
        mMotors.moveToAngle(float(msg),shortestRoute=False)
        #mMotors.moveToAngle(float(msg))
        #mMotors.setMotorNumber(motorsArduino.MOTOR_H)
        #mMotors.moveToAngle(float(msg),shortestRoute=True)
        #print(mMotors.currentAngle[mMotors.motorNumber])
        
        #mMotors.moveToTwoAngles(float(msg)/4, float(msg))
        
        
        #print(mMotorH.getCurrentStep())
        #mMotorV.moveByAngle(-60)

        
        
    mMotors.powerOn(False, False)
    #mMotorV.powerOn(False)
    constants.Control.mCapture.closeCamera()
    


