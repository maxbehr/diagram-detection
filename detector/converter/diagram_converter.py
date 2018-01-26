import cv2
import imutils
from imutils import contours
from detector.util import *
import numpy as np
from detector.diagram.shape import Shape
from detector.shape_type import ShapeType
import detector.util as util


class DiagramConverter(object):
    CONVERTER_TYPE = None

    def __init__(self, shape_detector):
        self.shape_detector = shape_detector
        """ Shape detector, that contains all detected shapes, the contours and the contour hierarchy. """
        self.generic_entities = []

    def transform_shapes_to_diagram(self):
        raise NotImplementedError()

    @classmethod
    def is_diagram():
        raise NotImplementedError()

    def get_generic_entities(self):
        return self.generic_entities
