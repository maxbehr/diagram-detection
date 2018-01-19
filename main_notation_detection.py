import argparse
import cv2
from detector.detector import *
from image_interaction import image_interaction

winname = "Window"

winname = "Erosion Dilation"
image = None

if __name__ == '__main__':

    cv2.namedWindow(winname)
    cv2.moveWindow(winname, 0, 0)

    #img_path = "img/class_diagram_notation.jpeg"
    #img_path = "img/class_pencil.jpeg"
    #img_path = "img/class.jpeg"
    #img_path = "img/class2.jpeg"
    img_path = "img/class_many.jpeg"
    #img_path = "img/usecase.jpeg"
    #img_path = "img/circles.jpeg"
    #img_path = "img/ocr_test.jpeg"
    #img_path = "img/ocr_test2.jpeg"

    #   Detect all shapes
    shape_detector = ShapeDetector(img_path)
    image = shape_detector.image
    original = image.copy()

    # Loop for get trackbar pos and process it
    while True:
        ch = cv2.waitKey(5)
        image = image_interaction(ch, image, img_path)
        cv2.imshow(winname, image)

        if ch == 27:
            break

    cv2.destroyAllWindows()
