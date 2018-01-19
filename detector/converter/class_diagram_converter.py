from detector import util
from detector.util import log
from detector.util import ShapeType
from detector.converter.diagram_converter import DiagramConverter
from detector.diagram.generic_entity import GenericEntity


class ClassDiagramTypes:
    CLASS_ENTITY = 0
    ASSOCIATION_ENTITY = 1


class ClassDiagramConverter(DiagramConverter):
    CONVERTER_TYPE = "class_diagram"

    def transform_shapes_to_diagram(self):
        log("transform to class diagram")
        self.extract_classes()

    def extract_classes(self):
        log(f"Extract classes from {len(self.shape_detector.shapes)} shapes")
        log(self.shape_detector.hierarchy)

        sorted_contours = self.shape_detector.sort_contours_by_parent()
        for k, v in sorted_contours.items():
            contour_groups = util.group_contours_by_x_pos(v)

            for group_key, group_value in contour_groups.items():
                log(f"group_key {group_key} has {len(group_value)} items")

                # Create class entities
                if len(group_value) == 3:
                    new_class = GenericEntity(None)
                    new_class.type = ClassDiagramTypes.CLASS_ENTITY

                    new_class.set("name_contour", group_value[0])
                    new_class.set("attribute_contour", group_value[1])
                    new_class.set("method_contour", group_value[2])

                    self.generic_entities.append(new_class)

        return self.generic_entities

    @classmethod
    def is_diagram(cls, shape_detector):
        return True

    def create_class_entity(self, shape):
        new_class = GenericEntity(shape)
        new_class.type = ClassDiagramTypes.CLASS_ENTITY

        contour_children = util.get_contour_children_for(shape.contour_index, self.shape_detector.hierarchy)
        sorted_contours = util.get_sorted_contours_for_hierachy_entries(self.shape_detector.contours, contour_children)

        new_class.set("name_contour", sorted_contours[0])
        new_class.set("attribute_contour", sorted_contours[1])
        new_class.set("method_contour", sorted_contours[2])

        return new_class

    def get_attributes(self):
        attributes = util.get_contour_children_for(self.shape.contour_index, self.shape_detector.hierarchy)
        return attributes
