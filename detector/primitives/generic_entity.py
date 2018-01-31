
class GenericEntity:
    def __init__(self, type=None):
        self.type = type
        self.data = {}
        self.shapes = []

    def add_shape(self, shape):
        self.shapes.append(shape)

    def get_all_contours(self):
        return [s.contour for s in self.shapes]

    def call(self, name):
        getattr(self, name)()

    def set(self, name, data):
        self.data[name] = data

    def get(self, name):
        return self.data[name]

    def __str__(self):
        return f"Type id: {self.type} - contains {len(self.shapes)} shapes"
