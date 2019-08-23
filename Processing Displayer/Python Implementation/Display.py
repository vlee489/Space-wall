"""
Responsible for displaying images on screen
"""
import threading

import pygame
import random
import time
import os
from os.path import isfile, join
white = (255, 255, 255)

# Settings
# Resolution
validID = [2645]  # Lists valid template IDs
HEIGHT = 720
WIDTH = 930
FULLSCREEN = False
BACKGROUND = "images/background.png"
OBJECTS = "D:/Git/Space-wall/Python Loader/output/"
TEMPSTORAGE = "images/temp/"
FRAMERATE = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
drawings = []
threads = list()
toIgnore = []

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
        self.Hspeed = random.randint(1, 20)
        self.Vspeed = random.randint(-2, 2)
        self.direction = random.choice([True, False])
        if self.direction:
            self.HLocation = random.randint(50, WIDTH/2)
        else:
            self.HLocation = random.randint(WIDTH/2, WIDTH)
        self.VLocation = random.randint(100,HEIGHT-100)
        # ADD IMAGE ROTATION
        self.image = pygame.image.load(self.location)
        screen.blit(self.image, (self.HLocation, self.VLocation))

    def run(self):
        if self.HLocation > WIDTH or self.HLocation < -100:
            return True
        if self.VLocation > HEIGHT or self.VLocation < -100:
            return True
        self.VLocation = self.VLocation + self.Vspeed
        if self.direction:
            self.HLocation = self.HLocation + self.Hspeed
        else:
            self.HLocation = self.HLocation - self.Hspeed
        screen.blit(self.image, (self.HLocation, self.VLocation))
        return False


class ImageProcessor(threading.Thread):
    image = "NULL"
    ID = 0

    def __init__(self, image, ID):
        super().__init__()
        self.image = image
        self.ID = ID

    def run(self):
        time.sleep(5)
        os.rename(directory + self.image, TEMPSTORAGE + str(self.ID) + '/' + self.image)
        if self.ID == 2645:
            drawings.append(spaceship1(TEMPSTORAGE + '2645/' + self.image))
        toIgnore.remove(self.image)


drawings.append(spaceship1("D:/Git/Space-wall/ship 1.png"))
while True:
    for IDS in validID:
        directory = OBJECTS + str(IDS) + '/'
        files = [f for f in os.listdir(directory) if isfile(join(directory, f))]
        for i in files:
            if i not in toIgnore:
                toIgnore.append(i)
                x = ImageProcessor(i, IDS)
                x.daemon = True
                threads.append(x)
                x.start()
    screen.fill(white)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
    for items in drawings:
        if items.run():
            drawings.remove(items)
    pygame.display.update()
    pygame.time.wait(10)
