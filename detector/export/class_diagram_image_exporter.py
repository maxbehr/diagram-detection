from detector.constants import constants
from detector.converter.class_diagram_converter import ClassDiagramConverter, ClassDiagramTypes
from detector.export.diagram_exporter import DiagramExporter
from detector import util, draw_util
from detector.util import log


class ClassDiagramImageExporter(DiagramExporter):
    EXPORTER_ID= "class_diagram_image_exporter"

    def export(self):
        log("Exporting class diagram to image")
        #   Label classes
        class_entities = self.converter.get_generic_entities(types=[ClassDiagramTypes.CLASS_ENTITY])
        log(f"\t... with {len(class_entities)} classes")
        self.image = draw_util.draw_bounding_boxes(self.image, class_entities, labels=True)

        # Extract text from class entities
        #for c in class_entities:
        #    for s in c.shapes:
        #        s.ocr()

        #   Draw bounding boxes of advanced associations
        advanced_association_entities = self.converter.get_generic_entities(
            types=[ClassDiagramTypes.ASSOCIATION_ENTITY_ADVANCED])
        log(f"\t... with {len(advanced_association_entities)} advanced associations")
        self.image = draw_util.draw_bounding_boxes(self.image, advanced_association_entities, color=constants.COLOR_RED, labels=True)

        #   Draw normal entities
        association_entities = self.converter.get_generic_entities(types=[ClassDiagramTypes.ASSOCIATION_ENTITY])
        log(f"\t... with {len(association_entities)} normal associations")
        self.image = draw_util.draw_entities_on_image(self.image, association_entities, color=constants.COLOR_YELLOW)

        #   Print relations between classes
        association_entities = association_entities + advanced_association_entities
        for i, assoc in enumerate(association_entities):
            from_class = assoc.get(ClassDiagramConverter.STR_ASSOC_FROM)
            to_class = assoc.get(ClassDiagramConverter.STR_ASSOC_TO)

            if from_class is not None and to_class is not None:
                log(f"Association {i} points from {from_class.get(constants.STR_GENERIC_ENTITY_LABEL_NAME)} "
                    f"to {to_class.get(constants.STR_GENERIC_ENTITY_LABEL_NAME)}")

        return self.image
