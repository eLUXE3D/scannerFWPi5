import os
import subprocess
import shutil

#to check which files have been changed so can make small update.zip files
#typically:
#CHANGE: base_library.zip
#CHANGE: license.lic
#CHANGE: main

#license is genuinely different.
#so add all into update.zip

# NOTE PW
#     nb*I2$jxMnNl60I+t&EE1GU0HbWert!

# directory1 = 'compare/V4p01main' #(orig)
# directory2 = 'compare/V4p02main' #(new)
# zipDir='compare/V4p02main'
# updateZip = '../updateV4p01toV4p02.zip'

directory1 = 'C:/Work-Data/TeethCompare/V4p07main' #(orig)
directory2 = 'C:/Work-Data/TeethCompare/V5p00main' #(new)
zipDir='C:/Work-Data/TeethCompare/V5p00main'#new
updateZip = '../updateV4p07toV5p00.zip'

def getNewAndChangedFiles():

    files1=[]
    files2=[]
    newOrChangedFiles=[]

    #GET ALL FILES IN DIR2 (new)
    for r, d, f in os.walk(directory2):
        #print(r, d, f)
        for filename in f:
            file2=os.path.join(r, filename)
            #print(file2)
            files2.append(file2)
    #print(files2)

    #IF DIR2 files NEW OR CHANGED, ADD TO LIST
    for file2 in files2:
        file1=file2.replace(directory2, directory1)
        #print(file2, file1)
        if not os.path.isfile(file1):
            print('NEW FILE:', file2)
            newOrChangedFiles.append(file2)
            continue
        if open(file1,'rb').read() == open(file2,'rb').read():
            pass
            #print('NO CHANGE:',file2)
        else:
            print('CHANGE:', file2)
            newOrChangedFiles.append(file2)

    return newOrChangedFiles

def addFilesToUpdateZip(files):
    #CHANGE WORKING DIRECTORY TO zipDir
    os.chdir(zipDir)
    print(os.getcwd())

    for fileToZip in files:
        if 'calibrationData.npz' in fileToZip:#don't overwrite calibration data during an update
            print('SKIPPING: ', fileToZip)
            continue
        fileToZip=fileToZip.replace(directory2+'\\', '')
        command='"C:/Program Files/7-Zip/7z.exe" a "'+updateZip+'" ' + fileToZip + ' -p"nb*I2$jxMnNl60I+t&EE1GU0HbWert!"'
        print(command)
        p=subprocess.check_output(command, shell=True).decode()
        #print (p)

    print ("zip finished")


if __name__ == "__main__":
    #REMOVE OLD ZIP
    updateZipPathAndFilename=zipDir+'/'+updateZip
    if os.path.isfile(updateZipPathAndFilename):
        os.remove(updateZipPathAndFilename)

    newOrChangedFiles=getNewAndChangedFiles()
    addFilesToUpdateZip(newOrChangedFiles)
    shutil.copy(updateZip, 'C:/Users/mathe/My Drive (tupeluk@gmail.com)/SharedFolders/ScannerSoftwareReleases/HWupdates/'+updateZip[3:])
    print('Copied new resource' + updateZip[3:] +' to C:/Users/mathe/My Drive/SharedFolders/ScannerSoftwareReleases/HWupdates/'+updateZip[3:])

