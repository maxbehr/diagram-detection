from xml.etree import ElementTree
from xml.dom import minidom


class XMLWriter:

    def __init__(self, output_file):
        self.file = output_file

    def write(self, elem):
        """
        Writes the given shapes to the output file.
        :return:
        """
        print(self.prettify(elem))
        # file = open(self.file, "w")
        # file.write(self.prettify(elem))
        # file.close()

    def prettify(self, elem):
        """
        Takes the given element and returns it as a prettified XML.
        """
        ugly_xml = ElementTree.tostring(elem, 'utf-8')
        pretty_xml = minidom.parseString(ugly_xml)
        return pretty_xml.toprettyxml(indent="  ")
