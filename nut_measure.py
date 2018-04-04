import cv2
import time
import numpy as np
import math

check = 5
sliceWidth = 480

def find_peak(th_row, th_col):
    
    rows = th_row.shape[0]
    check_width = 20
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
    print("sizep"+str(p_row.size))
    return p_row, p_column

def show_peak_valley(img, bina, th_row, th_col):
    #cv2.circle(img, (250, 250), 50, (100, 50, 200), -1)
    for i in range(th_row.shape[0]):
        #if(bina[int(v[i][1]),int(v[i][0])] !=0):
        cv2.circle(img, (int(th_row[i]), int(th_col[i])), 1, (0, 255, 0), -1)

    cv2.imshow("valleysssss", img)


img = cv2.imread('/home/theabysswalker/Documents/Dimensional-Accuracy-Assertion/nut2.jpg')

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
first_half = binaryImage[:, :sliceWidth]
second_half = binaryImage[:, sliceWidth:]
rownonzero_pos,colnonzero_pos = first_half.nonzero()
last_col = max(colnonzero_pos)
nut_col = first_half[:, last_col]
last_row = np.where(nut_col != 0)[0][0]
print("last row " + str(last_row))
for i in range(check):
    sec_col = second_half[last_row + i, :]
    #print(str(i)+"th row down")
    #print(sec_col)
    pix = np.where(sec_col != 0)[0]
    if pix.size > 0:
        print("down " +str(i))
        print(pix[0])
        r = last_row + i
        c = pix[0]
        cv2.circle(img[:, sliceWidth:], (c, r),1, (255,0,0),-1)
        break
    sec_col = second_half[last_row - i, :]
    #print(str(i)+"th row up")
    #print(sec_col)
    pix = np.where(sec_col != 0)[0]
    if pix.size > 0:
        print("up " +str(i))
        print(pix[0])
        r = last_row - i
        c = pix[0]
        cv2.circle(img[:, sliceWidth:], (c, r),1, (255,0,0),-1)
        break
 
print(pix[0] + sliceWidth - last_col)

cv2.circle(img, (last_col, last_row), 1, (0, 255, 0), -1)
cv2.imshow("val", img)

height = max(rownonzero_pos)

mini_col=min(colnonzero_pos)
mini_row=min(rownonzero_pos)
print("min "+str(mini_col) + " " +str(mini_row))
#print("min "+str(width) + " " +str(height))

if(mini_row<0):mini_row=0
if(mini_col<0):mini_col=0
stt=time.time()
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(second_half)
#print(centroids)
nut_thread_row = np.array([], dtype=np.int)
nut_thread_col = np.array([], dtype=np.int)
cv2.imshow('otsu', binaryImage)
for i in range(centroids.shape[0]):
    if second_half[int(centroids[i][1]), int(centroids[i][0])] != 0:
        nut_thread_row = np.append(nut_thread_row, int(centroids[i][0]))
        nut_thread_col = np.append(nut_thread_col, int(centroids[i][1]))
dist = np.array([])
for i in range(nut_thread_row.shape[0]-1):
    dist = np.append(dist, math.sqrt((nut_thread_row[i] - nut_thread_row[i+1])**2 + (nut_thread_col[i] - nut_thread_col[i+1])**2))
print("nut thread")
print(nut_thread_row)
print(nut_thread_col)
print("here it is")
print(second_half[nut_thread_col, nut_thread_row])
print(np.median(dist))
print(time.time() - stt)
show_peak_valley(img[:, sliceWidth:], binaryImage, nut_thread_row, nut_thread_col)
cv2.waitKey(0)
cv2.destroyAllWindows()


