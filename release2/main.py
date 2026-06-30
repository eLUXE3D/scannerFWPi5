import os
import constants
import lanServerMaster
import subprocess
import sys
sys.setrecursionlimit(5000)

#os.chdir('/home/pi/main')
print('Working dir', os.getcwd())

#sys.stdout = open(os.devnull, 'w')  # Disable print
#sys.stdout = sys.__stdout__  # Restore print

#keep screen always on for proj
subprocess.call(['sudo', 'xset', 's','off'])
subprocess.call(['sudo', 'xset', '-dpms'])
subprocess.call(['sudo', 'xset', 's','noblank'])
while True:
    lanServerMaster.startServer()
