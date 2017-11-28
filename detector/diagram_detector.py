import cv2
import imutils
from detector.shape import Shape

class DiagramDetector:
    def __init__(self):
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
        approx = cv2.approxPolyDP(c, 0.1 * peri, True)

        if len(approx) == 3:
            s = Shape.TRIANGLE

        if len(approx) == 4:
            s = Shape.RECTANGLE

        return s

    def aspect_ratio(self, c):
        """
        Calculates the aspect ratio of the given contour.
        :param c:
        :return: The aspect ratio.
        """
        x, y, w, h = cv2.boundingRect(c)
        return float(w) / h

    def area(self, c):
        """
        Calculates the area of the given contour.
        :param c:
        :return: The area as floati
        """
        return cv2.contourArea(c)

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
        print("shape: {shape}, aspect_ratio: {ratio}, area: {area}".format(
            shape=self.detect_shape(c),
            ratio=self.aspect_ratio(c),
            area=self.area(c)
        ))

    def is_class_diagram(self, image_path):
        """
        Identifies an image either as class diagram or not.

        :param image_path: Path of the image
        :return: true if the image was detected as UML class diagram, false otherwise.
        """

        # Read the image
        orig_image = cv2.imread(image_path)

        # Resize the image
        self.image = imutils.resize(orig_image, width=600)

        # Calc the ratio of the image
        ratio = orig_image.shape[0] / float(self.image.shape[0])

        # Convert the image to grayscale
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        #blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        #thresh = cv2.adaptiveThreshold(gray, 127, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        # Use canny edge detection on resized image
        canny = cv2.Canny(self.image, 100, 200)

        img, contours, hierarchy = self.detect_contours(canny)
        for c in contours:
            self.print_details(c)

            shape = self.detect_shape(c)
            M = cv2.moments(c)
            cX = int((M["m10"] / M["m00"]) * ratio)
            cY = int((M["m01"] / M["m00"]) * ratio)

            c = c.astype("float")
            c *= ratio
            c = c.astype("int")
            cv2.drawContours(self.image, [c], -1, (0, 255, 0), 2)

    def show_result(self):
        """
        Opens the image in a window.
        """
        cv2.imshow("Image", self.image)
        print("Show result image")
        cv2.waitKey()
