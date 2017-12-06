import cv2
import imutils
from imutils import contours
from detector.util import *
import numpy as np
from detector.shape import Shape

class UseCaseDetector:
    def __init__(self):
        self.image = None
        print("UseCaseDetector initialized")

    def detect(self):
        print("use case detection")