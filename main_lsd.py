import argparse
import cv2
import math

from detector.detector import *
from detector import util
from detector.point import *
from detector.line import *
from detector.shape_type import ShapeType
from detector.util import log
import numpy as np
import imutils
import time

winname = "LSD test"
wincanny = "canny"


def is_same_line(line_a, line_b):
    return is_close(*line_a.start(), *line_b.start()) and \
           is_close(*line_b.start(), *line_b.end())


def is_close(x1, y1, x2, y2):
    max_distance = 30

    s1 = math.pow(x2 - x1, 2)
    s2 = math.pow(y2 - y1, 2)

    d = math.sqrt(s1 + s2)

    return d <= max_distance


def is_line_in(lines, line):
    for l in lines:
        if is_same_line(l, line):
            return True
    return False


def merge_lines(lines):
    merged_lines = []
    for line in lines:
        if not is_line_in(merged_lines, line):
            merged_lines.append(line)
    return merged_lines


if __name__ == '__main__':

    cv2.namedWindow(winname)
    cv2.namedWindow(wincanny)

    img_path = "img/class_diagram_notation.jpeg"

    # Line Segment Detector
    lsd_image = cv2.imread(img_path)
    lsd_image = imutils.resize(lsd_image, width=700)
    lsd_gray = cv2.cvtColor(lsd_image, cv2.COLOR_BGR2GRAY)
    lsd_gauss = cv2.GaussianBlur(lsd_gray,(9,9),0)
    lsd_edges = cv2.Canny(lsd_gauss, 100, 150)

    cv2.imshow(wincanny, lsd_edges)

    LSD = cv2.createLineSegmentDetector()
    lines, width, prec, nfa = LSD.detect(lsd_edges)

    lsd_color = cv2.cvtColor(lsd_gray, cv2.COLOR_GRAY2BGR)

    log(f"{len(lines)} lines through LSD found")

    all_lines = []
    for i in range(len(lines)):
        for x1, y1, x2, y2 in lines[i]:
            line = Line(Point(x1,y1), Point(x2, y2))
            all_lines.append(line)

    # Merged lines
    merged_lines = merge_lines(all_lines)
    log(f"Lines were merged. Still {len(merged_lines)} lines")

    for l in merged_lines:
        start = l.start()
        end = l.end()
        #print("draw line from " + str(start) + " to " + str(end))
        cv2.line(lsd_color, start, end, (0, 0, 255), 2)
        #cv2.waitKey(1)
        #time.sleep(0.2)

    while True:
        cv2.imshow(winname, lsd_color)
        ch = cv2.waitKey(5)

    cv2.destroyAllWindows()
