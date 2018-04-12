import RPi.GPIO as GPIO
import time
from picamera import PiCamera
from picamera.array import PiRGBArray
import cv2
import numpy as np
import math

######## Fill constants here ########
cmPerPixel = 1/174.92
checkWidth = 10
removeLastElements = 2
removeFirstElements = 2
threadEnd = 35
totalImages = 16
totalSteps = 512
sinLaserAngle = math.sin(math.radians(55.54))
halfHeight = 1080 / 2
#####################################

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

camera = PiCamera()
camera.resolution = (1920, 1088)
#camera.framerate = (1, 10)
#camera.shutter_speed = 10000
#camera.exposure_mode = 'off'
rawCapture = PiRGBArray(camera)
time.sleep(0.1)
camera.capture(rawCapture, format="bgr")
rawCapture.truncate()
rawCapture.seek(0)
time.sleep(1)

GPIO.output(enable_pin, 1)


class Image:
    processed_image_index = 0

    def __init__(self):
        self.image = np.array([])
        self.is_pic_taken = True
        self.is_pic_processed = False

    def take_image(self):
        camera.capture(rawCapture, format='bgr')
        self.image = rawCapture.array
        self.is_pic_taken = True
        self.is_pic_processed = False
        rawCapture.truncate()
        rawCapture.seek(0)

    def process_image(self, index):
       if self.is_pic_taken:
           #print("Hello")
           if not self.is_pic_processed:
                if process(self.image, index):
                    #print("processed")
                    self.is_pic_processed = True
                else:
                    print("errorororor")


def show_peak_valley(img, v_row, v_column, p_row, p_column, index):
    #cv2.circle(img, (250, 250), 50, (100, 50, 200), -1)
    for i in range(v_row.shape[0]):
        cv2.circle(img, (int(v_column[i]), int(v_row[i])), 1, (0, 255, 0), -1)

    for i in range(p_row.shape[0]):
        cv2.circle(img, (int(p_column[i]), int(p_row[i])), 1, (255, 0, 0), -1)

    cv2.imshow("image"+str(index), img)


def find_peak(th_row, th_col):
    start=time.time()
    rows = th_row.shape[0]
    check_width = 30
    p_row = np.array([], np.int16)
    p_column = np.array([], np.int16)
    i = check_width
    end_flag = False
    first_time = True
    
    while i < rows - check_width:
        
        if th_row[i] <= th_row[i-1] and th_row[i] <= th_row[i+1]:
            peak_flag = True
            
            for p in range(1, check_width):
                if th_row[i] > th_row[i-p] or th_row[i] > th_row[i+p]:
                    peak_flag = False
                    break

            if peak_flag:
                if first_time:
                    first_time = False
                elif p_row[-1] - th_row[i] > threadEnd:
                    #print("thread length is " + str((th_col[i] - th_col[0])*cmPerPixel))
                    end_flag = True
                    break
                p_row = np.append(p_row, th_row[i])
                p_column = np.append(p_column, th_col[i])
                i += check_width - 5
        
        if end_flag:
            break
        i += 1
    stop=time.time()-start
    #print(stop)
    #print("sizep"+str(p_row.size))
    return p_row, p_column


def find_valley(th_row, th_col):
    start=time.time()
    rows = th_row.shape[0]
    check_width = 30
    v_row = np.array([], np.int16)
    v_column = np.array([], np.int16)
    i = check_width
    end_flag = False
    first_time = True

    while i < rows - check_width:
        
        if th_row[i] >= th_row[i-1] and th_row[i] >= th_row[i+1]:
            valley_flag = True
            
            for p in range(1, check_width):
                if th_row[i] < th_row[i-p] or th_row[i] < th_row[i+p]:
                    valley_flag = False
                    break

            if valley_flag:
                if first_time:
                    first_time = False
                elif (v_row[-1] - th_row[i]) > threadEnd:
                        end_flag = True
                        break
                v_row = np.append(v_row, th_row[i])
                v_column = np.append(v_column, th_col[i])
                i += check_width - 5
        
        if end_flag:
            break
        i += 1
    stop=time.time()-start
    #print(stop)
    return v_row, v_column



def process(bolt_image, index):
    #bolt_image = cv2.medianBlur(bolt_image, 3)
    retval, binaryImage = cv2.threshold(bolt_image[:,:,2], 80, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    thread_row = np.array([])
    thread_col = np.array([])
    kernel = np.ones((3, 3))
    binaryImage = cv2.morphologyEx(binaryImage, cv2.MORPH_OPEN, kernel)
    cv2.imshow("bin" +str(index), binaryImage)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    #print("nonzero " +str(np.count_nonzero(binaryImage)))
    nonz_r, nonz_c = binaryImage.nonzero()
    last_col = max(nonz_c)
    first_col = min(nonz_c)
    if(first_col < 0):
        first_col = 0

    for column in range(first_col, last_col):
        col_array = binaryImage[:, column]
        white = np.where(col_array != 0)[0]
        if white.size != 0:
            thread_row = np.append(thread_row, int(white[0]))
            thread_col = np.append(thread_col, column)

    valley_row, valley_col = find_valley(thread_row, thread_col)
    peak_row, peak_col = find_peak(thread_row, thread_col)
    thread_diff = np.where(np.diff(thread_col, 1) > 50)
    #print(thread_diff)
    if valley_row.size > 0 and valley_row.size > peak_row.size:
        arr_length = peak_row.size
    elif peak_row.size > 0 and peak_row.size > valley_row.size:
        arr_length = valley_row.size
    else:
        arr_length = -1

    if arr_length != -1:
        valley_row = valley_row[removeFirstElements : arr_length - removeLastElements]
        valley_col = valley_col[removeFirstElements : arr_length - removeLastElements]
        peak_row = peak_row[removeFirstElements : arr_length - removeLastElements]
        peak_col = peak_col[removeFirstElements : arr_length - removeLastElements]
    #print(peak_row)
    global radius_array
    if(index < totalImages / 2):
        radius_array = np.append(radius_array, int(halfHeight - peak_row[-1]))
    else:
        radius_array[int(index % (totalImages / 2))] += halfHeight - peak_row[-1]
    print("radius")
    print(radius_array)
    #print("thread peak greter than half")
    #print(peak_row[np.where(peak_row > 540)])
    length_of_bolt = np.abs(thread_col[0] - thread_col[-1])

    thread_pitch = np.mean(np.diff(peak_col, 1))
    thread_height = abs(np.mean(peak_row - valley_row))


    global pitch_array
    pitch_array = np.append(pitch_array, thread_pitch)
    global length_array
    length_array = np.append(length_array, length_of_bolt)
    global height_array
    height_array = np.append(height_array, thread_height)
    #show_peak_valley(bolt_image, valley_row, valley_col, peak_row, peak_col, index)
    #print("Thread pitch is " + str(thread_pitch*cmPerPixel))
    #print("Length of bolt is " + str(length_of_bolt*cmPerPixel))
    #print("Thread Height is " + str(thread_height*cmPerPixel))
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    return True

def setStep(w1, w2, w3, w4):
    GPIO.output(coil_A_1_pin, w1)
    GPIO.output(coil_A_2_pin, w2)
    GPIO.output(coil_B_1_pin, w3)
    GPIO.output(coil_B_2_pin, w4)

def main_loop(image_obj):
    delay_rotate = 5/1000.0
    for index in range(0, totalImages):
        eachStep(delay_rotate)
        setStep(0, 0, 0, 0)
        GPIO.output(laser_pin, True)
        time.sleep(0.01)
        image_obj.take_image()
        GPIO.output(laser_pin, False)
        time.sleep(0.05)
        #print("index " + str(index))
        #if(index < 2):
        image_obj.process_image(index)
        #time.sleep(1)
    
def eachStep(delay):
    fourStepRotations = int(totalSteps / totalImages)
    for i in range(0, fourStepRotations):
        setStep(1, 0, 1, 0)
        time.sleep(delay)
        setStep(0, 1, 1, 0)
        time.sleep(delay)
        setStep(0, 1, 0, 1)
        time.sleep(delay)
        setStep(1, 0, 0, 1)
        time.sleep(delay)


radius_orig = float(input('Enter radius of the Bolt in cm: '))
length_orig = float(input('Enter length of the Bolt in cm: '))
pitch_orig = float(input('Enter thread pitch of the Bolt: '))
height_orig = float(input('Enter thread height of the Bolt: '))
start = time.time()
radius_array = np.array([])
pitch_array = np.array([])
length_array = np.array([])
height_array = np.array([])
#print(radius_array)
image_obj = Image()
main_loop(image_obj)
np.mean(radius_array)
radiusInCm = np.mean(radius_array) * cmPerPixel / sinLaserAngle
lengthInCm = np.mean(length_array) * cmPerPixel
pitchInCm = np.mean(pitch_array) * cmPerPixel
heightInCm = np.mean(height_array) * cmPerPixel / sinLaserAngle
print("Radius of Bolt " + str(radiusInCm))
print("Length of Bolt " + str(lengthInCm))
print("Thread pitch of Bolt " + str(pitchInCm))
print("Thread height of Bolt " + str(heightInCm))
print("time " +str(time.time() - start))
#image_obj.take_image()
#image_obj.image = cv2.imread('/home/theabysswalker/Documents/Dimensional-Accuracy-Assertion/znap5.jpg')
#cv2.imshow("asd",image_obj.image)
#image_obj.process_image()
#cv2.waitKey(0)
#cv2.destroyAllWindows()
