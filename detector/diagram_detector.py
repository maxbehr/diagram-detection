import cv2
import imutils
from imutils import contours
from detector.util import *
import numpy as np
from detector.shape_type import ShapeType
from detector.diagram.shape import Shape
import detector.util as util
from detector.diagram.class_diagram_detector import ClassDiagramDetector

class DiagramDetector:
    def __init__(self):
        self.orig_image = None
        self.image = None
        self.preprocessed_gray = None
        self.shapes = []
        print("DiagramDetector initialized")

    def _is_diagram_rect(self, c):
        x, y, w, h = cv2.boundingRect(c)
        ratio = aspect_ratio(c)
        area = w * h

        return detect_shape(c) == ShapeType.RECTANGLE #and h > w and area > 200 #and ratio < 1

    def _preprocess(self, image):
        # Blur image
        image = cv2.GaussianBlur(image, (5,5), 0)

        # Grayscale image
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.imshow("gray", image)

        # Threshold image
        _, image = cv2.threshold(image, 135, 255, cv2.THRESH_BINARY_INV)
        #image = cv2.dilate(image, (15, 15), iterations=3)
        cv2.imshow("thresh", image)

        return image

    def _get_working_copy(self, image):
        return imutils.resize(image, width=700)

    def load(self, image_path):
        self.orig_image = cv2.imread(image_path)
        self.image = self._get_working_copy(self.orig_image)

    def get_shapes(self):
        return self.shapes

    def find_shapes(self, image):
        """
        Looks for contours in the given image which are then transformed into Shapes. All found Shapes are then
        returned as an array.

        :return: Array with all found shapes
        """
        # Holds the area of all rects that were defined as class diagram rectangles
        area_rects = 0
        # img, contours, hierarchy = detect_contours(proc_image)
        im, cnts, hierarchy = detect_contours(image)
        cons = cnts[0] if imutils.is_cv2() else cnts[1]
        cons = contours.sort_contours(cnts, method="left-to-right")[0]

        found_shapes = []
        for (i, c) in enumerate(cons):
            shape = Shape(c)
            x, y, w, h = cv2.boundingRect(c)
            shape.set_image(image[y:y+h, x:x+w])
            found_shapes.append(shape)

        return found_shapes

    def find_class_diagram_shape(self, image):
        im, cnts, hierarchy = detect_contours(image)
        contour_map = {}
        for h in hierarchy[0]:
            parent_id = h[3]

            if parent_id in contour_map:
                contour_map[parent_id].append(h)
            else:
                contour_arr = []
                contour_arr.append(h)
                contour_map[parent_id] = contour_arr

        return contour_map

    def get_analyzed_image(self):
        area_rects = 0
        for (i, shape) in enumerate(self.shapes):
            if shape.shape is not ShapeType.UNIDENTIFIED:
                shape.print_info()

                area_rects += shape.area()

                cv2.drawContours(self.image, [shape.contour], 0, (0, 255, 0), 2)

                #M = shape.moments()
                #cX = int((M["m10"] / M["m00"]))
                #cY = int((M["m01"] / M["m00"]))
                #cv2.putText(self.image, shape.shape_name(), (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        # Calculate percentage of rectangle area in image
        image_height, image_width = image_area(self.image)
        area_rects_percentage = round(area_rects / (image_width * image_height) * 100, 4)
        print("Found rects: {amount}, area: {area} ({perc}%)".format(amount=len(self.shapes), area=area_rects, perc=area_rects_percentage))

        return self.image

    def analyze(self):
        # Preprocess the image
        proc_image = self._preprocess(self.image)
        #self.shapes = self.find_shapes(proc_image)

        cdd = ClassDiagramDetector()
        cdd.detect(proc_image)
        class_shape_contours = cdd.get_class_shape_contours(proc_image)
        util.draw_contours_on_image(class_shape_contours, self.image)

        #for x in self.find_class_diagram_shape(proc_image):
        #    print(x)

        return self.shapes, self.get_analyzed_image()

    def is_class_diagram(self):
        """
        Identifies an image either as class diagram or not.

        :param image_path: Path of the image
        :return: true if the image was detected as UML class diagram, false otherwise.
        """

        # Preprocess the image
        im = self.image
        print_image_details(im)
        proc_image = self._preprocess(self.image)

        # Calc the ratio of the image
        #ratio = self.orig_image.shape[0] / float(self.image.shape[0])

        # Use canny edge detection on resized image
        #canny = cv2.Canny(self.image, 100, 100)
        #canny = cv2.dilate(canny, (3,3), iterations=5)
        # cv2.imshow("canny", canny)

        # Holds the area of all rects that were defined as class diagram rectangles
        area_rects = 0
        # img, contours, hierarchy = detect_contours(proc_image)
        cnts = detect_contours(proc_image)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        cnts = contours.sort_contours(cnts, method="left-to-right")[0]
        #cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:2]

        bounding_boxes = {}
        found_shapes = []
        found_diagram_rects = []
        for (i, c) in enumerate(cnts):
            shape = Shape(c)
            found_shapes.append(shape);
            shape.print_info()

            (x, y, w, h) = shape.bounding_rect()
            # roi = proc_image[y:y + h, x:x + w]
            # bounding_boxes[i] = roi

            area_rects += shape.area()

            cv2.drawContours(self.image, [c], -1, (0, 255, 0), 2)

            M = shape.moments()
            cX = int((M["m10"] / M["m00"]))
            cY = int((M["m01"] / M["m00"]))
            cv2.putText(self.image, shape.shape_name(), (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 0, 0), 1)

            #cv2.rectangle(self.image, (x, y), (x + w, y + h), (0, 255, 0), -1)

            # if self._is_diagram_rect(c):
            #     print_contour_details(c)
            #
            #     found_diagram_rects.append(c)
            #     area_rects += area_contour(c)
            #
            #     # shape = self.detect_shape(c)
            #     # M = cv2.moments(c)
            #     # cX = int((M["m10"] / M["m00"]) * ratio)
            #     # cY = int((M["m01"] / M["m00"]) * ratio)
            #
            #     # c = c.astype("float")
            #     # c *= ratio
            #     # c = c.astype("int")
            #     cv2.drawContours(self.image, [c], -1, (0, 255, 0), 2)
            #
            #     (x, y, w, h) = cv2.boundingRect(c)
            #     font = cv2.FONT_HERSHEY_SIMPLEX
            #     #cv2.putText(self.image, str(i), (int(x/2), int(y/2)), font, 1, (0, 0, 0), 2, cv2.LINE_AA)
            #     #cv2.rectangle(self.image, (x, y), (x + w, y + h), (0, 255, 0), -1)


        # Calculate percentage of rectangle area in image
        image_height, image_width = image_area(self.image)
        area_rects_percentage = round(area_rects / (image_width * image_height) * 100, 4)
        print("Found rects: {amount}, area: {area} ({perc}%)".format(amount=len(found_diagram_rects), area=area_rects, perc=area_rects_percentage))

    def show_result(self):
        """
        Opens the image in a window.
        """
        util.crop_shapes_and_save_as_files(self.image, self.shapes)

        cv2.namedWindow("Image", cv2.WINDOW_AUTOSIZE)

        #cv2.createTrackbar('Epsilon', 'Image', 0, 100, self.is_class_diagram)

        cv2.imshow("Image", self.image)
        cv2.waitKey()
        cv2.destroyAllWindows()
