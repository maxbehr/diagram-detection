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
