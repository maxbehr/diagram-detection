from detector.export.exporter import Exporter


class DiagramExporter(Exporter):
    def __init__(self, image, converter, options):
        self.image = image.copy()
        self.converter = converter
        self.opts = options

    def export(self):
        pass
