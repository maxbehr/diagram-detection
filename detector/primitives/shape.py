import detector.util as util
from detector.util import *
import os
from detector.primitives.shape_type import ShapeType


class Shape:
    def __init__(self, contour):
        self.image = None
        self.contour = contour
        self.contour_index = -1
        """ Defines the contour index in the hierarchy list """

        self.shape = util.detect_shape(contour)
        self.text = None

        (x, y, w, h) = self.bounding_box()
        self.w = w
        self.h = h
        self.x = x
        self.y = y

    def ocr(self):
        filename = f"{self.shape_name()}_{util.random_str()}.png"
        self.save_image(f"{filename}")
        self.text = util.ocr(f"{filename}")

    def save_image(self, filename):
        """
        Saves the shape to disk.
        :param filename: Name of the saved file.
        :return:
        """
        output_filename = f"{filename}"
        util.save_image(self.image, output_filename)

    def remove_image(self):
        """
        Removes the saved image.
        :return:
        """
        os.remove(self.output_filename)

    def set_image(self, image):
        self.image = image

    def area(self):
        """
        Returns the area of thisthis contour.
        :return:
        """
        return util.area_contour(self.contour)

    def bounding_box(self):
        """
        Returns the bounding rectangle of this contour.
        :return: Returns a touple in the form of (x, y, w, h)
        """
        return cv2.boundingRect(self.contour)

    def moments(self):
        """
        Returns the moments array of this contour.
        :return:
        """
        return cv2.moments(self.contour)

    def shape_name(self):
        return ShapeType.to_s(self.shape)

    def print_info(self):
        """
        Prints some information, such as shape type, amount of sides, ratio, etc. to the console.
        :return:
        """
        return util.print_contour_details(self.contour)


    def __str__(self):
        return util.get_contour_details(self.contour)
