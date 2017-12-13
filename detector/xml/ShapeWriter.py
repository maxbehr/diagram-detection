from detector.xml.XMLWriter import XMLWriter
from xml.etree.ElementTree import Element, SubElement, Comment, tostring


class ShapeWriter:

    def __init__(self, shapes, output_file):
        self.shapes = shapes
        self.writer = XMLWriter(output_file)

    def _preprocess(self, shapes):
        """
        Creates for every given shape an XML element.
        :return:
        """
        # Add root element
        root = Element('root')
        root.append(
            Comment('Generated xml shapes')
        )

        # Add elements for each shape
        for shape in shapes:
            root.append(
                Comment('Generated shape: {name}'.format(name=shape.shape_name()))
            )

            child = SubElement(root, 'shape', { 'attr-1': 'attribute content' })
            child.set('attr-b', 'other attribute content')
            child.text = 'tag content'

        return root

    def write(self, shapes):
        """
        Writes all XML elements into a file using the XML writer.
        :param shapes:
        :return:
        """
        root = self._preprocess(shapes)
        self.writer.write(root)
