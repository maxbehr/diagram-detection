from detector.util import *
from detector.diagram.diagram_converter import DiagramConverter
from detector.diagram.shape import Shape
import detector.util as util


class ClassDiagramConverter(DiagramConverter):
    CONVERTER_TYPE = "class_diagram"

    def transform_shapes_to_diagram(self):
        log("transform to class diagram")

