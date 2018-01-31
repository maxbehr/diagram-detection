from detector.util import distance_between


class Line:
    def __init__(self, point_a, point_b):
        self.point_a = point_a
        self.point_b = point_b

    def start(self):
        return self.point_a

    def start_xy(self):
        return self.point_a.x, self.point_a.y

    def end(self):
        return self.point_b

    def end_xy(self):
        return self.point_b.x, self.point_b.y

    def length(self):
        return distance_between(self.start(), self.end())

    def contains_point(self, point):
        return self.start_xy() == point.get_xy_tuple() or self.end_xy() == point.get_xy_tuple()

    def slope(self):
        """
        Calculates the slope of this line and returns it.
        :return: Slope of this line
        """
        return Line._slope(self.point_a, self.point_b)

    def bounding_box(self):
        x1, y1 = self.start_xy()
        x2, y2 = self.end_xy()

        if x1 < x2:
            xb1 = x1
            xb2 = x2
        else:
            xb1 = x2
            xb2 = x1

        if y1 < y2:
            yb1 = y1
            yb2 = y2
        else:
            yb1 = y2
            yb2 = y1

        wb = xb2 - xb1
        hb = yb2 - yb1

        return xb1, yb1, wb, hb

    def _slope(a, b):
        """
        Calculates the slope between the given two points.
        :param a: Point a
        :param b: Point b
        :return: Slope between two points
        """
        x1, y1 = a.get_xy_tuple()
        x2, y2 = b.get_xy_tuple()
        return y2 - y1 / x2 - x1

    def __str__(self):
        return f"start: {self.start()}, end: {self.end()}, length: {self.length()}, slope: {self.slope()}"
