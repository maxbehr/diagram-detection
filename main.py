import argparse
import cv2
from detector.detector import *
from detector import util
from detector.shape_type import ShapeType
from detector.util import log
import numpy as np

ap = argparse.ArgumentParser()
output_file = "./output/found_shapes.xml"

if __name__ == '__main__':

    #img_path = "img/class_pencil.jpeg"
    #img_path = "img/class.jpeg"
    #img_path = "img/class_many.jpeg"
    img_path = "img/class2.jpeg"
    #img_path = "img/usecase.jpeg"
    #img_path = "img/circles.jpeg"
    #img_path = "img/ocr_test.jpeg"
    #img_path = "img/ocr_test2.jpeg"

    # ap.add_argument("-i", "--image", required=True, help="Path to the image you want to detect")
    # args = vars(ap.parse_args())
    # print(args["image"])

    #   Detect all shapes
    shape_detector = ShapeDetector(img_path)
    shapes = shape_detector.find_shapes()
    log(f"{len(shapes)} shapes in image found")

    #   Detect type of diagram
    diagram_converter = DiagramTypeDetector.find_converter(shape_detector)

    #   Convert shapes into diagram
    entities = diagram_converter.extract_classes()

    contours = [c.get("name_contour") for c in entities] +\
               [c.get("attribute_contour") for c in entities] +\
               [c.get("method_contour") for c in entities]

    #img = shape_detector.get_image_remove_shape_type(ShapeType.RECTANGLE)

    # Draw class contours
    util.draw_class_entities_on_img(entities, shape_detector.image)

    # Label contours
    util.label_contours_in_image(shape_detector.contours, shape_detector.image)

    # Open result in window
    cv2.namedWindow("Image", cv2.WINDOW_AUTOSIZE)
    cv2.imshow("Image", shape_detector.image)
    cv2.waitKey()
    cv2.destroyAllWindows()
