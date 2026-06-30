import subprocess
import time
import os


def setRW():
    print('rw')
    try:
        command = "sudo mount -o remount,rw /"
        p = subprocess.check_output(command, shell=True).decode()
        command = "sudo mount -o remount,rw /boot"
        p = subprocess.check_output(command, shell=True).decode()
    except Exception as e:
        print('ERROR RW: ',e)

def setRO():
    #had a concern that this does not flush buffer before changing to ro and so could cause corruption.
    #not sure if this is true or not.
    #options:
    # could sleep 5 sec
    # could do f.flush(), os.fsync(f.fileno()), f.close() to force data to disk first - flush does sw buffers, fsync blocks until disk write acknowledged.
    #https://www.geeksforgeeks.org/python-os-fsync-method/#:~:targetText=os.,flush()%20and%20then%20os.
    # could do both - sometimes (e.g. unzip), have no control of buffers and file handles.
    #could update all 20 units now, or do on next update.
    #Decision: probably actually ok, so do on next batch/ next HW update, and worst case ship out new sd cards.
    #os.sync() is better because it does all files.
    #could do mount rw, sync      :so never chop data writes?

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
        
def getDiskInfo():
    try:
        #command = "cat /proc/cpuinfo |grep Serial|cut -d' ' -f2"
        command = "dstat -d -D /dev/mmcblk0p2 1 1"
        diskInfo = subprocess.check_output(command, shell=True).decode()
        #p=p[0:16]
    except Exception as e:
        print('ERROR dstat', e)
        return 'NoData'
    
    return diskInfo

def fixDisk():#can do fix disk since it is mounted RO, may help to fix if corrupted by switch off during red screen.
    print('fixDisk start')
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

    print('fixDisk done')


def osReboot():
    print('REBOOT (Tupel)')
    setRO()
    time.sleep(3)
    command = "sudo reboot -f"
    print(command)
    p = subprocess.check_output(command, shell=True).decode()
    print(p)
    
if __name__ == "__main__":
    diskInfo=getDiskInfo()
    print(diskInfo)
    
    
