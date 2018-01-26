class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_xy_tuple(self):
        return self.x, self.y

    def __str__(self):
        return str(self.get_xy_tuple())
