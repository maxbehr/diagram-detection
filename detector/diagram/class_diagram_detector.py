import cv2
import imutils
from imutils import contours
from detector.util import *
import numpy as np
from detector.shape_type import ShapeType
import detector.util as util


class ClassDiagramDetector:
    def __init__(self):
        self.image = None
        """ The image this detector was applied to """

        self.shape_hierarchy = None
        """ Holds the shape hierarchy of the image this class diagram detector was applied to """

        self.cnts = None
        """ Holds all contours of the image this class diagram detector was applied to """

        log("ClassDiagramDetector initialized")

    def detect(self, image):
        self.shape_hierarchy, self.cnts = util.create_shape_hierarchy(image)
        for k, v in self.shape_hierarchy.items():
            util.log(f"contour {k} has {len(v)} children")


    def get_class_shape_contours(self, image):
        shape_hierarchy, cnts = util.create_shape_hierarchy(image)
        #img, cnts, hierarchy = detect_contours(image)

        # for k, v in shape_hierarchy.items():
        #filtered = filter(lambda x: len(x) == 3, shape_hierarchy.values())
        all_class_shape_contours = []
        for k, v in shape_hierarchy.items():
            all_class_shape_contours.append(cnts)

            #all_class_shape_contours += cnts[k]

        return cnts



