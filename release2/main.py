import os
import constants
import lanServerMaster
import lanServerSlave
import subprocess
import sys
sys.setrecursionlimit(5000)

#test
#import scanMaster

#os.chdir('/home/pi/main')
print('Working dir', os.getcwd())

#exit()

#sys.stdout = open(os.devnull, 'w')  # Disable print
#sys.stdout = sys.__stdout__  # Restore print

if os.uname()[1] in (constants.Info.MASTER_UNAME, constants.Info.PI5_UNAME):
    #keep screen always on for proj
    subprocess.call(['sudo', 'xset', 's','off'])
    subprocess.call(['sudo', 'xset', '-dpms'])
    subprocess.call(['sudo', 'xset', 's','noblank'])
    while True:
        lanServerMaster.startServer()
    #scanMaster.speedTest()

if os.uname()[1]==constants.Info.SLAVE_UNAME:
    while True:
        lanServerSlave.startServer()
