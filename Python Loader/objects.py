"""
This file contains all the object designs for the items in the program
"""


class Image:
    ImageID = "1000"
    image = "blank"
    templateID = 9999

    def __init__(self, image):
        self.image = image

    def addid(self, imageid):
        self.ImageID = imageid

    def addtemplateid(self, templateid):
        self.templateID = templateid
