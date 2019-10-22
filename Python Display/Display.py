"""
Responsible for displaying images on screen
"""
import errno
import threading
import cv2
import pygame
import random
import time
import os
from os.path import isfile, join

white = (255, 255, 255)

# Settings
# Resolution
validIDs = [1836, 2018, 2171, 1273, 2645, 3001]  # Lists valid template IDs
HEIGHT = 720  # 720
WIDTH = 1280  # 930
FULLSCREEN = False
BACKGROUND = "images/background.jpg"
OBJECTS = "D:/Git/Space-wall/Python Loader/output/"  # Point to the output folder of the python Loader
TEMPSTORAGE = "images/temp/"
FRAMERATE = 15

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
drawings = []
threads = list()
toIgnore = []
toRemove = []
clock = pygame.time.get_ticks()


class spaceship1:
    location = "NONE"
    flame = False
    shrink = False
    Hspeed = 20
    Vspeed = 0
    HLocation = 100
    VLocation = 100
    direction = True
    image = None

    def __init__(self, imageLocation):
        self.location = imageLocation
        self.Hspeed = random.randint(1, 10)
        self.Vspeed = random.randint(-2, 2)
        self.direction = random.choice([True, False])
        if self.direction:
            self.HLocation = random.randint(1, int(WIDTH / 8))
        else:
            self.HLocation = random.randint(WIDTH - int(WIDTH / 8), WIDTH)
            self.img = cv2.imread(imageLocation, cv2.IMREAD_UNCHANGED)
            (self.h, self.w) = self.img.shape[:2]
            self.center = (self.w / 2, self.h / 2)
            self.M = cv2.getRotationMatrix2D(self.center, 180, 1.0)
            self.rotated180 = cv2.warpAffine(self.img, self.M, (self.w, self.h))
            cv2.imwrite(self.location, self.rotated180)
        self.VLocation = random.randint(int(HEIGHT / 2) - 100, int(HEIGHT / 2) + 100)
        # ADD IMAGE ROTATION
        self.image = pygame.image.load(self.location)
        self.image = pygame.transform.rotate(self.image, self.Vspeed * 3)

    def run(self):
        if self.HLocation > WIDTH + 400 or self.HLocation < -500:
            drawings.remove(self)
            return True
        if self.VLocation > HEIGHT + 400 or self.VLocation < -500:
            drawings.remove(self)
            return True

        self.VLocation = self.VLocation + self.Vspeed
        if self.direction:
            self.HLocation = self.HLocation + self.Hspeed
        else:
            self.HLocation = self.HLocation - self.Hspeed


class ufo:
    location = "NONE"
    Hspeed = 20
    HLocation = 100
    VLocation = 100
    direction = True
    image = None

    def __init__(self, imageLocation):
        self.location = imageLocation
        self.Hspeed = random.randint(1, 10)
        self.direction = random.choice([True, False])
        if self.direction:
            self.HLocation = random.randint(1, int(WIDTH / 8))
        else:
            self.HLocation = random.randint(WIDTH - int(WIDTH / 8), WIDTH)
        self.VLocation = random.randint(int(HEIGHT / 2) - 100, int(HEIGHT / 2) + 100)
        # ADD IMAGE ROTATION
        self.image = pygame.image.load(self.location)

    def run(self):
        if self.HLocation > WIDTH + 400 or self.HLocation < -500:
            drawings.remove(self)
            return True

        if self.direction:
            self.HLocation = self.HLocation + self.Hspeed
        else:
            self.HLocation = self.HLocation - self.Hspeed


class star:
    flicker = 10
    HLocation = 100
    VLocation = 100
    location = "NONE"
    image = None
    imageTime = 100

    def __init__(self, imageLocation):
        self.location = imageLocation
        self.HLocation = random.randint(30, WIDTH-30)
        self.VLocation = random.randint(int(HEIGHT / 2), int(HEIGHT / 2) + 100)
        self.flicker = random.randint(1, 5)
        self.image = pygame.image.load(self.location)
        self.img = cv2.imread(imageLocation, cv2.IMREAD_UNCHANGED)
        (self.h, self.w) = self.img.shape[:2]
        self.imageTime = random.randint(30000, 50000)
        self.imageTime = self.imageTime + clock
        self.image = pygame.image.load(self.location)
        print(self.VLocation)

    def run(self):
        if clock > self.imageTime:
            drawings.remove(self)
            return True


class alien:
    HLocation = 100
    VLocation = 100
    location = "NONE"
    image = None
    Hspeed = 20
    Vspeed = 0
    direction = True

    def __init__(self, imageLocation):
        self.location = imageLocation
        self.Hspeed = random.randint(1, 5)
        self.Vspeed = random.randint(-1, 1)
        self.direction = random.choice([True, False])
        if self.direction:
            self.HLocation = random.randint(1, int(WIDTH / 8))
        else:
            self.HLocation = random.randint(WIDTH - int(WIDTH / 8), WIDTH)
        self.VLocation = random.randint(int(HEIGHT / 2) - 100, int(HEIGHT / 2) + 100)
        # ADD IMAGE ROTATION
        self.image = pygame.image.load(self.location)
        self.image = pygame.transform.rotate(self.image, self.Vspeed * 3)

    def run(self):
        if self.HLocation > WIDTH + 400 or self.HLocation < -500:
            drawings.remove(self)
            return True
        if self.VLocation > HEIGHT + 400 or self.VLocation < -500:
            drawings.remove(self)
            return True

        self.VLocation = self.VLocation + self.Vspeed
        if self.direction:
            self.HLocation = self.HLocation + self.Hspeed
        else:
            self.HLocation = self.HLocation - self.Hspeed


class spaceman:
    HLocation = 100
    VLocation = 100
    location = "NONE"
    image = None
    Hspeed = 20
    Vspeed = 0

    def __init__(self, imageLocation):
        self.location = imageLocation
        self.Hspeed = random.randint(1, 5)
        self.Vspeed = random.randint(-1, 1)
        self.HLocation = random.randint(1, int(WIDTH / 8))
        self.VLocation = random.randint(int(HEIGHT / 2) - 100, int(HEIGHT / 2) + 100)
        self.image = pygame.image.load(self.location)

    def run(self):
        if self.HLocation > WIDTH + 400 or self.HLocation < -500:
            drawings.remove(self)
            return True

        self.VLocation = self.VLocation + self.Vspeed
        self.HLocation = self.HLocation + self.Hspeed


class ShootingStar:
    HLocation = 100
    VLocation = 100
    location = "NONE"
    image = None
    Hspeed = 20
    Vspeed = 0

    def __init__(self, imageLocation):
        self.location = imageLocation
        self.Hspeed = random.randint(1, 10)
        self.Vspeed = random.randint(-3, 3)
        self.direction = random.choice([True, False])
        self.HLocation = random.randint(1, int(WIDTH / 8))
        self.VLocation = random.randint(int(HEIGHT / 2) - 300, int(HEIGHT / 2) + 200)
        # ADD IMAGE ROTATION
        self.image = pygame.image.load(self.location)
        self.image = pygame.transform.rotate(self.image, self.Vspeed * 3)

    def run(self):
        if self.HLocation > WIDTH + 400 or self.HLocation < -500:
            drawings.remove(self)
            return True
        if self.VLocation > HEIGHT + 400 or self.VLocation < -500:
            drawings.remove(self)
            return True

        self.VLocation = self.VLocation + self.Vspeed
        self.HLocation = self.HLocation + self.Hspeed

# Deletes all files in temp holding location
def cleanUP():
    print("Starting cleanup")
    count = 0
    for r, d, f in os.walk(TEMPSTORAGE):
        for file in f:
            os.remove(os.path.join(r, file))
            count = count + 1
    print("Number of files cleaned up: " + str(count))
    print("Clean up Finished")


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


Background_object = Background(BACKGROUND, [0, 0])


# Processes images
class ImageProcessor(threading.Thread):
    image = "NULL"
    ID = 0

    def __init__(self, image, ID, image_directory, available_drawings):
        super().__init__()
        self.image = image
        self.ID = ID
        self.image_directory = image_directory
        self.available_drawings = available_drawings

    def run(self):
        time.sleep(2)
        os.rename(self.image_directory + self.image, TEMPSTORAGE + str(self.ID) + '/' + self.image)
        if self.ID == 2645:
            self.available_drawings.append(spaceship1(TEMPSTORAGE + '2645/' + self.image))
        if self.ID == 2171:
            self.available_drawings.append(spaceman(TEMPSTORAGE + '2171/' + self.image))
        if self.ID == 3001:
            self.available_drawings.append(alien(TEMPSTORAGE + '3001/' + self.image))
        if self.ID == 1836:
            self.available_drawings.append(star(TEMPSTORAGE + '1836/' + self.image))
        if self.ID == 1273:
            self.available_drawings.append(ShootingStar(TEMPSTORAGE + '1273/' + self.image))
        if self.ID == 2018:
            self.available_drawings.append(ufo(TEMPSTORAGE + '2018/' + self.image))
        toIgnore.remove(self.image)


def create_folder(dir_path):
    try:
        os.makedirs(dir_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def setup():
    for validID in validIDs:
        create_folder(f"{TEMPSTORAGE}{validID}")


setup()
clock_1 = pygame.time.Clock()
cleanUP()
while True:
    clock = pygame.time.get_ticks()
    ticks = pygame.time.get_ticks()
    clock_1.tick(FRAMERATE)
    drawings_blits = []
    blit_list = [(Background_object.image, Background_object.rect)]
    for IDS in validIDs:
        directory = OBJECTS + str(IDS) + '/'
        files = [f for f in os.listdir(directory) if isfile(join(directory, f)) and f.split(".")[1] in ["jpg", "png"]]
        for i in files:
            if i not in toIgnore:
                toIgnore.append(i)
                x = ImageProcessor(i, IDS, directory, drawings)
                x.daemon = True
                threads.append(x)
                x.start()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cleanUP()
            pygame.quit()
            quit()
    for items in drawings:
        items.run()
        blitLocation = (items.image, (items.HLocation, items.VLocation))
        blit_list.append(blitLocation)
    screen.blits(blit_list)
    pygame.display.update()

