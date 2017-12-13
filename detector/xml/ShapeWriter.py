from detector.xml.XMLWriter import XMLWriter


class ShapeWriter:

    def __init__(self, shapes, output_file):
        self.shapes = shapes
        self.writer = XMLWriter(output_file)

    def _preprocess(self, shapes):
        """
        Creates for every given shape an XML element.
        :return:
        """
        self.xml_elements = shapes;
        return self.xml_elements

    def write(self, shapes):
        xml_elements = self._preprocess(shapes)

        """
        Writes all XML elements into a file using the XML writer.
        :param shapes: 
        :return: 
        """
        print("Write shapes")
