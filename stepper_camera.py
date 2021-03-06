import RPi.GPIO as GPIO
import time
import picamera
 
GPIO.setmode(GPIO.BCM)
 
enable_pin = 18
coil_A_1_pin = 4
coil_A_2_pin = 17
coil_B_1_pin = 23
coil_B_2_pin = 24
laser_pin = 3
 
GPIO.setup(enable_pin, GPIO.OUT)
GPIO.setup(coil_A_1_pin, GPIO.OUT)
GPIO.setup(coil_A_2_pin, GPIO.OUT)
GPIO.setup(coil_B_1_pin, GPIO.OUT)
GPIO.setup(coil_B_2_pin, GPIO.OUT)
GPIO.setup(laser_pin, GPIO.OUT)

camera = picamera.PiCamera()
time.sleep(1)

GPIO.output(enable_pin, 1)
  
def setStep(w1, w2, w3, w4):
    GPIO.output(coil_A_1_pin, w1)
    GPIO.output(coil_A_2_pin, w2)
    GPIO.output(coil_B_1_pin, w3)
    GPIO.output(coil_B_2_pin, w4)

def rotate():
    delay_rotate = 5/1000.0
    for i in range(0, 25):
        fourStepForward(delay_rotate)
        print(i)
        setStep(0, 0, 0, 0)
        time.sleep(0.2)
        GPIO.output(laser_pin, True)
        time.sleep(0.2)
        camera.capture('znap' + str(i) + '.jpg')
        GPIO.output(laser_pin, False)
        #time.sleep(1)
        time.sleep(0.2)
    
def fourStepForward(delay):
    for i in range(0, 40):
        setStep(1, 0, 1, 0)
        time.sleep(delay)
        setStep(0, 1, 1, 0)
        time.sleep(delay)
        setStep(0, 1, 0, 1)
        time.sleep(delay)
        setStep(1, 0, 0, 1)
        time.sleep(delay)

#while True:
    #setStep(0, 0, 0, 0)
    #rotate()
setStep(0, 0, 0, 0)
rotate()

