Copyright 2019 Tupel Ltd. all rights reserved.

What folders are in this zip:

1). Arduino
 - Source code for the arduino firmware (that controls the turntable).
 - The pi-installer is used on the pi to reflash the arduino in case it loses its data.
 
2). InstallV2
 - has files that needs to be copied to the pi during installation.
 
3). Release2
 - Source code for the pi firmware.

4). Tools
 - Setup.py creates the license whitelists.
 - It adds into the update the latest calibration plate files.
 
5). TQDM - some 3rd party library that I think is required build process.

6). Wifi
 - Notes on wifi setup for the pi
 
7). key copies for eluxe
 - keys for building the PC software - which you presumably already have.
 
obfuscateV2.sh
  - Run on a pi to build the source code to a new hardware version
  
V5p00main.zip
  - The latest firmware version
  - run tools/fileCompare.py to find only the files that changed since the last firmware, so the user can update only necessary files (faster).