import cv2
import time
import numpy as np
import math
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

def show_peak_valley(img, bina, v):
    #cv2.circle(img, (250, 250), 50, (100, 50, 200), -1)
    for i in range(v.shape[0]):
        #if(bina[int(v[i][1]),int(v[i][0])] !=0):
        cv2.circle(img, (int(v[i][0]), int(v[i][1])), 1, (0, 255, 0), -1)

    cv2.imshow("valleysssss", img)


img = cv2.imread('/home/theabysswalker/Documents/Dimensional-Accuracy-Assertion/nut2.jpg')

#img = img[400:600, 500:1800]

redChannel = img[:, 360 :, 2]

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
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binaryImage)
print(centroids)
nut_thread_row = np.array([])
nut_thread_col = np.array([])
cv2.imshow('otsu', binaryImage)
for i in range(centroids.shape[0]):
    if binaryImage[int(centroids[i][1]), int(centroids[i][0])] != 0:
        nut_thread_row = np.append(nut_thread_row, int(centroids[i][0]))
        nut_thread_col = np.append(nut_thread_col, int(centroids[i][1]))
sol = 0
for i in range(nut_thread_row.shape[0]-1):
    sol = sol + math.sqrt((nut_thread_row[i] - nut_thread_row[i+1])**2 + (nut_thread_col[i] - nut_thread_col[i+1])**2)
print(nut_thread_row)
print(nut_thread_col)
print(sol/(nut_thread_row.shape[0]-1))
print(time.time() - stt)
show_peak_valley(img[:,360:,:], binaryImage, centroids)
cv2.waitKey(0)
cv2.destroyAllWindows()

