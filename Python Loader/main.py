"""
This file contains the main work for sort and cropping images
"""

import numpy as np
from pyzbar import pyzbar
import cv2
import objects
import re
from PIL import Image
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import hashlib
BLOCKSIZE = 65536
import threading
import os

validID = [2645, 6834]
outputFolder = "output/"
inputFolder = "D:/Git/Space-wall/Image Input"
templates = "Templates/"
threads = list()


# Used for detecting when a file is added and then processing the file
class fileHandler(PatternMatchingEventHandler):
    patterns = ["*.png", "*.jpg"]

    def process(self, event):
        print(event.src_path, event.event_type)

    def on_created(self, event):
        self.process(event)
        # If new image is found then we create a thread to process the image
        x = threading.Thread(target=processImage(event.src_path))
        threads.append(x)
        x.start()


# generates ID of image
def generateImageID(imageobject):
    """
    try:
        image = imageobject.image
        hasher = hashlib.md5()
        with open(image, 'rb') as afile:
            buf = afile.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(BLOCKSIZE)
        imageobject.addid(hasher.hexdigest())
        return 1
    except Exception:
        print("==================")
        print("Unable to generate hash ID")
        print("file: " + imageobject.image)
        return 0
    """
    image = imageobject.image
    hasher = hashlib.md5()
    with open(image, 'rb' ) as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    imageobject.addid(hasher.hexdigest())
    return 1


# Reads the QR code of image from imageObject and adds it to the template ID
def readQRCode(imageobject):
    try:
        QRImage = imageobject.image
        QRImage = cv2.imread(QRImage)
        mask = cv2.inRange(QRImage, (0, 0, 0), (200, 200, 200))
        threshold = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        inverted = 255 - threshold  # black-in-white
        barcode = pyzbar.decode(inverted)
        imageobject.addtemplateid(int(re.sub("[^0-9]", "", str(barcode[0].data))))
        return 1
    except Exception:
        print("==================")
        print("Unable to read QR Code")
        print("file: " + imageobject.image)
        return 0


def cutImage(imageobject):
    try:
        saveName = outputFolder + imageobject.ImageID + '.png'
        reference_image = imageobject.image
        mask_image = templates + str(imageobject.templateID) + ".png"
        reference_image = cv2.imread(reference_image)
        mask_image = cv2.imread(mask_image)
        # applying the mask to original image
        masked_image = cv2.bitwise_or(reference_image, mask_image)
        # The resultant image
        cv2.imwrite(saveName, masked_image)

        img = Image.open(saveName)
        img = img.convert("RGBA")
        datas = img.getdata()
        newData = []
        for item in datas:
            if item[0] == 255 and item[1] == 255 and item[2] == 255:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)
        img.putdata(newData)
        img.save(saveName, "PNG")
    except Exception:
        print("==================")
        print("Unable to crop image")
        print("file: " + imageobject.image)
        return 0


# Runs all the image recognition and processing
def processImage(imageLocation):
    location = imageLocation.replace("\\", "/")
    proImg = objects.Image(location)
    if generateImageID(proImg) == 0:
        return
    if readQRCode(proImg) == 0:
        return
    if proImg.ImageID in validID:
        if cutImage(proImg) == 0:
            return


if __name__ == '__main__':
    observer = Observer()
    observer.schedule(fileHandler(), path=inputFolder)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
