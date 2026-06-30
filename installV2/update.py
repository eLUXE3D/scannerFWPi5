import zipfile
import os
import subprocess
import RPi.GPIO as GPIO
import time

updateFilename = 'update.zip'  # update in update.py also
UPDATE_PWD = b'nb*I2$jxMnNl60I+t&EE1GU0HbWert!'

def projOn():
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(12,GPIO.OUT)
        GPIO.output(12,GPIO.HIGH)
        time.sleep(1)
        GPIO.output(12,GPIO.LOW)
        time.sleep(1)
        GPIO.output(12, GPIO.HIGH)
        print('ProjOn')
    except Exception as e:
        print('ERROR: projOn', e)
    
def fixDisk():#can do fix disk since it is mounted RO, may help to fix if corrupted by switch off during red screen.
    print('diskCheck start')
    try:
        p='no data'
        command = "sudo fsck -f -y /dev/mmcblk0p1"
        p = subprocess.check_output(command, shell=True).decode()
        print(p)
    except Exception as e:
        print(p)
        print('ERROR: diskCheck1', e)

    try:
        p = 'no data'
        command = "sudo fsck -f -y /dev/mmcblk0p2"
        p = subprocess.check_output(command, shell=True).decode()
        print(p)
    except Exception as e:
        print(p)
        print('ERROR: diskCheck2', e)

    print('diskCheck done')


def update():
    try:
        if os.path.isfile(updateFilename):
            # UNZIP
            setRW()
            the_zip_file = zipfile.ZipFile(updateFilename)
            the_zip_file.setpassword(UPDATE_PWD)
            the_zip_file.extractall(path=None, members=None, pwd=UPDATE_PWD)
            print('Updated')
        else:
            print('no update')
            return False
    except Exception as e:
        print(e)
        print('update fail')

    try:
        os.remove(updateFilename)
        # setRO()
        print('Update success')
    except Exception as e:
        print(e)
        print('update fail to remove update zip')

    return True

def isChargeMode():
    try:
        chargeModeFile='chargeMode.txt'
        if os.path.isfile(chargeModeFile):
            setRW()
            os.remove(chargeModeFile)
            #setRO()
            print('CHARGE MODE')
            return True
        else:
            print('NOT CHARGE MODE')
    except Exception as e:
        print('charge mode detect fail',e)
    
    return False


def runBatchFile():
    try:
        batchFile = 'batchFile.sh'
        if os.path.isfile(batchFile):
            setRW()
            try:
                p = 'no data'
                command = "sudo sh batchFile.sh"
                p = subprocess.check_output(command, shell=True).decode()
                print(p)
            except Exception as e:
                print(p)
                print('ERROR: runBatchFile', e)
            os.remove(batchFile)
            # setRO()
            return True
        else:
            print('NO BATCH FILE')
    except Exception as e:
        print('runBatchFile fail', e)

    return

def setRW():
    print('rw')
    try:
        command = "sudo mount -o remount,rw /"
        p = subprocess.check_output(command, shell=True).decode()
        command = "sudo mount -o remount,rw /boot"
        p = subprocess.check_output(command, shell=True).decode()
    except Exception as e:
        print('ERROR RW: ',e)

def setRO():#fails in start up script, so I do it in main
    print('ro')
    try:
        os.sync()
        time.sleep(3)
        command = "sudo mount -o remount,ro /"
        p = subprocess.check_output(command, shell=True).decode()
        command = "sudo mount -o remount,ro /boot"
        p = subprocess.check_output(command, shell=True).decode()
    except Exception as e:
        print('ERROR RO: ',e)

updated=update()
chargeMode=isChargeMode()
runBatchFile()
if not updated and not chargeMode:#don't turn proj on if doing a reboot (because double on reverts projector to main menu).
    projOn()
#fixDisk()#risks corruption if power cut so disabled.

