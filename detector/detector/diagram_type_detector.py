from detector.converter import *


class DiagramTypeDetector:
    CONVERTERS = [
        ClassDiagramConverter,
        UseCaseDiagramConverter
    ]

    @classmethod
    def find_converter(cls, shape_detector_obj):
        """
        Returns the converter that can be used for the shapes.
        :return:
        """
        for converter in cls.CONVERTERS:
            if converter.is_diagram(shape_detector_obj):
                return converter(shape_detector_obj)
