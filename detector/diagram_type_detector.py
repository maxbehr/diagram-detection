import cv2
import imutils
from imutils import contours
from detector.util import *
import numpy as np
from detector.shape_type import ShapeType
from detector.diagram.shape import Shape
import detector.util as util
from detector.diagram.class_diagram_converter import ClassDiagramConverter


class DiagramTypeDetector:
    CONVERTERS = [ClassDiagramConverter]

    def __init__(self, shapes):
        self.shapes = shapes
        self.suggested_converter = None

        util.log("DiagramTypeDetector initialized")

    def _is_diagram_rect(self, c):
        x, y, w, h = cv2.boundingRect(c)
        ratio = aspect_ratio(c)
        area = w * h

        return detect_shape(c) == ShapeType.RECTANGLE #and h > w and area > 200 #and ratio < 1

    def analyze_shapes(self):
        """

        :return:
        """
        log("DiagramShapeDetector: analyze shapes and and set suggested converter")
        self.suggested_converter = "class_diagram"

    def get_converter(self):
        """
        Returns the converter that can be used for the shapes.
        :return:
        """
        for converter in self.CONVERTERS:
            if self._check_converter(converter):
                return converter(self.shapes)

    def _check_converter(self, converter):
        """
        Checks the given converter against the suggested converter. Returns true, when both are equal. Returns false
        otherwise.
        :param converter: Converter we want to check the suggested converter against.
        :return: true if the suggested converter matches the given one, false otherwise.
        """
        return self.suggested_converter == converter.CONVERTER_TYPE
