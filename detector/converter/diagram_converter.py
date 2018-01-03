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

    def __init__(self, shapes):
        self.shapes = shapes

    def transform_shapes_to_diagram(self):
        raise NotImplementedError()
