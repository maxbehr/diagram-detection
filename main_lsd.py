import cv2
import math

from detector import util
from detector import draw_util
from detector.primitives.line import *
from detector.primitives.point import Point
from detector.util import log
import imutils

winname = "LSD test"
wincanny = "canny"


def is_same_point(point_a, point_b):
    return point_a.get_xy_tuple() == point_b.get_xy_tuple()


def is_same_line(line_a, line_b):
    return line_a.start_xy() == line_b.start_xy() and \
           line_a.end_xy() == line_b.end_xy()


def could_be_same_line(line_a, line_b):
    return (is_point_close(line_a.start(), line_b.start()) and is_point_close(line_a.end(), line_b.end())) or \
           (is_point_close(line_a.start(), line_b.end()) and is_point_close(line_a.end(), line_b.start()))


def are_lines_connected(line_a, line_b):
    return line_a.end_xy == line_b.start_xy or line_a.end_xy == line_b.end_xy


def is_point_close(p1, p2):
    return is_close(*p1.get_xy_tuple(), *p2.get_xy_tuple()) #and is_close(*p2.get_xy_tuple(), *p1.get_xy_tuple())


def is_close(x1, y1, x2, y2, max_distance=30):
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


def purge_lines(lines, min_line_length=100):
    purged_lines = []
    for line in lines:
        if not is_line_in(purged_lines, line):
            # Check line length
            if line.length() >= min_line_length:
                purged_lines.append(line)

    return purged_lines


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


def get_opposite_line_end(point, line):
    """
    Takes the given point and compares it to the start and end point of the given line. The point of the line that
    matches the given point will be the opposite line end
    :param point:
    :param line:
    :return:
    """
    if line.start_xy() == point.get_xy_tuple():
        return line.end_xy()
    if line.end_xy() == point.get_xy_tuple():
        return line.start_xy()

    return None


def get_corresponding_point_in_lines(point, lines):
    returned_point = None
    b = False
    for l in lines:
        if is_point_close(point, l.start()):
            returned_point = l.start()
            b = True
        if is_point_close(point, l.end()):
            returned_point = l.end()
            b = True

        if b:
            break

    return returned_point


def get_closest_corresponding_point(reference_point, line):
    if is_point_close(reference_point, line.start()):
        return line.start()
    if is_point_close(reference_point, line.end()):
        return line.end()
    return None


def get_next_line_with_corresponding_point(point, lines):
    if point is None:
        return None
    else:
        lines = list(filter(lambda x: x.contains_point(point) is False, lines))
        log(f"continue with {len(lines)} lines")
        for l in lines:
            log(f"check point {point}")
            closest_point = get_closest_corresponding_point(point, l)
            if closest_point is None:
                return get_opposite_line_end(point, l)
            else:
                return get_next_line_with_corresponding_point(closest_point, lines)
        return point


def sc(line, lines):
    lines = list(filter(lambda x: x != line, lines))

    orig_start = line.end()
    found_point = orig_start
    while found_point is not None and not is_same_point():
        found_point = get_corresponding_point_in_lines(found_point, lines)
        if not is_same_point(found_point):
            lines = list(filter(lambda x: x != line, lines))

    return orig_start, found_point


if __name__ == '__main__':

    cv2.namedWindow(winname)
    #cv2.namedWindow(wincanny)

    #img_path = "img/class_diagram_notation.jpeg"
    #img_path = "img/two_lines.jpg"
    img_path = "img/three_lines.jpg"

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
    merged_lines = purge_lines(all_lines)
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

    # path_lines = []
    # for i,l1 in enumerate(merged_lines):
    #     l2 = None
    #     if (i+1) < len(merged_lines):
    #         l2 = merged_lines[i+1]
    #
    #     if l1 is not None and l2 is not None and not is_same_line(l1, l2):
    #         path = get_path(l1, l2)
    #         if path is not None:
    #             start, end = path
    #
    #             new_line = Line(Point(*start), Point(*end))
    #             if not is_line_in(path_lines, new_line):
    #                 path_lines.append(new_line)
    #
    # log(f"Found path lines: {len(path_lines)}")

    # Draw text at points
    #ppp = [(623.08844, 40.161674), (623.12268, 39.814278)]
    #for point in ppp:
    #    cv2.putText(lsd_color, str(point), (int(point[0]), int(point[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

    path_lines = []
    for l in merged_lines:
        start_point = l.start()
        end_point = get_next_line_with_corresponding_point(start_point, merged_lines)

        if end_point is None:
            end_point = l.end()

        path_lines.append(Line(start_point, end_point))

    log("Draw path lines")
    path_lines = purge_lines(path_lines, 5)
    draw_util.draw_labeled_lines(lsd_color, path_lines, color=(0, 255, 0))

    log("Draw merged lines")
    draw_util.draw_labeled_lines(lsd_color, merged_lines)

        #cv2.waitKey(1)
        #time.sleep(0.2)

    while True:
        cv2.imshow(winname, lsd_color)
        ch = cv2.waitKey(5)

    cv2.destroyAllWindows()
