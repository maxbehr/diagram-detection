class DiagramConverter(object):
    CONVERTER_TYPE = None

    def __init__(self, shape_detector):
        self.shape_detector = shape_detector
        """ Shape detector, that contains all detected shapes, the contours and the contour hierarchy. """
        self.generic_entities = []

    def convert(self):
        raise NotImplementedError()

    def is_diagram(self):
        raise NotImplementedError()

    def get_generic_entities(self, type=None):
        if type:
            return [e for e in self.generic_entities if e.type == type]
        else:
            return self.generic_entities
