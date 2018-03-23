import RPi.GPIO as GPIO
import time
from picamera import PiCamera
from picamera.array import PiRGBArray
import cv2

######## Fill constants here ########
cmPerPixel = 5.9/1104.0
checkWidth = 30
removeLastElements = 3
removeFirstElements = 2
#####################################

class Image:
    processed_image_index = 0

    def __init__(self):
        self.is_pic_taken = False
        self.is_pic_processed = False

    def take_image(self, camera, rawCapture):
        camera.capture(rawCapture, format='bgr')
        self.image = rawCapture.array
        self.is_pic_taken = True

    def process_image(self):
       if self.is_pic_taken:
           if not self.is_pic_processed:
                if not process(self.image):
                    print("Error in measuring bolt dimensions")
                else:
                    self.is_pic_processed = True


def process(bolt_image):
    retval, binaryImage = cv2.threshold(bolt_image.image[:,:,2], 80, 255,
    cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    thread_row = np.array([])
    thread_col = np.array([])

    nonz_r, nonz_c = binaryImage.nonzero()
    last_col = max(nonz_c)
    first_col = min(nonz_c) - 2
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

    if valley_row.size > peak_row.size:
        arr_length = peak_row.size
    else:
        arr_length = valley_row.size

    valley_row = valley_row[removeFirstElements : arr_length - removeLastElements]
    valley_col = valley_col[removeFirstElements : arr_length - removeLastElements]
    peak_row = peak_row[removeFirstElements : arr_length - removeLastElements]
    peak_col = peak_col[removeFirstElements : arr_length - removeLastElements]

    length_of_bolt = np.abs(thread_col[0] - thread_col[-1])

    thread_pitch = np.mean(np.diff(peak_col, 1)
    thread_height = np.mean(peak_row - valley_row)

