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

    def __str__(self):
        return f"start: {self.start()}, end: {self.end()}, length: {self.length()}"
