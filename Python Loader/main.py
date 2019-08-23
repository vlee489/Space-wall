"""
This file contains the main work for sort and cropping images
"""
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

# Settings
OUTPUTFOLDER = "output/"  # Picture output folder
INPUTFOLDER = "D:/Git/Space-wall/Image Input"  # Input folder
templates = "Templates/"  # Template folder
validID = [2645, 6834]  # Lists valid template IDs

# Variables
threads = list()
active = False


# Used for detecting when a file is added and then processing the file
class fileHandler(PatternMatchingEventHandler):
    patterns = ["*.png", "*.jpg"]

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
    except Exception:
        print("==================")
        print("Unable to generate hash ID")
        print("file: " + imageobject.image)
        return 0


# Reads the QR code of image from imageObject and adds it to the template ID
def readQRCode(imageobject):
    try:
        QRImage = imageobject.image
        QRImage = cv2.imread(QRImage)
        barcode = pyzbar.decode(QRImage)
        imageobject.addtemplateid(int(re.sub("[^0-9]", "", str(barcode[0].data))))
        return 1
    except Exception:
        print("==================")
        print("Unable to scan QR code")
        print("file: " + imageobject.image)
        return 0


def cutImage(imageobject):
    try:
        saveName = OUTPUTFOLDER + str(imageobject.templateID) + "/" + imageobject.ImageID + '.png'
        tempSave = "temp/" + imageobject.ImageID + '.png'
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
    except Exception:
        print("==================")
        print("Unable to crop image")
        print("file: " + imageobject.image)
        traceback.print_exc()
        return 0


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


if __name__ == '__main__':
    if not active:
        active = True
        # Starts observers to see if files are added
        observer = Observer()
        observer.schedule(fileHandler(), path=INPUTFOLDER)
        observer.start()
        observer.join()
