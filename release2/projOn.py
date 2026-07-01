import RPi.GPIO as GPIO
import time

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

projOn()


