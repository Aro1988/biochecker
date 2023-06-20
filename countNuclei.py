import os
import cv2
import numpy as np
from scipy import ndimage
from skimage.feature import peak_local_max
from skimage.segmentation import watershed
import imutils
import csv
import shutil

rootPath = os.getcwd() # Hier den Root-Pfad einfügen

src = os.path.join(rootPath, 'source')
outPath = os.path.join(rootPath, 'count')

if os.path.exists(outPath):
    shutil.rmtree(outPath)
if not os.path.exists(outPath):
    os.mkdir(outPath)

csvFile = os.path.join(rootPath, 'count', 'count.csv')
csvFile = open(csvFile, 'a', newline='')

writer = csv.writer(csvFile)
writer.writerow(['file', 'count'])

folder = os.listdir(src)

for fname in folder:

    if 'ch00' not in fname:
        continue

    p = os.path.join(src, fname)
    name = fname.split('_')
    del name[-1]
    name = '_'.join(name)

    img = cv2.imread(p)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    border_size = 5
    gray = cv2.copyMakeBorder(gray, border_size, border_size, border_size, border_size, cv2.BORDER_CONSTANT, value=0)

    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=1)

    contours, hierarchy = cv2.findContours(closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Loop over all the contours and add count number
    count = 1
    for i, c in enumerate(contours):

        area = cv2.contourArea(c)
        x,y,w,h = cv2.boundingRect(c)
        #cv2.rectangle(img,(x,y),(x+w,y+h),(100,100,0),2)

        if (area < 100 or area > 4000):
            continue

        cv2.drawContours(img, [c], -1, (0, 255, 0), 2)

        # Calculate the centroid of the contour
        M = cv2.moments(c)
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

        # Draw the count number at the centroid location
        cv2.putText(img, str(count), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        count = count + 1
    
    name = name+'_ch00_count.tif'
    writer.writerow([name, count])
    op = os.path.join(outPath, name)
    cv2.imwrite(op, img)
print('completed')
