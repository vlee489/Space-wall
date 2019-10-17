"""
This file contains the main work for sort and cropping images
"""
import os
import traceback
from pyzbar import pyzbar
import cv2
import objects
import re
from PIL import Image
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import uuid
import threading
import atexit

# Settings
OUTPUTFOLDER = "output/"  # Picture output folder
INPUTFOLDER = "/Users/vlee489/Desktop/Space-wall/Image Input"  # Input folder
TEMP = "temp/"  # Used for temp holding
templates = "Templates/"  # Template folder
validID = [1836, 2018, 2171, 2173, 2645, 3001]  # Lists valid template IDs

# Variables
threads = list()
active = False


# Used for detecting when a file is added and then processing the file
class fileHandler(PatternMatchingEventHandler):
    patterns = ["*.png", "*.jpg", "*.JPEG"]

    def on_created(self, event):
        # If new image is found then we create a thread to process the image
        x = ImageProcessor(event.src_path)
        x.daemon = True
        threads.append(x)
        x.start()


# generates ID of image
def generateImageID(imageobject):
    try:
        id = uuid.uuid1()
        imageobject.addid(id.hex)
        return 1
    except Exception:  # TODO : This exception is far too broad
        print("==================")
        print("Unable to generate hash ID")
        print("file: " + imageobject.image)
        return 0


# Reads the QR code of image from imageObject and adds it to the template ID
def readQRCode(imageobject):
    #try:
    # Copied straight from https://stackoverflow.com/questions/50080949/qr-code-detection-from-pyzbar-with-camera-image
    QRImage = imageobject.image
    QRImage = cv2.imread(QRImage)
    mask = cv2.inRange(QRImage, (0, 0, 0), (200, 200, 200))
    thresholded = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    inverted = 255 - thresholded  # black-in-white
    barcode = pyzbar.decode(inverted)
    if not barcode:
        print("==================")
        print("Unable to find QR code")
        print("file: " + imageobject.image)
        return 0
    imageobject.addtemplateid(int(re.sub("[^0-9]", "", str(barcode[0].data))))
    return 1


# Crops the image depending on ID
def cutImage(imageobject):
    try:
        saveName = OUTPUTFOLDER + str(imageobject.templateID) + "/" + imageobject.ImageID + '.png'
        tempSave = TEMP + imageobject.ImageID + '.png'
        reference_image = imageobject.image
        mask_image = templates + str(imageobject.templateID) + ".png"
        reference_image = cv2.imread(reference_image)

        # Checks size of file and resize if needed
        if reference_image.shape != (2381, 3368, 3):
            reference_image = cv2.resize(reference_image, (3368, 2381), interpolation=cv2.INTER_LINEAR)

        mask_image = cv2.imread(mask_image)
        # applying the mask to original image
        masked_image = cv2.bitwise_or(reference_image, mask_image)
        # Shrink image for better use
        masked_image = cv2.resize(masked_image, (337, 238), interpolation=cv2.INTER_LINEAR)
        # The resultant image
        cv2.imwrite(tempSave, masked_image)

        img = Image.open(tempSave)
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
    except Exception:  # TODO : This exception is far too broad
        print("==================")
        print("Unable to crop image")
        print("file: " + imageobject.image)
        traceback.print_exc()
        return 0


# Cleans up temp files on closing
def cleanUP():
    print("Starting cleanup")
    count = 0
    for r, d, f in os.walk(TEMP):
        for file in f:
            os.remove(os.path.join(r, file))
            count = count + 1
    print("Number of files cleaned up: " + str(count))
    print("Clean up Finished")


# Starts the main process of processing images in its own thread
class ImageProcessor(threading.Thread):
    def __init__(self, imageLocation):
        super().__init__()
        self.location = imageLocation.replace("\\", "/")

    def run(self):
        time.sleep(1)
        proImg = objects.Image(self.location)
        if generateImageID(proImg) == 0:
            return
        if readQRCode(proImg) == 0:
            return
        if proImg.templateID in validID:
            if cutImage(proImg) == 0:
                return
        print("---------------")
        print("Processed Image")
        print("file: " + proImg.image)


# Runs the main program
atexit.register(cleanUP)  # BROKEN!
if __name__ == '__main__':
    if not active:
        active = True
        # Starts observers to see if files are added
        observer = Observer()
        observer.schedule(fileHandler(), path=INPUTFOLDER)
        observer.start()
        observer.join()
