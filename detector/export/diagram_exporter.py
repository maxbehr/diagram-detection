class DiagramExporter(object):
    EXPORTER_ID = None

    def __init__(self, image, converter, options):
        self.image = image.copy()
        self.converter = converter
        self.opts = options

    def export(self):
        raise NotImplementedError()
