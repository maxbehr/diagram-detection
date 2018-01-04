
class GenericEntity:
    def __init__(self, shape):
        self.shape = shape
        self.type = None
        self.class_contour = None
        self.methods = {}

    def add_method(self, name, func):
        self.methods[name] = func

    def call(self, name):
        getattr(self, name)()
