from detector.util import *
from detector.converter.diagram_converter import DiagramConverter


class UseCaseDiagramConverter(DiagramConverter):
    CONVERTER_TYPE = "use_case_diagram"

    def transform_shapes_to_diagram(self):
        log("transform to use case diagram")

    @classmethod
    def is_diagram(cls, shapes):
        return False
