from detector import util, draw_util
from detector.detector.line_detector import LineDetector
from detector.primitives.shape import Shape
from detector.primitives.shape_type import ShapeType
from detector.util import log
from detector.converter.diagram_converter import DiagramConverter
from detector.primitives.generic_entity import GenericEntity


class ClassDiagramTypes:
    CLASS_ENTITY = 0
    ASSOCIATION_ENTITY = 1
    ASSOCIATION_ENTITY_ADVANCED = 2


class ClassDiagramConverter(DiagramConverter):
    CONVERTER_TYPE = "class_diagram"

    STR_ASSOC_FROM = "ASSOCIATION_FROM"
    STR_ASSOC_TO = "ASSOCIATION_TO"
    STR_ASSOC_PART = "ASSOCIATION_PART"
    STR_CLASS_NAME = "CLASS_NAME"

    def convert(self):
        log("transform to class primitives")
        self.generic_entities = self.generic_entities + self._extract_classes()
        self.generic_entities = self.generic_entities + self._extract_associations()
        self._link_associations_with_classes()

        return self.generic_entities

    def _extract_classes(self):
        """
        Extracts the class entities from a class diagram sketch.
        :return: An array of GenericEntities, were each GenericEntity contains a found class
        """
        """
        Extracts the class entities from a class diagram sketch.
        :return: An array of GenericEntities, were each GenericEntity contains a found class
        """
        log(f"Extract classes from {len(self.shape_detector.shapes)} shapes")

        found_classes = []
        sorted_contours = self.shape_detector.sort_contours_by_parent()
        class_counter = 0
        for k, v in sorted_contours.items():
            contour_groups = util.group_contours_by_x_pos(v)

            for group_key, group_value in contour_groups.items():
                # Create class entities
                if len(group_value) == 3:
                    new_class = GenericEntity(ClassDiagramTypes.CLASS_ENTITY)
                    new_class.set(ClassDiagramConverter.STR_CLASS_NAME, f"Class {class_counter}")

                    # Add shapes to class
                    new_class.add_shape(self.shape_detector.create_shape(group_value[0]))
                    new_class.add_shape(self.shape_detector.create_shape(group_value[1]))
                    new_class.add_shape(self.shape_detector.create_shape(group_value[2]))

                    # new_class.set("name_contour", group_value[0])
                    # new_class.set("attribute_contour", group_value[1])
                    # new_class.set("method_contour", group_value[2])

                    found_classes.append(new_class)
                    class_counter += 1

        log(f"{len(found_classes)} class entities found")
        return found_classes

    def _extract_associations(self):
        """
        Main method that calls the sub methods in order to extract all associations from the image.
        :return: An array of GenericEntities, were each GenericEntity contains an extracted association
        """
        # Remove class entitites in order to find associations
        img = util.remove_generic_entities_in_image(self.shape_detector.image, self.generic_entities, ClassDiagramTypes.CLASS_ENTITY)
        advanced_associations = self._extract_advanced_associations(img)

        img = util.remove_generic_entities_in_image(img, advanced_associations, ClassDiagramTypes.ASSOCIATION_ENTITY_ADVANCED, preprocess=False)
        simple_associations = self._extract_simple_associations(img)

        return simple_associations + advanced_associations

    def _extract_simple_associations(self, image):
        """
        Tries to extract the associations that are simple lines between classes.
        :param image: The image the associations are extracted from
        :return: An array of GenericEntities, were each GenericEntity contains the extracted association
        """
        line_detector = LineDetector()
        line_detector.init(image)
        line_detector.find_lines()
        lines = line_detector.merge_lines()
        log(f"{len(lines)} lines found")

        found_associations = []
        for l in lines:
            new_assoc = GenericEntity(ClassDiagramTypes.ASSOCIATION_ENTITY)
            new_assoc.add_shape(l)
            found_associations.append(new_assoc)

        log(f"{len(found_associations)} simple associations found")
        return found_associations

    def _extract_advanced_associations(self, image):
        """
        Tries to extract the associations such as inheritance, aggregation, composition between classes.
        :param image: The image the associations are extracted from
        :return: An array of GenericEntities, were each GenericEntity contains an extracted association
        """
        found_associations = []

        # Extract inheritance shapes
        for shape in self.shape_detector.shapes:
            if shape.shape is ShapeType.TRIANGLE:
                new_inheritance_assoc = GenericEntity(ClassDiagramTypes.ASSOCIATION_ENTITY_ADVANCED)
                log(f"Advanced association found: {shape}")
                new_inheritance_assoc.add_shape(shape)
                found_associations.append(new_inheritance_assoc)

        log(f"{len(found_associations)} advanced associations found")
        return found_associations

    def _link_associations_with_classes(self):
        """
        Links the found classes and associations with each other.
        """
        log(f"Try linking classes with associations")
        class_entities = self.get_generic_entities(types=[ClassDiagramTypes.CLASS_ENTITY])
        assoc_entities = self.get_generic_entities(types=[ClassDiagramTypes.ASSOCIATION_ENTITY])
        inher_entities = self.get_generic_entities(types=[ClassDiagramTypes.ASSOCIATION_ENTITY_ADVANCED])

        remaining_assoc_entities = []

        # Link lines with found advanced association shapes
        for a in assoc_entities:
            line = a.shapes[0]  # GenericEntity of type ASSOCIATION_ENTITY always has just one shape, which is a Line
            line_start = line.start_xy()
            line_end = line.end_xy()

            # Link with inheritance
            for c in inher_entities:
                inheritance_bounding_box = c.bounding_box()

                if util.is_point_in_area(line_start, inheritance_bounding_box) or util.is_point_in_area(line_end, inheritance_bounding_box):
                    a.add_shape(c)
                    log("Association part for inheritance association found")
                else:
                    remaining_assoc_entities.append(a)

        # Link class entities with remaining associations
        for c in class_entities:
            class_bounding_box = c.bounding_box()

            # ... with simple associations
            for a in remaining_assoc_entities:
                line = a.shapes[0]  # GenericEntity of type ASSOCIATION_ENTITY always has just one shape, which is a Line
                line_start = line.start_xy()
                line_end = line.end_xy()

                if util.is_point_in_area(line_start, class_bounding_box):
                    a.set(ClassDiagramConverter.STR_ASSOC_FROM, c)
                    log("FROM association found")

                elif util.is_point_in_area(line_end, class_bounding_box):
                    a.set(ClassDiagramConverter.STR_ASSOC_TO, c)
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
