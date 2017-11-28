import cv2
import imutils
import numpy as np
from detector.shape import Shape

class DiagramDetector:
    def __init__(self):
        self.orig_image = None
        self.image = None
        print("DiagramDetector initialized")

    def detect_shape(self, c):
        """
        Identifies the given contour as shape.
        :param c:
        :return: The shape of type Shape
        """
        s = Shape.UNIDENTIFIED

        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.05 * peri, True)

        if len(approx) == 3:
            s = Shape.TRIANGLE

        if len(approx) == 4:
            s = Shape.RECTANGLE

        return s

    def is_diagram_rect(self, c):
        x, y, w, h = cv2.boundingRect(c)
        ratio = self.aspect_ratio(c)
        area = w * h

        return self.detect_shape(c) == Shape.RECTANGLE #and h > w and area > 200 #and ratio < 1

    def aspect_ratio(self, c):
        """
        Calculates the aspect ratio of the given contour.
        :param c:
        :return: The aspect ratio.
        """
        x, y, w, h = cv2.boundingRect(c)
        return float(w) / h

    def image_area(self, image):
        return image.shape[:2]

    def area(self, c):
        """
        Calculates the area of the given contour.
        :param c:
        :return: The area as floati
        """
        x, y, w, h = cv2.boundingRect(c)
        return w * h

    def detect_contours(self, image):
        """
        Detects the contours of the given image.
        :param image: Image you want the contours of
        :return: A tuple containg (img, contours, hierarchy)
        """
        #   cv2.RETR_TREE --> Relationships between contours
        #   cv2.RETR_EXTERNAL --> Ohne doppelte Konturen
        return cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    def print_details(self, c):
        """
        Prints some detailed information of the given contour.

        :param c: Countour you want some details of.
        """
        x, y, w, h = cv2.boundingRect(c)

        print("shape: {shape}, aspect_ratio: {ratio}, w: {w}, h: {h}, area: {area}".format(
            shape=self.detect_shape(c),
            ratio=self.aspect_ratio(c),
            w=w,
            h=h,
            area=self.area(c)
        ))

    def print_image_details(self, image):
        height, width = self.image_area(image)
        print("Image - width: {w}, height: {h}, area: {area}".format(w=width, h=height, area=(width * height)))

    def preprocess(self, image):
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


    def is_class_diagram(self, image_path):
        """
        Identifies an image either as class diagram or not.

        :param image_path: Path of the image
        :return: true if the image was detected as UML class diagram, false otherwise.
        """

        # Read the image
        self.orig_image = cv2.imread(image_path)
        self.image = imutils.resize(self.orig_image, width=700)

        # Preprocess the image
        self.print_image_details(self.image)
        proc_image = self.preprocess(self.image)

        # Calc the ratio of the image
        #ratio = self.orig_image.shape[0] / float(self.image.shape[0])

        # Use canny edge detection on resized image
        #canny = cv2.Canny(self.image, 100, 100)
        #canny = cv2.dilate(canny, (3,3), iterations=5)
        # cv2.imshow("canny", canny)

        # Holds the area of all rects that were defined as class diagram rectangles
        area_rects = 0
        img, contours, hierarchy = self.detect_contours(proc_image)

        found_diagram_rects = []
        for c in contours:
            if self.is_diagram_rect(c):
                self.print_details(c)

                found_diagram_rects.append(c)
                area_rects += self.area(c)

                # shape = self.detect_shape(c)
                # M = cv2.moments(c)
                # cX = int((M["m10"] / M["m00"]) * ratio)
                # cY = int((M["m01"] / M["m00"]) * ratio)

                # c = c.astype("float")
                # c *= ratio
                # c = c.astype("int")
                #cv2.drawContours(self.image, [c], -1, (0, 255, 0), 2)

                x, y, w, h = cv2.boundingRect(c)
                cv2.rectangle(self.image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Calculate percentage of rectangle area in image
        image_height, image_width = self.image_area(self.image)
        area_rects_percentage = round(area_rects / (image_width * image_height) * 100, 4)
        print("Found rects: {amount}, area: {area} ({perc}%)".format(amount=len(found_diagram_rects), area=area_rects, perc=area_rects_percentage))


    def show_result(self):
        """
        Opens the image in a window.
        """
        cv2.namedWindow("Image", cv2.WINDOW_AUTOSIZE)
        cv2.imshow("Image", self.image)
        cv2.waitKey()
        cv2.destroyAllWindows()
