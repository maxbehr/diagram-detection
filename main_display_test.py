import argparse
import cv2
from detector.detector import *
from detector import util
from detector.shape_type import ShapeType
from detector.util import log
import numpy as np

winname = "Window"

hough_winname = "Hough Lines"
houghp_winname = "HoughP Lines"
winname = "Erosion Dilation"
win_original = "Original"

image = None

def nothing(arg):
    # Get trackbar values
    rho = cv2.getTrackbarPos(tbRho, hough_winname) + 1
    theta = cv2.getTrackbarPos(tbTheta, hough_winname) + 1
    threshold = cv2.getTrackbarPos(tbThreshold, hough_winname) + 1
    theta = (np.pi / 180) * (theta)

    minLineLength = cv2.getTrackbarPos(tbMinLineLength, hough_winname) + 1
    maxLineGap = cv2.getTrackbarPos(tbMaxLineGap, hough_winname) + 1

    original_copy_hough = image.copy()
    original_copy_houghp = image.copy()

    hough_lines = find_hough_lines(original_copy_hough, rho, theta, threshold)
    draw_hough_lines(hough_lines, original_copy_hough)

    houghp_lines = find_houghp_lines(original_copy_houghp, rho, theta, threshold, minLineLength, maxLineGap)
    draw_houghp_lines(houghp_lines, original_copy_houghp)

    cv2.imshow(hough_winname, original_copy_hough)
    cv2.imshow(houghp_winname, original_copy_houghp)

    pass


def find_houghp_lines(image, rho, theta, threshold, minLineLength, maxLineGap):
    #img = util.create_canny_edge_image(image)
    houghp_lines = shape_detector.find_lines_in_image_houghp(image, rho, theta, threshold, minLineLength, maxLineGap)
    log(f"Found {len(houghp_lines)} Hough lines")

    return houghp_lines


def draw_houghp_lines(lines, image):
    for x in range(0, len(lines)):
        for x1, y1, x2, y2 in lines[x]:
            cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 2)


def find_hough_lines(image, rho, theta, threshold):
    #img = util.create_canny_edge_image(image)
    hough_lines = shape_detector.find_lines_in_image_hough(image, rho, theta, threshold)
    log(f"Found {len(hough_lines)} HoughP lines")

    return hough_lines


def draw_hough_lines(lines, image):
    for x in range(0, len(lines)):
        for rho, theta in lines[x]:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))

            cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 2)


if __name__ == '__main__':

    cv2.namedWindow(hough_winname)
    cv2.moveWindow(hough_winname, 800, 0)

    cv2.namedWindow(houghp_winname)
    cv2.moveWindow(houghp_winname, 0, 500)

    cv2.namedWindow(winname)
    cv2.moveWindow(winname, 0, 0)

    # Rho
    tbRho = "Rho"
    cv2.createTrackbar(tbRho, hough_winname, 50, 100, nothing)

    # Theta
    tbTheta = "Theta"
    cv2.createTrackbar(tbTheta, hough_winname, 40, 100, nothing)

    # Threshold
    tbThreshold = "Threshold"
    cv2.createTrackbar(tbThreshold, hough_winname, 1, 100, nothing)

    # MinLineLength
    tbMinLineLength = "MinLineLength"
    cv2.createTrackbar(tbMinLineLength, hough_winname, 1, 100, nothing)

    # MaxLineGap
    tbMaxLineGap = "MaxLineGap"
    cv2.createTrackbar(tbMaxLineGap, hough_winname, 1, 100, nothing)

    img_path = "img/class_diagram_notation.jpeg"
    #img_path = "img/class_pencil.jpeg"
    #img_path = "img/class.jpeg"
    #img_path = "img/class2.jpeg"
    #img_path = "img/usecase.jpeg"
    #img_path = "img/circles.jpeg"
    #img_path = "img/ocr_test.jpeg"
    #img_path = "img/ocr_test2.jpeg"

    #   Detect all shapes
    shape_detector = ShapeDetector(img_path)
    image = shape_detector.image
    original = image.copy()

    # Press R for Reset
    # Press B for binary image
    # Press I for inverted image
    # Press E for erosion
    # Press D for dilation
    # Press C for Canny Edge
    # Press H for Hough Lines
    # Press P for HoughP Lines

    # Loop for get trackbar pos and process it
    while True:
        ch = cv2.waitKey(5)

        # C - Canny Edge
        if ch == 99:
            image = util.create_canny_edge_image(image, min=50, max=150)

        # D - Dilate
        if ch == 100:
            log("Dilate")
            image = util.dilate(image)

        # E - Erode
        if ch == 101:
            log("Erode")
            image = util.erode(image)

        # C - Find Classes
        if ch == 49:
            shape_detector = ShapeDetector(img_path)
            shapes = shape_detector.find_shapes()
            diagram_converter = DiagramTypeDetector.find_converter(shape_detector)
            entities = diagram_converter.extract_classes()
            image = util.draw_class_entities_on_img(entities, image)
            log(f"{len(shapes)} shapes in image found")

        # B - Binary
        if ch == 98:
            image = util.create_binary_img(image)

        # I - Inverted
        if ch == 105:
            image = util.create_inverted_image(image)

        # R - Reset
        if ch == 114:
            image = shape_detector.image
            original = image.copy()

        if ch == 27:
            break

        cv2.imshow(winname, image)
        #cv2.imshow(win_original, original)

    cv2.destroyAllWindows()
