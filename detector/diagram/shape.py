import cv2
import detector.util as util


class Shape:
    def __init__(self, contour):
        self.type = None
        self.contour = contour
        self.shape = util.detect_shape(contour)

        (x, y, w, h) = cv2.boundingRect(self.contour)
        self.w = w
        self.h = h
        self.x = x
        self.y = y

    def area(self):
        """
        Returns the area of thisthis contour.
        :return:
        """
        return util.area_contour(self.contour)

    def bounding_rect(self):
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

    def print_info(self):
        """
        Prints some information, such as shape type, amount of sides, ratio, etc. to the console.
        :return:
        """
        util.print_contour_details(self.contour)