from detector import util
from detector.primitives.shape import Shape
from detector.util import log
from detector.util import ShapeType
from detector.converter.diagram_converter import DiagramConverter
from detector.primitives.generic_entity import GenericEntity


class UseCaseDiagramConverter(DiagramConverter):
    CONVERTER_TYPE = "usecase_diagram"

    def convert(self):
        log("transform to use case primitives")

    def is_diagram(cls, shape_detector):
        return False

    def draw_class_entities_on_img(self, entities):
        pass
