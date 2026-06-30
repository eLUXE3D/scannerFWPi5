import os
import time
import constants


#https://www.text2speech.org/


def setVolume(volume=100):
    os.system('sudo amixer cset numid=1 '+str(volume)+'%')
    
def file(soundCode=constants.Sounds.STOP_PING):
    setVolume(int(constants.Scanning.SOUND))
    #if constants.Info.HW_VERSION[:1] == '2':  # if v2.x
    #    os.system('aplay Sounds/silence.wav')#initialise audio so first bit of sound does not go missing
    #    time.sleep(0.8)
    if soundCode==constants.Sounds.START_PING:
        os.system('aplay Sounds/start_ping.wav &')
    if soundCode == constants.Sounds.STOP_PING:
        os.system('aplay Sounds/stop_ping.wav &')
    if soundCode == constants.Sounds.PROCESSING:
        os.system('aplay Sounds/processing.wav &')
    if soundCode == constants.Sounds.CALIBRATING:
        os.system('aplay Sounds/calibrating.wav &')
    if soundCode == constants.Sounds.SCAN_COMPLETE:
        os.system('aplay Sounds/scan_complete.wav &')
    if soundCode == constants.Sounds.READY_TO_SCAN:
        os.system('aplay Sounds/ready_to_scan.wav &')
    if soundCode == constants.Sounds.SHUTTING_DOWN:
        os.system('aplay Sounds/shutting_down.wav &')
    if soundCode == constants.Sounds.MUSIC:
        os.system('aplay Sounds/music.wav &')
    if soundCode == constants.Sounds.CALIBRATION_FAILED:
        os.system('aplay Sounds/calibration_failed.wav &')
    if soundCode == constants.Sounds.QR_NOT_FOUND:
        os.system('aplay Sounds/QRnotFound.wav &')  

    return

if __name__ == "__main__":
    #setVolume(100)
    file(soundCode=constants.Sounds.PROCESSING)
    time.sleep(3)
    #file(soundCode=constants.Sounds.MUSIC)
    
