from detector.converter.class_diagram_converter import ClassDiagramConverter, ClassDiagramTypes
from detector.export.diagram_exporter import DiagramExporter
from detector import util, draw_util
from detector.util import log


class ClassDiagramImageExporter(DiagramExporter):
    EXPORTER_ID= "class_diagram_image_exporter"

    def export(self):
        #   Label classes
        class_entities = self.converter.get_generic_entities(types=[ClassDiagramTypes.CLASS_ENTITY])
        log(f"{len(class_entities)} class entitites")
        self.image = draw_util.draw_bounding_boxes(self.image, class_entities, labels=True)

        #   Label advanced associations
        inheritance_entities = self.converter.get_generic_entities(
            types=[ClassDiagramTypes.ASSOCIATION_ENTITY_ADVANCED])
        self.image = draw_util.draw_bounding_boxes(self.image, inheritance_entities, labels=True)

        #   Draw association entities on image
        association_entities = self.converter.get_generic_entities(types=[ClassDiagramTypes.ASSOCIATION_ENTITY])
        log(f"{len(association_entities)} association entitites")
        self.image = draw_util.draw_entities_on_image(self.image, association_entities)

        for i, assoc in enumerate(association_entities):
            from_class = assoc.get(ClassDiagramConverter.STR_ASSOC_FROM)
            to_class = assoc.get(ClassDiagramConverter.STR_ASSOC_TO)

            if from_class is not None and to_class is not None:
                log(f"Association {i} points from {from_class.get(ClassDiagramConverter.STR_CLASS_NAME)} "
                    f"to {to_class.get(ClassDiagramConverter.STR_CLASS_NAME)}")

        return self.image
