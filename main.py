import argparse
from detector.detector import *
from detector.util import *

ap = argparse.ArgumentParser()
output_file = "./output/found_shapes.xml"


#def nothing(arg):
#    print(arg)
#    pass

if __name__ == '__main__':

    #img_path = "img/class_pencil.jpeg"
    img_path = "img/class.jpeg"
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
    diagram_converter.transform_shapes_to_diagram()


    #dd = DiagramDetector()
    #dd.load(img_path)
    #shapes, analyzed_image = dd.analyze()

    #dd.is_class_diagram()
    #dd.show_result()

    #writer = ShapeWriter(shapes, output_file)
    #writer.write(shapes)

    # while True:
    #     cv2.namedWindow("Image", cv2.WINDOW_AUTOSIZE)
    #     #cv2.createTrackbar('Epsilon', 'Image', 1, 100, nothing)
    #
    #     cv2.imshow("Image", analyzed_image)
    #     ch = cv2.waitKey(5)
    #     if ch == 27:
    #         break;
    #
    # cv2.destroyAllWindows()

