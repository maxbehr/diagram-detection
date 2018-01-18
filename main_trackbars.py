import argparse
import cv2
from detector.detector import *
from detector import util
from detector.shape_type import ShapeType
from detector.util import log
import numpy as np

ap = argparse.ArgumentParser()
output_file = "./output/found_shapes.xml"

hough_winname = "Hough Lines"
houghp_winname = "HoughP Lines"

def nothing(arg):
    print(arg)
    rho = cv2.getTrackbarPos(tbRho, hough_winname) + 1
    theta = cv2.getTrackbarPos(tbTheta, hough_winname) + 1
    threshold = cv2.getTrackbarPos(tbThreshold, hough_winname) + 1

    theta = (np.pi / 180) * (theta)


    # HoughP Lines
    houghp_img = shape_detector.image.copy()
    houghp_img = util.create_canny_edge_image(houghp_img)
    houghp_lines = shape_detector.find_lines_in_image_houghp(houghp_img, rho, theta, threshold)
    log(f"Found {len(houghp_lines)} Hough lines")
    for x in range(0, len(houghp_lines)):
        for x1, y1, x2, y2 in houghp_lines[x]:
            cv2.line(houghp_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

    # Hough Lines
    hough_img = shape_detector.image.copy()
    hough_img = util.create_canny_edge_image(hough_img)
    hough_lines = shape_detector.find_lines_in_image_hough(hough_img, rho, theta, threshold)
    log(f"Found {len(hough_lines)} HoughP lines")
    for x in range(0, len(hough_lines)):
        for rho, theta in hough_lines[x]:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))

            cv2.line(hough_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

    cv2.imshow("Hough Lines", hough_img)
    cv2.imshow("HoughP Lines", houghp_img)
    pass

if __name__ == '__main__':

    #img_path = "img/class_pencil.jpeg"
    img_path = "img/class.jpeg"
    #img_path = "img/class2.jpeg"
    #img_path = "img/usecase.jpeg"
    #img_path = "img/circles.jpeg"
    #img_path = "img/ocr_test.jpeg"
    #img_path = "img/ocr_test2.jpeg"

    #   Detect all shapes
    shape_detector = ShapeDetector(img_path)
    shapes = shape_detector.find_shapes()

    #   Detect type of diagram
    diagram_converter = DiagramTypeDetector.find_converter(shape_detector)
    img = shape_detector.get_image_remove_shape_type(ShapeType.RECTANGLE)

    cv2.namedWindow(hough_winname)
    cv2.namedWindow(houghp_winname)

    # Rho
    tbRho = "Rho"
    cv2.createTrackbar(tbRho, hough_winname, 50, 100, nothing)

    # Theta
    tbTheta = "Theta"
    cv2.createTrackbar(tbTheta, hough_winname, 40, 100, nothing)

    # Threshold
    tbThreshold = "Threshold"
    cv2.createTrackbar(tbThreshold, hough_winname, 1, 100, nothing)

    # Loop for get trackbar pos and process it
    while True:
        ch = cv2.waitKey(5)
        if ch == 27:
            break

    cv2.destroyAllWindows()