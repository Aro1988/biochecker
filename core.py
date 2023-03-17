import cv2
import os
import numpy as np
import math
import csv

def generateMask(image, minBrightness):  
    grayedImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    threshold = cv2.threshold(grayedImage, minBrightness, 255, cv2.THRESH_BINARY)[1]
    kernel = np.ones((2,2), np.uint8)
    morphOpen = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)
    return morphOpen

def maskExtract(image, mask):
    extractedImages = []
    invertedMask = cv2.bitwise_not(mask)
    extractedImages.append(cv2.bitwise_and(image, image, mask=mask))
    extractedImages.append(cv2.bitwise_and(image, image, mask=invertedMask))
    return extractedImages

def calculateBrightness(pixel):
    return math.sqrt(0.299 * math.pow(pixel[0], 2) + 0.587 * math.pow(pixel[1], 2) + 0.114 * math.pow(pixel[2], 2))

def calculateMeanBrightness(image):
    height, width, channels = image.shape
    pixelCount = 0
    brightnessSum = 0
    for y in range(height):
        for x in range(width):
            pixel = image[y,x]
            if pixel[0] == 0 and pixel[1] == 0 and pixel[2] == 0:
                continue
            brightness = calculateBrightness(pixel)
            brightnessSum += brightness
            pixelCount += 1
    divison = 0
    if pixelCount > 0:
        divison = brightnessSum/pixelCount
    return [divison, brightnessSum, pixelCount]

def removeBrightPixel(image, minBrightness):
    height, width, channels = image.shape
    for y in range(height):
        for x in range(width):
            pixel = image[y,x]
            if pixel[0] == 0 and pixel[1] == 0 and pixel[2] == 0:
                continue
            brightness = calculateBrightness(pixel)
            if brightness >= minBrightness:
                image[y,x] = np.array([0,0,0])
    return image

def switchDarkPixel(foregroundImage, backgroundImage, maxBrightness):  
    height, width, channels = foregroundImage.shape
    for y in range(height):
        for x in range(width):
            pixel = foregroundImage[y,x]
            brightness = calculateBrightness(pixel)
            if brightness <= maxBrightness:
                backgroundImage[y, x] = pixel
                foregroundImage[y, x] = [0, 0, 0]

def loadImage(imagePath):
    if not os.path.exists:
        raise Exception(f"Bild {imagePath} existiert nicht.")
    image = cv2.imread(imagePath)
    return image

def sanitizeAndCheckPath(path):
    path = os.path.normpath(path)
    if not os.path.exists(path):
        raise Exception(f"Der Pfad {path} wurde nicht gefunden.")
    return path

def sanitizeAndCheckFactor(factor):
    try:
        factor = float(factor)
        return factor
    except ValueError:
        raise Exception(f"Das Argument {factor} ist keine Kommazahl.")

def findCh01Files(path):
    files = []
    fileList = os.listdir(path)
    for fileName in fileList:
        if 'ch01' not in fileName:
            continue
        else:
            files.append(fileName)
    return files

def getFileBasename(fileName):
    name = fileName.split('_')
    del name[-1]
    name = '_'.join(name)
    return name

def getMatchingCh02FileName(ch01File):
    baseName = getFileBasename(ch01File)
    ch02name = baseName + '_ch02.tif'
    return ch02name

def saveImage(image, filePath):
    cv2.imwrite(filePath, image)

def getCsv(csvPath):
    if os.path.exists(csvPath):
        os.remove(csvPath)
    csvFile = open(csvPath, 'w', newline='')
    return csv.writer(csvFile, delimiter=';')