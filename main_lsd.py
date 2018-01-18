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
    return line_a.start_xy() == line_b.start_xy() and \
           line_a.end_xy() == line_b.end_xy()


def could_be_same_line(line_a, line_b):
    return is_close(*line_a.start_xy(), *line_b.start_xy()) and \
           is_close(*line_b.start_xy(), *line_b.end_xy())


def are_lines_connected(line_a, line_b):
    return line_a.end_xy == line_b.start_xy or line_a.end_xy == line_b.end_xy


def is_close(x1, y1, x2, y2):
    max_distance = 20

    s1 = math.pow(x2 - x1, 2)
    s2 = math.pow(y2 - y1, 2)

    d = math.sqrt(s1 + s2)

    return d <= max_distance


def is_line_in(lines, line):
    for l in lines:
        if could_be_same_line(l, line):
            return True
    return False


def merge_lines(lines):
    merged_lines = []
    for line in lines:
        if not is_line_in(merged_lines, line):
            merged_lines.append(line)
    return merged_lines


def get_line_end_point_in_other_line(point, lines):
    for l in lines:
        if is_close(*point, *l.start_xy()):
            return l.start_xy()

        elif is_close(*point, *l.end_xy()):
            return l.end_xy()

    return None


def short_circuit(point, lines):
    last_valid_point = None
    last_found_point = point
    while last_found_point is not None:
        last_found_point = get_line_end_point_in_other_line(last_found_point, lines)
        if last_found_point is not None:
            last_valid_point = Point(*last_found_point)

    return last_valid_point


def short_circuit_line(line, lines):
    last_valid_line = None
    last_found_line = line
    while last_found_line is not None:
        for l in lines:
            if not is_same_line(last_found_line, l):
                if are_lines_connected(last_found_line, l):
                    last_found_line = l

        last_found_line = None
        break

    return last_found_line


def get_path(line_a, line_b):
    a_start = line_a.start_xy()
    a_end = line_a.end_xy()
    b_start = line_b.start_xy()
    b_end = line_b.end_xy()

    if is_close(*a_start, *b_start):
        return a_end, b_end

    if is_close(*a_start, *b_end):
        return a_end, b_start

    if is_close(*a_end, *b_end):
        return a_start, b_start

    if is_close(*a_end, *b_start):
        return a_start, b_end

    return None


def find_path(line, lines):
    origin_start = line.start()
    origin_end = line.end()

    potential_path = None
    lines = list(filter(lambda x: is_same_line(x, line) is False, lines))
    for l in lines:
        potential_path = get_path(line, l)

        # Set new line
        if potential_path is not None:
            potential_start, potential_end = potential_path
            potential_start_point = Point(*potential_start)
            potential_end_point = Point(*potential_end)

            line = Line(potential_start_point, potential_end_point)
        else:
            break

    return line


if __name__ == '__main__':

    cv2.namedWindow(winname)
    #cv2.namedWindow(wincanny)

    img_path = "img/class_diagram_notation.jpeg"

    # Line Segment Detector
    lsd_image = cv2.imread(img_path)
    lsd_image = imutils.resize(lsd_image, width=700)
    lsd_gray = cv2.cvtColor(lsd_image, cv2.COLOR_BGR2GRAY)
    lsd_gauss = cv2.GaussianBlur(lsd_gray,(9,9),0)
    lsd_edges = cv2.Canny(lsd_gauss, 100, 150)

    #cv2.imshow(wincanny, lsd_edges)

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

    # path_lines = []
    # for l in merged_lines:
    #     #path_line = find_path(l, merged_lines)
    #     short_circuit_end_point = short_circuit_line(l, merged_lines)
    #
    #     if short_circuit_end_point is not None:
    #         short_circuit_line = Line(l.start(), short_circuit_end_point)
    #         path_lines.append(short_circuit_line)
    #     else:
    #         path_lines.append(l)
    #
    # log(f"Found path lines: {len(path_lines)}")

    path_lines = []
    for i,l1 in enumerate(merged_lines):
        l2 = None
        if (i+1) < len(merged_lines):
            l2 = merged_lines[i+1]

        if l1 is not None and l2 is not None and not is_same_line(l1, l2):
            path = get_path(l1, l2)
            if path is not None:
                start, end = path

                new_line = Line(Point(*start), Point(*end))
                if not is_line_in(path_lines, new_line):
                    path_lines.append(new_line)

    log(f"Found path lines: {len(path_lines)}")

    for i,l in enumerate(path_lines):
        cv2.line(lsd_color, l.start_xy(), l.end_xy(), (0, 255, 0), 2)


    for i,l in enumerate(merged_lines):
        start = l.start_xy()
        end = l.end_xy()

        #print("draw line from " + str(start) + " to " + str(end))
        cv2.line(lsd_color, start, end, (0, 0, 255), 2)

        x = int(start[0])
        y = int(start[1])
        cv2.putText(lsd_color, str(i), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

        #cv2.waitKey(1)
        #time.sleep(0.2)

    while True:
        cv2.imshow(winname, lsd_color)
        ch = cv2.waitKey(5)

    cv2.destroyAllWindows()
