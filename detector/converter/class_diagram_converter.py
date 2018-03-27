from detector import util, draw_util
from detector.constants import constants
from detector.detector.line_detector import LineDetector
from detector.primitives.line import Line
from detector.primitives.shape import Shape
from detector.primitives.shape_type import ShapeType
from detector.util import log
from detector.converter.diagram_converter import DiagramConverter
from detector.primitives.generic_entity import GenericEntity


class ClassDiagramTypes:
    CLASS_ENTITY = 0
    ASSOCIATION_ENTITY = 1
    ASSOCIATION_ENTITY_ADVANCED = 2

    ASSOCIATION_LINE = 3
    ASSOCIATION_SYMBOL = 4


class ClassDiagramConverter(DiagramConverter):
    CONVERTER_TYPE = "class_diagram"

    MIN_AREA_CLASS_RECTANGLES = 50
    """ Defines the minimum area a rectangle needs to have in order to be noticed as part of a class"""

    STR_ASSOC_FROM = "ASSOCIATION_FROM"
    STR_ASSOC_TO = "ASSOCIATION_TO"
    STR_ASSOC_PART = "ASSOCIATION_PART"
    STR_CLASS_NAME = "CLASS_NAME"

    def convert(self):
        log("transform to class primitives")
        self.generic_entities = self.generic_entities + self._extract_classes()
        self.generic_entities = self.generic_entities + self._extract_associations()
        self._join_lines_with_association_symbols()
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
            v = [v for k,v in enumerate(v) if util.area_contour(v) > ClassDiagramConverter.MIN_AREA_CLASS_RECTANGLES]
            contour_groups = util.group_contours_by_x_pos(v)

            for group_key, group_value in contour_groups.items():
                # Create class entities
                if len(group_value) == 3:
                    new_class = GenericEntity(ClassDiagramTypes.CLASS_ENTITY)
                    new_class.set(constants.STR_GENERIC_ENTITY_LABEL_NAME, f"Class {class_counter}")

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
        img = util.remove_generic_entities_in_image(img, advanced_associations, ClassDiagramTypes.ASSOCIATION_SYMBOL, preprocess=False)
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
        shapes, _, _ = self.shape_detector.find_shapes_in_image(image)
        for shape in shapes:
            if shape.shape is ShapeType.TRIANGLE or shape.shape is ShapeType.RECTANGLE:
                log(f"Advanced association found: {shape}")
                assoc = GenericEntity(ClassDiagramTypes.ASSOCIATION_SYMBOL)
                assoc.add_shape(shape)
                found_associations.append(assoc)

        log(f"{len(found_associations)} advanced associations found")
        return found_associations

    def _join_lines_with_association_symbols(self):
        """
        Joins the found lines with the advanced association shapes, such as inheritance, aggregation and so on.
        :return:
        """
        lines_entities = self.get_generic_entities(types=[ClassDiagramTypes.ASSOCIATION_ENTITY])
        symbol_entities = self.get_generic_entities(types=[ClassDiagramTypes.ASSOCIATION_SYMBOL])

        for l in lines_entities:
            line = l.shapes[0]  # GenericEntity of type ASSOCIATION_ENTITY always has just one shape, which is a Line
            line_start = line.start_xy()
            line_end = line.end_xy()

            for s in symbol_entities:
                symbol_bb = s.bounding_box()

                if util.is_point_in_area(line_start, symbol_bb) or util.is_point_in_area(line_end, symbol_bb):
                    s = s.shapes[0]    # TODO: Don't assume we have only one shape!
                    l.add_shape(s)

                    if s.shape is ShapeType.TRIANGLE:
                        l.set(constants.STR_GENERIC_ENTITY_LABEL_NAME, "Inheritance")
                    elif s.shape is ShapeType.RECTANGLE:
                        l.set(constants.STR_GENERIC_ENTITY_LABEL_NAME, "Aggregation")

                    l.type = ClassDiagramTypes.ASSOCIATION_ENTITY_ADVANCED # Change type from simple to advanced association
                    log("Association line was joined with symbol")

    def _link_associations_with_classes(self):
        """
        Links the found classes and associations with each other.
        """
        log(f"Try linking classes with associations")
        class_entities = self.get_generic_entities(types=[ClassDiagramTypes.CLASS_ENTITY])
        assoc_entities = self.get_generic_entities(types=[ClassDiagramTypes.ASSOCIATION_ENTITY])
        advanced_entities = self.get_generic_entities(types=[ClassDiagramTypes.ASSOCIATION_ENTITY_ADVANCED])

        # Link class entities with remaining associations
        for c in class_entities:
            class_bounding_box = c.bounding_box(adjustment=constants.BOUNDING_BOX_ADJUSTMENT)

            # ... with advanced associations
            for a in advanced_entities:
                for advanced_shape in a.shapes:
                    if type(advanced_shape) is Shape:
                        advanced_bounding_box = advanced_shape.bounding_box()

                        if util.do_bounding_boxes_intersect(advanced_bounding_box, class_bounding_box) or util.do_bounding_boxes_intersect(class_bounding_box, advanced_bounding_box):
                            a.set(ClassDiagramConverter.STR_ASSOC_FROM, c)

                    elif type(advanced_shape) is Line:
                        line_start = advanced_shape.start_xy()
                        line_end = advanced_shape.end_xy()

                        if util.is_point_in_area(line_start, class_bounding_box) or util.is_point_in_area(line_end, class_bounding_box):
                            a.set(ClassDiagramConverter.STR_ASSOC_TO, c)

            # ... with simple associations
            for a in assoc_entities:
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
