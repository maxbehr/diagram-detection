import cv2
import imutils
import numpy as np
import argparse
from detector.diagram_detector import DiagramDetector
from detector.xml.ShapeWriter import ShapeWriter

ap = argparse.ArgumentParser()
output_file = "./output/found_shapes.xml"

if __name__ == '__main__':
    img_path = "img/example3.jpg"

    # ap.add_argument("-i", "--image", required=True, help="Path to the image you want to detect")
    # args = vars(ap.parse_args())
    # print(args["image"])

    dd = DiagramDetector()
    dd.load(img_path)
    shapes, analyzed_image = dd.analyze()
    
    #dd.is_class_diagram()
    #dd.show_result()

    writer = ShapeWriter(shapes, output_file)
    writer.write(shapes)
