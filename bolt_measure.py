import cv2
import time
import numpy as np

cmPerPixel = 5.9/1104.0
removeLastElements = 2
removeFirstElements = 1

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
                elif p_row[-1] - th_row[i] > 50:
                    end_flag = True
                    break
                p_row = np.append(p_row, th_row[i])
                p_column = np.append(p_column, th_col[i])
                i += check_width - 5
        
        if end_flag:
            break
        i += 1
    stop=time.time()-start
    print(stop)
    print("sizep"+str(p_row.size))
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
                elif (v_row[-1] - th_row[i]) > 50:
                        end_flag = True
                        break
                v_row = np.append(v_row, th_row[i])
                v_column = np.append(v_column, th_col[i])
                i += check_width - 5
        
        if end_flag:
            break
        i += 1
    stop=time.time()-start
    print(stop)
    return v_row, v_column


def glare_noise(p_row,v_row):
    start=time.time()
    p_avg=np.mean(p_row)
    noisepos_peak=list()
    for i in range(0,len(p_row)):
        if(p_row[i]> p_avg+60 or p_row[i]< p_avg-60):
            noisepos_peak.append(i)
                
    peak=np.array(np.delete(p_row,noisepos_peak),np.int16)
    
    v_avg=np.mean(v_row)
    noisepos_valley=list()
    for i in range(0,len(valley_row)):
        if(v_row[i]> v_avg+60 or v_row[i]< v_avg-60):
            noisepos_valley.append(i)
    
    valley=np.array(np.delete(v_row,noisepos_valley),np.int16)
    
    
    stop=time.time()-start
    print(stop)
    
    return peak,valley


def show_peak_valley(img, v_row, v_column, p_row, p_column):
    #cv2.circle(img, (250, 250), 50, (100, 50, 200), -1)
    for i in range(v_row.shape[0]):
        cv2.circle(img, (int(v_column[i]), int(v_row[i])), 1, (0, 255, 0), -1)

    for i in range(p_row.shape[0]):
        cv2.circle(img, (int(p_column[i]), int(p_row[i])), 1, (255, 0, 0), -1)

    cv2.imshow("valleysssss", img)


start=time.time()
img = cv2.imread('znap24.jpg')


#img = img[380:600, 500:1550]
img = cv2.imread('/home/theabysswalker/Documents/Dimensional-Accuracy-Assertion/znap5.jpg')

#img = img[400:600, 500:1800]

redChannel = img[:, :, 2]
#redChannel = cv2.bilateralFilter(redChannel, 10, 100, 100)

retval,binaryImage = cv2.threshold(redChannel, 80, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

thread_row = np.array([])
thread_col = np.array([])
top = 0
bottom = 0
#print(binaryImage.shape[0])
#print(binaryImage.shape[1])

rownonzero_pos,colnonzero_pos=binaryImage.nonzero()
width = max(colnonzero_pos)
height = max(rownonzero_pos)

mini_col=min(colnonzero_pos)-50
mini_row=min(rownonzero_pos)-50
print("min "+str(mini_col) + " " +str(mini_row))
print("min "+str(width) + " " +str(height))

if(mini_row<0):mini_row=0
if(mini_col<0):mini_col=0
stt=time.time()
for column in range(mini_col,width,1):
    c = binaryImage[:,column]
    white = np.where(c!=0)[0]
    if (white.size != 0):
        thread_row = np.append(thread_row, int(white[0]))
        thread_col = np.append(thread_col, column)

print("now " + str(time.time()-stt))

'''            This is your version
temp_row = np.array([])
temp_col = np.array([])
stt=time.time()
for column in range(mini_col,width,1):

    for row in range(mini_row,height,2):
        if binaryImage[row, column] != 0:
            temp_row = np.append(temp_row, row)
            temp_col = np.append(temp_col, column)
            break
print("bolu's "+str(time.time()-stt))
#temp = np.diff(thread_row, 1)
#temp = np.where(temp < -50)
#print("Hello")
#print(temp)
'''

temp = np.diff(thread_row, 1)
temp = np.where(temp < -50)
print("Hello")
print(temp)

valley_row, valley_column = find_valley(thread_row, thread_col)

peak_row, peak_column = find_peak(thread_row, thread_col)

top = thread_col[0]
bottom = thread_col[-1]

print("No of pixels from top to bottom is {}".format((bottom - top) * cmPerPixel))
#print("Time is {}".format(stop-start))
if valley_row.size > peak_row.size:
    arr_length = peak_row.size
else:
    arr_length = valley_row.size
valley_row = valley_row[removeFirstElements : arr_length - removeLastElements]
valley_column = valley_column[removeFirstElements : arr_length - removeLastElements]
peak_row = peak_row[removeFirstElements : arr_length - removeLastElements]
peak_column = peak_column[removeFirstElements : arr_length - removeLastElements]

print("Peaks:")
print(peak_row)
print("their pos:")
print(peak_column)
print("peak diff")
print(np.diff(peak_column, 1))

print("Valleys")
print(valley_row)
print("their pos:")
print(valley_column)
print("valley diff")
print(np.diff(valley_column,1)*5.9/1104)
print("thread pitch")

thread_pitch = np.mean(np.diff(peak_column, 1))
thread_height = abs(np.mean(peak_row - valley_row))
print(thread_pitch * cmPerPixel)
print("thread height")
print(thread_height * cmPerPixel)
show_peak_valley(img, valley_row, valley_column, peak_row, peak_column)

#peak_row,valley_row=glare_noise(peak_row,valley_row)
stop=time.time()-start
show_peak_valley(img, valley_row, valley_column, peak_row, peak_column)
print("total time",stop)
#cv2.imshow('org', redChannel)
cv2.imshow('otsu', binaryImage)

cv2.waitKey(0)
cv2.destroyAllWindows()
