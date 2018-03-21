import os
import argparse
from detector import util, draw_util
from detector.detector import *
from detector.export.basic_shape_image_exporter import BasicShapeImageExporter

ap = argparse.ArgumentParser()


if __name__ == '__main__':
    ap.add_argument("-i", "--image", required=True, help="Path to the image you want to detect")
    ap.add_argument("-s", "--save", required=False, help="Path the result will be saved at")
    args = vars(ap.parse_args())

    img_path = args["image"]
    output_path = args["save"]

    print(img_path)
    if os.path.isfile(img_path):
        shape_detector = ShapeDetector(img_path)
        shapes = shape_detector.find_shapes()

        # Print shapes
        for s in shapes:
            util.log(f"\t{s}")

        exporter = BasicShapeImageExporter(shape_detector.image, shape_detector)
        img = exporter.export()

        util.save_image(img, output_path)

    else:
        raise ValueError("Image doesn't exist")
