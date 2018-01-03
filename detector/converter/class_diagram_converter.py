from detector.util import *
from detector.converter.diagram_converter import DiagramConverter


class ClassDiagramConverter(DiagramConverter):
    CONVERTER_TYPE = "class_diagram"

    def transform_shapes_to_diagram(self):
        log("transform to class diagram")

    @classmethod
    def is_diagram(cls, shapes):
        return True
