
class GenericEntity:
    def __init__(self, shape):
        self.shape = shape
        self.type = None
        self.data = {}
        self.methods = {}

    def add_method(self, name, func):
        self.methods[name] = func

    def call(self, name):
        getattr(self, name)()

    def set(self, name, data):
        self.data[name] = data

    def get(self, name):
        return self.data[name]
