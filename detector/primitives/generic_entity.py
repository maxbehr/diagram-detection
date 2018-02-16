
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

    def bounding_box(self, adjustment=0):
        """
        Returns the bounding box of this GenericEntity by considering all contained shapes.
        :param adjustment: Pixels that will be applied to the xy-coordinates and the width and height of bounding box,
                            in order to adjust the size of the bounding box.
        :return: A tuple containing the xy-coordinates, width and height of the bounding box (x, y, w, h)
        """
        min_y_shape = min(self.shapes, key=lambda shape: shape.y)
        max_y_shape = max(self.shapes, key=lambda shape: shape.y)

        x = min(self.shapes, key=lambda shape: shape.x).x
        w = max(self.shapes, key=lambda shape: shape.w).w
        y = min_y_shape.y
        h = max_y_shape.y + max_y_shape.h - min_y_shape.y

        return x-adjustment,\
               y-adjustment,\
               w+adjustment*2,\
               h+adjustment*2

    def __str__(self):
        return f"Type id: {self.type} - contains {len(self.shapes)} shapes"
