from detector.constants import constants
from detector import util, draw_util
from detector.export.exporter import Exporter
from detector.primitives.generic_entity import GenericEntity
from detector.util import log


class BasicShapeImageExporter(Exporter):
    EXPORTER_ID= "basic_shape_image_exporter"

    def export(self):
        log("Exporting image with labeled basic shapes")

        entities = []
        for s in self.shape_detector.get_shapes():
            if util.has_no_contour_children(s.contour_index, self.shape_detector.hierarchy):
                ge = GenericEntity()
                ge.add_shape(s)
                ge.set(constants.STR_GENERIC_ENTITY_LABEL_NAME, s.shape_name())
                entities.append(ge)

        self.image = draw_util.draw(self.image, entities)

        return self.image
