import cv2
import imutils
from imutils import contours

from detector.util import *
import numpy as np
from detector.shape_type import ShapeType
from detector.diagram.shape import Shape
import detector.util as util

from detector.converter import *


class DiagramTypeDetector:
    CONVERTERS = [
        ClassDiagramConverter,
        UseCaseDiagramConverter
    ]

    @classmethod
    def find_converter(cls, shapes):
        """
        Returns the converter that can be used for the shapes.
        :return:
        """
        for converter in cls.CONVERTERS:
            if converter.is_diagram(shapes):
                return converter(shapes)