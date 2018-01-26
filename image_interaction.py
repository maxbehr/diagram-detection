from detector import util
from detector.detector import *
from detector.util import log


# Press R for Reset
# Press B for binary image
# Press I for inverted image
# Press E for erosion
# Press D for dilation
# Press C for Canny Edge
# Press H for Hough Lines
# Press P for HoughP Lines
def image_interaction(ch, image, img_path):
    # C - Canny Edge
    if ch == 99:
        image = util.create_canny_edge_image(image)

    # D - Dilate
    if ch == 100:
        log("Dilate")
        image = util.dilate(image)

    # E - Erode
    if ch == 101:
        log("Erode")
        image = util.erode(image)

    # C - Find Classes
    if ch == 97:
        shape_detector = ShapeDetector(img_path)
        shapes = shape_detector.find_shapes()
        diagram_converter = DiagramTypeDetector.find_converter(shape_detector)
        entities = diagram_converter._extract_classes()
        image = util.draw_entities_on_image(entities, image)
        log(f"{len(shapes)} shapes in image found")

    # S - Extract Shapes
    if ch == 115:
        shape_detector = ShapeDetector(img_path)
        shapes = shape_detector.find_shapes()
        shape_detector.save_found_shapes()
        log(f"{len(shapes)} shapes in image found")
        for s in shapes:
            util.print_contour_details(s.contour)

    # B - Binary
    if ch == 98:
        image = util.create_binary_img(image)

    # I - Inverted
    if ch == 105:
        image = util.create_inverted_image(image)

    # R - Reset
    if ch == 114:
        shape_detector = ShapeDetector(img_path)
        image = shape_detector.image
        original = image.copy()

    return image