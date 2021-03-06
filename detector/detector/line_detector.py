from detector.primitives.line import Line
from detector.primitives.point import Point
from detector.util import *
import detector.util as util
import math


class LineDetector:
    max_point_distance = 30
    """ Defines the maximum distance two points can have in order to be seen as one point """

    def __init__(self):
        self.edge_image = None
        self.lines = []
        self.LSD = None

        util.log("LineDetector initialized")

    def init_with_image(self, image):
        """
        Initializes the Line Detector with an image that has not been processed with an edge detection, but will be
        Canny Edge'd by this method.
        :param image: Image that will be processed.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gauss = cv2.GaussianBlur(gray, (9, 9), 0)
        self.edge_image = cv2.Canny(gauss, 100, 150)

    def init(self, canny_image):
        """
        Initializes the Line Detector with an image that already contains only its edges.
        :param canny_image:
        :return:
        """
        self.edge_image = canny_image

    def find_lines(self):
        """
        Creates a LineSegmentDetector and finds lines in the image, which are stored and returned.
        :return: List of Line objects
        """
        self.lines = []
        self.LSD = cv2.createLineSegmentDetector()
        lines, width, prec, nfa = self.LSD.detect(self.edge_image)
        # self.LSD.drawSegments(image, lines)

        if lines is not None:
            for i in range(len(lines)):
                for x1, y1, x2, y2 in lines[i]:
                    line = Line(Point(x1, y1), Point(x2, y2))
                    self.lines.append(line)

        log(f"{len(self.lines)} lines found")
        return self.lines

    def is_same_point(point_a, point_b):
        return point_a.get_xy_tuple() == point_b.get_xy_tuple()

    def is_same_line(line_a, line_b):
        return line_a.start_xy() == line_b.start_xy() and \
               line_a.end_xy() == line_b.end_xy()

    def could_be_same_line(line_a, line_b):
        return (LineDetector.is_point_close(line_a.start(), line_b.start()) and LineDetector.is_point_close(line_a.end(), line_b.end())) or \
               (LineDetector.is_point_close(line_a.start(), line_b.end()) and LineDetector.is_point_close(line_a.end(), line_b.start()))

    def are_lines_connected(line_a, line_b):
        return line_a.end_xy == line_b.start_xy or line_a.end_xy == line_b.end_xy

    def are_lines_close(line_a, line_b):
        close = LineDetector.is_point_close(line_a.start(), line_b.start()) or \
                LineDetector.is_point_close(line_a.start(), line_b.end()) or \
                LineDetector.is_point_close(line_a.end(), line_b.start()) or \
                LineDetector.is_point_close(line_a.end(), line_b.end())
        return close

    def is_point_close(p1, p2):
        return LineDetector.is_close(*p1.get_xy_tuple(), *p2.get_xy_tuple()) #and is_close(*p2.get_xy_tuple(), *p1.get_xy_tuple())

    def is_close(x1, y1, x2, y2, max_distance=30):
        s1 = math.pow(x2 - x1, 2)
        s2 = math.pow(y2 - y1, 2)
        d = math.sqrt(s1 + s2)
        return d <= max_distance

    def is_line_in(lines, line):
        for l in lines:
            if LineDetector.could_be_same_line(l, line):
                return True
        return False

    def merge_lines(self):
        self.lines = self._merge_lines(self.lines)
        return self.lines

    def filter_lines(self, **args):
        self.lines = self._filter_lines(self.lines, **args)
        return self.lines

    def _filter_by_angle(lines, min_angle=0):
        lines = [(l1, l2) for l1 in lines for l2 in lines if util.angle_between_lines(l1, l2) >= min_angle and LineDetector.are_lines_close(l1, l2)]
        log(f"{len(lines)} angle lines")
        return lines

    def _filter_lines(self, lines, min_length=None, max_length=None):
        filtered_lines = lines

        if min_length is not None:
            filtered_lines = [l for l in filtered_lines if l.length() >= min_length]

        if max_length is not None:
            filtered_lines = [l for l in filtered_lines if l.length() < max_length]

        return filtered_lines

    def _merge_lines(self, lines):
        """
        Merges lines after checking if they could be the same.
        Does not change the lines list of the object.

        :param lines: The lines you want to merge.
        :return: list of merged lines
        """
        merged_lines = []
        for line in lines:
            if not LineDetector.is_line_in(merged_lines, line):
                merged_lines.append(line)
        log(f"{len(merged_lines)} merged lines")
        return merged_lines

    def _purge_lines(self, lines, min_line_length=100):
        """
        Purges the given lines by checking if they could be the same and if their length is as expected.
        Does not change the lines list of the object.

        :param lines: List of lines that will be checked
        :param min_line_length: Minimum length a line needs to pass the check
        :return: list of pruged lines
        """
        purged_lines = []
        for line in lines:
            if not LineDetector.is_line_in(purged_lines, line):
                # Check line length
                if line.length() >= min_line_length:
                    purged_lines.append(line)

        return purged_lines

    def _same_slope_lines(self):
        # Get lines with the same slope
        same_slope_lines = []

        for i in range(len(self.lines)):
            for j in range(i + 1, len(self.lines)):
                l1 = self.lines[i]
                l2 = self.lines[j]

                if l1 is not l2:
                    slope1 = l1.slope()
                    slope2 = l2.slope()

                    tol = 5

                    if slope1-tol <= slope2 <= slope1+tol or slope2-tol <= slope1 <= slope2+tol:
                        longest = l1 if l1.length() > l2.length() else l2
                        same_slope_lines.append(longest)

        return same_slope_lines

    def get_line_end_point_in_other_line(point, lines):
        for l in lines:
            if LineDetector.is_close(*point, *l.start_xy()):
                return l.start_xy()
            elif LineDetector.is_close(*point, *l.end_xy()):
                return l.end_xy()
        return None

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

    def get_closest_corresponding_point(reference_point, line):
        if LineDetector.is_point_close(reference_point, line.start()):
            return line.start()
        if LineDetector.is_point_close(reference_point, line.end()):
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
                closest_point = LineDetector.get_closest_corresponding_point(point, l)
                if closest_point is None:
                    return LineDetector.get_opposite_line_end(point, l)
                else:
                    return LineDetector.get_next_line_with_corresponding_point(closest_point, lines)
            return point
