import core
import sys
import os
import csv
import locale


try:
    args = sys.argv
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8') 
    if len(args) != 6:
        raise Exception('Ungültige Paramter (Quellpfad, Zielpfad, UntererFaktorRot, UntererFaktorGrün, ObererFaktorGrün)')
    sourcePath = core.sanitizeAndCheckPath(args[1])
    targetPath = core.sanitizeAndCheckPath(args[2])
    lowerCh02Factor = core.sanitizeAndCheckFactor(args[3])
    lowerCh01Factor = core.sanitizeAndCheckFactor(args[4])
    upperCh01Factor = core.sanitizeAndCheckFactor(args[5])     
    findCh01Files = core.findCh01Files(sourcePath)
    csvPath = os.path.join(targetPath, 'results.csv')   
    if os.path.exists(csvPath):
        os.remove(csvPath)
    csvFile = open(csvPath, 'w', newline='', delimiter=';')
    writer = csv.writer(csvFile)
    writer.writerow(['sample', 'transfected is brighter', 'brightning_transfected', 'pixelcount_transfected', 'sumbrightness_transfected', 'brightning_untransfacted', 'pixelcount_untransfacted', 'sumbrightness_untransfacted'])
    for ch01FileName in findCh01Files:
        baseName = core.getFileBasename(ch01FileName)
        print(f"Verarbeite {baseName}...")
        ch02FileName = core.getMatchingCh02FileName(ch01FileName)
        ch01FilePath = os.path.join(sourcePath, ch01FileName)
        ch02FilePath = os.path.join(sourcePath, ch02FileName)
        ch01image = core.loadImage(ch01FilePath)
        ch02image = core.loadImage(ch02FilePath)
        ch02MeanBrightness = core.calculateMeanBrightness(ch02image)
        if lowerCh02Factor <= 0:
            minThreshold = 0
        else:
            minThreshold = lowerCh02Factor * ch02MeanBrightness[0]
        print(f"Unterer Threshold für das ch02 Bild: {minThreshold}")
        mask = core.generateMask(ch02image, minThreshold)
        maskFilePath = os.path.join(targetPath, f"{baseName}_mask.tif")
        core.saveImage(mask, maskFilePath)
        ch01MeanBrightness = core.calculateMeanBrightness(ch01image)
        ch01Foreground, ch01Background = core.maskExtract(ch01image, mask)
        core.saveImage(ch01Foreground, os.path.join(targetPath, f"{baseName}_transfected.tif"))
        core.saveImage(ch01Background, os.path.join(targetPath, f"{baseName}_untransfected.tif"))
        print(f"Unterer Threshold für das ch01 Bild: {ch01MeanBrightness[0] * lowerCh01Factor}")
        if lowerCh01Factor > 0:
            core.switchDarkPixel(ch01Foreground, ch01Background, ch01MeanBrightness[0] * lowerCh01Factor)
        core.saveImage(ch01Background, os.path.join(targetPath, f"{baseName}_untransfected_cleaned.tif"))
        if upperCh01Factor > 0:
            ch01Foreground = core.removeBrightPixel(ch01Foreground, ch01MeanBrightness[0] * upperCh01Factor)
            print(f"Oberer Threshold für das ch01 Bild: {ch01MeanBrightness[0] * lowerCh01Factor}")
        else:
            print(f"Oberer Threshold für das ch01 Bild: 0")
        core.saveImage(ch01Foreground, os.path.join(targetPath, f"{baseName}_transfected_cleaned.tif"))
        foregroundMeanBrightness = core.calculateMeanBrightness(ch01Foreground)
        backgroundMeanBrightness = core.calculateMeanBrightness(ch01Background)
        res = 0
        if foregroundMeanBrightness[0] > backgroundMeanBrightness[0]:
            res = 1
        writer.writerow([baseName, res, locale.format('%0.2f', foregroundMeanBrightness[0]), foregroundMeanBrightness[1], foregroundMeanBrightness[2], locale.format('%0.2f', backgroundMeanBrightness[0]), backgroundMeanBrightness[1], backgroundMeanBrightness[2]])
    print('Ausführung beendet.')
except Exception as ex:
    print('Ein Fehler ist aufgetreten:')
    print(ex)
    import traceback
    print(traceback.format_exc())
