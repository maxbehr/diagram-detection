from detector import util
from detector import draw_util
from detector.detector.line_detector import LineDetector
from detector.primitives.shape import Shape
from detector.util import log
from detector.util import ShapeType
from detector.converter.diagram_converter import DiagramConverter
from detector.primitives.generic_entity import GenericEntity


class ClassDiagramTypes:
    CLASS_ENTITY = 0
    ASSOCIATION_ENTITY = 1


class ClassDiagramConverter(DiagramConverter):
    CONVERTER_TYPE = "class_diagram"

    def convert(self):
        log("transform to class primitives")
        self.generic_entities = self.generic_entities + self._extract_classes()
        self.generic_entities = self.generic_entities + self._extract_associations()
        self._link_associations_with_classes()

        return self.generic_entities

    def _extract_classes(self):
        log(f"Extract classes from {len(self.shape_detector.shapes)} shapes")

        found_classes = []
        sorted_contours = self.shape_detector.sort_contours_by_parent()
        for k, v in sorted_contours.items():
            contour_groups = util.group_contours_by_x_pos(v)

            for group_key, group_value in contour_groups.items():
                # Create class entities
                if len(group_value) == 3:
                    new_class = GenericEntity(ClassDiagramTypes.CLASS_ENTITY)

                    # Add shapes to class
                    new_class.add_shape(Shape(group_value[0]))
                    new_class.add_shape(Shape(group_value[1]))
                    new_class.add_shape(Shape(group_value[2]))

                    # new_class.set("name_contour", group_value[0])
                    # new_class.set("attribute_contour", group_value[1])
                    # new_class.set("method_contour", group_value[2])

                    found_classes.append(new_class)

        log(f"{len(found_classes)} class entities found")
        return found_classes

    def _extract_associations(self):
        # Remove class entitites in order to find associations
        img = util.remove_generic_entities_in_image(self.shape_detector.image, self.generic_entities, ClassDiagramTypes.CLASS_ENTITY)

        line_detector = LineDetector()
        line_detector.init(img)
        line_detector.find_lines()
        lines = line_detector.merge_lines()
        log(f"{len(lines)} lines found")

        found_associations = []
        for l in lines:
            new_assoc = GenericEntity(ClassDiagramTypes.ASSOCIATION_ENTITY)
            new_assoc.add_shape(l)

            found_associations.append(new_assoc)

        log(f"{len(found_associations)} associations entities found")
        return found_associations

    def _link_associations_with_classes(self):
        log(f"Try linking classes with associations")
        class_entities = self.get_generic_entities(type=ClassDiagramTypes.CLASS_ENTITY)
        assoc_entities = self.get_generic_entities(type=ClassDiagramTypes.ASSOCIATION_ENTITY)

        for c in class_entities:
            class_bounding_box = c.bounding_box()

            for a in assoc_entities:
                line = a.shapes[0]  # GenericEntity of type ASSOCIATION always has just one shape, which is a Line
                line_start = line.start_xy()
                line_end = line.end_xy()

                if util.is_point_in_area(line_start, class_bounding_box):
                    a.set("ASSOCIATION_FROM", c)
                    log("FROM association found")

                if util.is_point_in_area(line_end, class_bounding_box):
                    a.set("ASSOCIATION_TO", c)
                    log("TO association found")

    @classmethod
    def is_diagram(cls, shape_detector):
        return True

    def get_attributes(self):
        attributes = util.get_contour_children_for(self.shape.contour_index, self.shape_detector.hierarchy)
        return attributes

    def draw_class_entities_on_img(self, entities):
        entities = filter(lambda x: x.type == ClassDiagramTypes.CLASS_ENTITY, entities)
        return draw_util.draw_entities_on_image(self.shape_detector.image, entities)
