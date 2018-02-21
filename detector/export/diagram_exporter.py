class DiagramExporter(object):
    EXPORTER_ID = None

    def __init__(self, image, converter):
        self.image = image.copy()
        self.converter = converter

    def export(self):
        raise NotImplementedError()
