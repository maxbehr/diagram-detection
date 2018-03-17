class Exporter(object):
    EXPORTER_ID = None

    def __init__(self, image, shape_detector):
        self.image = image.copy()
        self.shape_detector = shape_detector

    def export(self):
        raise NotImplementedError()
