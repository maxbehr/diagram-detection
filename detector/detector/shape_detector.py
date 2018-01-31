from detector.util import *
import numpy as np
from detector.primitives.shape import Shape
import detector.util as util


class ShapeDetector:
    def __init__(self, image=None):
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

        if image is not None:
            self._load(image)

        util.log("ShapeDetector initialized")

    def _load(self, image_path):
        log(f"ShapeDetector: load image '{image_path}' and create working copy")
        self.orig_image = cv2.imread(image_path)
        self.load(self.orig_image)

    def load(self, image):
        self.image = util.create_working_copy_of_image(image)
        self.preprocessed_image = util.preprocess_image(self.image)

    def get_shapes(self):
        return self.shapes

    def find_shapes(self):
        found_shapes, cons, hierarchy = self.find_shapes_in_image(self.preprocessed_image)

        self.shapes = found_shapes
        self.contours = cons
        self.hierarchy = hierarchy

        log(f"{len(found_shapes)} shapes found")
        return found_shapes

    def find_shapes_in_image(self, image):
        """
        Looks for contours in the given image which are then transformed into Shapes. All found Shapes are then
        returned as an array.

        :return: Array with all found shapes
        """
        # Holds the area of all rects that were defined as class primitives rectangles
        area_rects = 0
        # img, contours, hierarchy = detect_contours(proc_image)
        im, cnts, hierarchy = detect_contours(image)

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
            shape = Shape(c)
            x, y, w, h = cv2.boundingRect(c)
            shape.set_image(self.image[y:y+h, x:x+w])
            shape.contour_index = i
            found_shapes.append(shape)

        return found_shapes, cons, hierarchy

    def label_contours(self):
        self.image = util.label_contours_in_image(self.contours, self.image)

    def find_lines_in_image_houghp(self, image, rho=1, theta=np.pi / 180, threshold=20, minLineLength=None, maxLineGap=None):
        img = image.copy()
        edges = cv2.Canny(img, 50, 200, apertureSize=3)
        lines = cv2.HoughLinesP(edges, rho, theta, threshold, minLineLength=minLineLength, maxLineGap=maxLineGap)

        return lines

    def find_lines_in_image_hough(self, image, rho=1, theta=np.pi / 180, threshold=20):
        img = image.copy()
        edges = cv2.Canny(img, 50, 150, apertureSize=3)

        minLineLength = None
        maxLineGap = None
        lines = cv2.HoughLines(edges, rho, theta, threshold)

        return lines

    def get_canny_edge_image(self, min=100, max=200):
        return util.create_canny_edge_image(self.image, min, max)

    def save_found_shapes(self):
        for k, shape in enumerate(self.shapes):
            shape.save_image(f"shape_{k}.png")

    def get_image_remove_contours(self, contours_to_be_removed):
        """
        Returns the pre-processed image with the given contours removed.
        :param contours_to_be_removed: The contours that should not be included in the image that is returned.
        :return: Image without the shapes of the given contours removed.
        """
        image = self.preprocessed_image.copy()

        erosion_factor = 5
        for c in contours_to_be_removed:
            (x, y, w, h) = cv2.boundingRect(c)
            util.print_contour_details(c)

            cv2.rectangle(image, (x-erosion_factor, y-erosion_factor), (x+w+erosion_factor, y+h+erosion_factor), (0, 0, 0), -1)

        return image

    def get_shapes_by_type(self, shape_type):
        """
        Filters the found shapes by the given shape type.
        :param shape_type: Shape type the found shapes are filtered by.
        :return: An array that contains the filtered shapes.
        """
        shapes = [s for s in self.shapes if s.shape == shape_type]
        shapes_contours = [s.contour for s in shapes]

        return shapes, shapes_contours

    def get_image_remove_shape_type(self, shape_type):
        """
        Removes the given shape type from the image.
        :param shape_type:
        :return: image that has the given shape type removed
        """
        shapes, shapes_contours = self.get_shapes_by_type(shape_type)
        return self.get_image_remove_contours(shapes_contours)

    def get_image_filter_shape_type(self, shape_type):
        """
        Isolates the given shape type from the image and returns an image that only contains shapes from the given
        shape type.
        :param shape_type:
        :return: image that contains only shape types of the given shape type
        """
        img = self.get_image_remove_shape_type(shape_type)
        _, contours_remove, _ = self.find_shapes_in_image(img)
        return self.get_image_remove_contours(contours_remove)

    def sort_contours_by_parent(self):
        return util.get_sorted_contours_by_parent(self.contours, self.hierarchy)

    def show_result(self):
        """
        Opens the image in a window.
        """
        cv2.namedWindow("ShapeDetector", cv2.WINDOW_AUTOSIZE)
        cv2.imshow("ShapeDetector", self.image)
        cv2.waitKey()
        cv2.destroyAllWindows()
