class Line:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def start(self):
        return self.a.x, self.a.y

    def end(self):
        return self.b.x, self.b.y
