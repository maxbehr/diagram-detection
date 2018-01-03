import cv2
import imutils
from imutils import contours
from detector.util import *
import numpy as np
from detector.shape_type import ShapeType
from detector.diagram.shape import Shape
import detector.util as util


class ShapeDetector:
    def __init__(self, image):
        self.orig_image = None
        """ Reference to the original image. A working copy will be created from this image. """

        self.image = None
        """ Working copy of the original image. All image processing happens will be applied on this image. """

        self.preprocessed_image = None
        """ Preprocessed working copy image. """

        self.shapes = []
        """ Holds all found shapes. """

        self.contours = None
        self.hierarchy = None

        self._load(image)

        util.log("ShapeDetector initialized")

    def _load(self, image_path):
        log("ShapeDetector: load image '{image_path}' and create working copy")
        self.orig_image = cv2.imread(image_path)
        self.image = util.create_working_copy_of_image(self.orig_image)
        self.preprocessed_image = util.preprocess_image(self.image)

    def get_shapes(self):
        return self.shapes

    def find_shapes(self):
        """
        Looks for contours in the given image which are then transformed into Shapes. All found Shapes are then
        returned as an array.

        :return: Array with all found shapes
        """
        # Holds the area of all rects that were defined as class diagram rectangles
        area_rects = 0
        # img, contours, hierarchy = detect_contours(proc_image)
        im, cnts, hierarchy = detect_contours(self.preprocessed_image)

        #cons = cnts[0] if imutils.is_cv2() else cnts[1]
        # TODO: Why are we using cnts when creating the bounding rects instead of cons? No openCV version check needed?

        # TODO: Currently, we aren't sorting the contours anymore, but rather we are creating bounding rects for all contours.

        # Try creating bounding rect for all contours in order to then get all contours for which we could create
        # a bounding rect
        bounding_boxes = [cv2.boundingRect(c) for c in cnts]
        cons = [cnts[i] for i, v in enumerate(bounding_boxes)]

        #cons = contours.sort_contours(cnts, method="left-to-right")[0]

        found_shapes = []
        for (i, c) in enumerate(cons):
            log(f"c has children: {len(util.get_contour_children_for(i, hierarchy))}")

            shape = Shape(c)
            x, y, w, h = cv2.boundingRect(c)
            shape.set_image(self.image[y:y+h, x:x+w])
            found_shapes.append(shape)

        self.shapes = found_shapes
        self.contours = cons
        self.hierarchy = hierarchy

        return found_shapes

    def save_found_shapes(self):
        for k, shape in enumerate(self.shapes):
            shape.save_image(f"shape_{k}.png")

    def show_result(self):
        """
        Opens the image in a window.
        """
        cv2.namedWindow("ShapeDetector", cv2.WINDOW_AUTOSIZE)
        cv2.imshow("ShapeDetector", self.image)
        cv2.waitKey()
        cv2.destroyAllWindows()
