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
    ap.add_argument("-c", "--custom", required=False,
                    help="Set this parameter in order to define how the detection should be handled. If not -c is not"
                         " set, diagram detection takes place.", action="store_true")

    ap.add_argument("-o", "--ocr", required=False, help="Enables the Optical Character Recognition",
                    action="store_true")

    ap.add_argument("-e", "--epsilon", required=False,
                    help="Defines the value (epsilon) that is used to approximate contours.", nargs='?',
                    const=options.DEFAULT_CONTOUR_EPSILON, type=float, default=options.DEFAULT_CONTOUR_EPSILON)

    ap.add_argument("-dl", "--lines", required=False, help="Set this parameter in order to toggle the line detection.",
                    action="store_true")

    ap.add_argument("-ds", "--shapes", required=False, help="Set this parameter in order to toggle the shape detection.",
                    action="store_true")


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
        img = shape_detector.image

        if not args['custom']:  # Start default diagram detection
            shapes = shape_detector.find_shapes()

            # Print shapes
            for s in shapes:
                util.log(f"\t{s}")

            diagram_converter = DiagramTypeDetector.find_converter(shape_detector)
            diagram_converter.convert()

            classDiagramImageExporter = ClassDiagramImageExporter(img, diagram_converter, opts)
            img = classDiagramImageExporter.export()

        else:  # custom behaviour
            if args['shapes']:
                shapes = shape_detector.find_shapes()
                img = draw_util.draw_shapes_on_image(img, shapes)

            if args['lines']:
                line_detector = LineDetector()
                line_detector.init(shape_detector.preprocessed_image)
                line_detector.find_lines()
                lines = line_detector.merge_lines()

                img = draw_util.draw_labeled_lines(img, lines, draw_labels=False)

        if output_path is not None:
            util.save_image(img, output_path)

    else:
        raise ValueError("Image doesn't exist")
