import os
import argparse
from detector import util, draw_util
from detector.constants import options as options
from detector.detector import *
from detector.export.class_diagram_image_exporter import ClassDiagramImageExporter

ap = argparse.ArgumentParser()


def init_args():
    ap.add_argument("-i", "--image", required=True, help="Path to the image you want to detect")
    ap.add_argument("-s", "--save", required=False, help="Path the result will be saved at")
    ap.add_argument("-v", "--verbose", required=False, help="Prints details about the detection")
    ap.add_argument("-o", "--ocr", required=False, help="Enables the Optical Character Recognition",
                    nargs='?', const=True, type=bool, default=options.DEFAULT_OCR)

    ap.add_argument("-e", "--epsilon", required=False, help="Defines the value (epsilon) that is used to approximate contours.",
                    nargs='?', const=options.DEFAULT_CONTOUR_EPSILON, type=float, default=options.DEFAULT_CONTOUR_EPSILON)

    ap.add_argument("-l", "--lines", required=False, help="Set this parameter in order to toggle the line detection. Defaults to False.",
                    nargs='?', const=options.DEFAULT_LINE_DETECTION, type=bool, default=options.DEFAULT_LINE_DETECTION)


if __name__ == '__main__':
    init_args()
    args = vars(ap.parse_args())

    img_path = args["image"]
    output_path = args["save"]

    print(img_path)
    if os.path.isfile(img_path):
        opts = {
            'ocr': args['ocr'],
            'contour_epsilon': args['epsilon']
        }
        util.log(f"Passed options: {str(opts)}")

        shape_detector = ShapeDetector(img_path, opts)
        shapes = shape_detector.find_shapes()

        img = shape_detector.image

        if args['lines']:
            line_detector = LineDetector()
            line_detector.init(shape_detector.preprocessed_image)
            lines = line_detector.find_lines()
            img = draw_util.draw_labeled_lines(img, lines)

        # Print shapes
        for s in shapes:
            util.log(f"\t{s}")

        diagram_converter = DiagramTypeDetector.find_converter(shape_detector)
        diagram_converter.convert()

        classDiagramImageExporter = ClassDiagramImageExporter(img, diagram_converter, opts)
        img = classDiagramImageExporter.export()

        if output_path is not None:
            util.save_image(img, output_path)
    else:
        raise ValueError("Image doesn't exist")