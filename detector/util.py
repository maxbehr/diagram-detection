import cv2
import imutils
import os
import time

from detector.primitives.shape_type import ShapeType
import pytesseract
from PIL import Image
import numpy as np
import math

EPSILON_FACTOR = 0.04
""" Defines the accuracy for contour detection """

OUTPUT_PATH = "output/"
""" Defines the path images will be saved to """

EROSION_BY = 5
""" Amount pixel that are applied to bounding box of a contour when removing contours from image. Default is 5. """

CONTOUR_REMOVAL_COLOR = (0,0,0)
""" Color that is used to remove shapes and contours. Default is white (255, 255, 255). """

def aspect_ratio(c):
    """
    Calculates the aspect ratio of the given contour.
    :param c:
    :return: The aspect ratio.
    """
    x, y, w, h = cv2.boundingRect(c)
    return float(w) / h


def image_area(image):
    return image.shape[:2]


def area_contour(c):
    """
    Calculates the area of the given contour.
    :param c:
    :return: The area as floati
    """
    x, y, w, h = cv2.boundingRect(c)
    return w * h


def print_contour_details(c):
    log(get_contour_details(c))


def get_contour_details(c):
    """
    Prints some detailed information of the given contour.

    :param c: Countour you want some details of.
    """
    x, y, w, h = cv2.boundingRect(c)

    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, EPSILON_FACTOR * peri, True)
    sides = len(approx)

    shape_type = detect_shape(c)
    shape = ShapeType.to_s(shape_type=shape_type)

    return f"Contour - shape: {shape}, sides: {sides}, ratio: {aspect_ratio(c)}, x: {x}, y: {y}, w: {w}, h: {h}, area: {area_contour(c)}"


def print_image_details(image):
    """
    Prints some information for the given image.
    :param self:
    :param image:
    """

    height, width = image_area(image)
    log(f"Image - width: {width}, height: {height}, area: {width*height}")


def detect_contours(image):
    """
    Detects the contours of the given image.
    :param image: Image you want the contours of
    :return: A tuple containg (img, contours, hierarchy)
    """
    #   cv2.RETR_TREE --> Relationships between contours
    #   cv2.RETR_EXTERNAL --> Ohne doppelte Konturen
    return cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)


def detect_shape(c):
    """
    Identifies the given contour as shape.
    :param c:
    :return: The shape of type Shape
    """
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, EPSILON_FACTOR * peri, True)

    if len(approx) == 3:
        return ShapeType.TRIANGLE

    if len(approx) == 4:
        (x, y, w, h) = cv2.boundingRect(approx)
        ratio = w / float(h)

        if 0.9 <= ratio <= 1.1:
            return ShapeType.SQUARE
        else:
            return ShapeType.RECTANGLE

    if len(approx) == 5:
        return ShapeType.PENTAGON

    if len(approx) >= 6:
        return ShapeType.CIRCLE

    return ShapeType.UNIDENTIFIED


def label_entities_in_image(entities, image):
    """
    Labels shapes that are contained in the given generic entitites. The added text contains the detected shape names.
    :param entities: Generic entities that contain the shapes you want to label
    :param image: The image the labels will be placed on
    :return: An copy of the given image with the added labels
    """
    image = image.copy()
    for e in entities:
        for s in e.shapes:
            text = ShapeType.to_s(s.shape)
            put_text_in_img(image, text, int(s.x), int(s.y))
    return image


def label_contours_in_image(contours, image):
    """
    Labels the given contours in the given image. Puts their indices as text onto the image.
    :param contours: Contours we want to label
    :param image: Image we want the labels to be added to
    """
    image = image.copy()
    for i, c in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(c)
        put_text_in_img(image, str(i), int(x+w/2), int(y+h/2))
    return image


def put_text_in_img(image, text, x, y, size=0.5, color=(0,0,0), thickness=1):
    """
    Puts the given text on the given image for the given x- and y-coordinate.
    :param image: Image the text is put on
    :param text: The text that will be drawn
    :param x: x coordinate of the text
    :param y: y coordinate of the text
    :param size: the font size
    :param color: the font color
    :param thickness: the font thickness
    :return:
    """
    cv2.putText(image, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, size, color, thickness, cv2.LINE_AA)


def save_image(image, filename):
    """
    Saves the given image to the disk.
    :param filename: Name of the saved file.
    :return:
    """
    cv2.imwrite(f"{OUTPUT_PATH}{filename}", image)


def ocr(image):
    if os.path.isfile(image):
        text = pytesseract.image_to_string(Image.open(image))
        log("Found OCR text: {text}".format(text=text))
        return text
    else:
        log("Shape::OCR: File doesn't exist")


def crop_area(x, y, w, h, image):
    """
    Crops the given area from the given image and returns the pixel data for the cropped area.
    :param area: Area as tuple (x, y, w, h)
    :param image: Image we want to crop the area from
    :return: Array with the pixel data of the cropped area
    """
    return image[y:y+h, x:x+w]


def crop_shapes_and_save_as_files(image, shapes):
    """
    Crops out all given shapes in the given image and saves them as separate image files.
    :param image: The image we want to crop out the shapes.
    :param shapes: The shapes we want to crop.
    """
    log(f"Crop {len(shapes)} shapes in image")

    for (i, shape) in enumerate(shapes):
        if shape.shape is not ShapeType.UNIDENTIFIED:
            (x, y, w, h) = shape.bounding_rect()
            cropped_image = crop_area(x, y, w, h, image)
            filename = "output/cropped_{i}.png".format(i=i)
            save_image(cropped_image, filename)


def create_shape_hierarchy(image):
    """
    Creates a dict, that resembles the hierarchy of the contours. As index there are all parent contours, children are
    all children contours of the parent contours.
    :param image: Image you want the contours from.
    :return: dict that contains the contour hierarchy
    """

    _, cnts, hierachy = detect_contours(image)
    #for c in zip(cnts, hierachy):

    contour_map = {}
    for h in hierachy[0]:
        parent_id = h[3]
        first_child_id = h[2]

        # Store only contours with a parent
        if parent_id > -1:
            if parent_id in contour_map:
                contour_map[parent_id].append(h)
            else:
                contour_arr = []
                contour_arr.append(h)
                contour_map[parent_id] = contour_arr

    return contour_map, cnts


def create_working_copy_of_image(image):
    """
    Creates a resized copy of the given image.
    :param image: Image the copy is created from.
    :return: Returns the resized image
    """
    return imutils.resize(image, width=700)


def preprocess_image(image):
    """
    Preprocesses the image in order to properly detect shapes. Applies gaussian blur, converts the color to b/w and
    creates a binary image from it, that is returned.
    :param image: Image that is gonna be preprocessed
    :return: Binary image of the given image.
    """

    # Blur image
    image = cv2.GaussianBlur(image, (5,5), 0)

    # Grayscale image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #cv2.imshow("gray", image)

    # Threshold image
    _, image = cv2.threshold(image, 135, 255, cv2.THRESH_BINARY_INV)
    #image = cv2.dilate(image, (15, 15), iterations=3)
    #cv2.imshow("thresh", image)

    return image


def create_binary_img(img):
    """
    Converts the given image into a binary image.
    :param img: Image you want to convert
    :return: Binary image of the given image
    """
    image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, image = cv2.threshold(img, 135, 255, cv2.THRESH_BINARY_INV)
    return image


def has_contour_children(contour_index, hierarchy):
    """
    Checks if the given index appears as parent_index in the given hierarchy.

    :param contour_index: Index of the contour we want to check, whether it has some children.
    :param hierarchy: Hierarchy, we want to check the given contour_index
    :return: True if given contour has children, False otherwise
    """
    all_parent_ids = [hierarchy[i][3] for i, v in enumerate(hierarchy)]
    return contour_index in all_parent_ids[0]


def get_contour_children_for(contour_index, hierarchy):
    """
    Returns the hierachy data of all child contours of the given contour_index from the given hierarchy.
    :param contour_index: Index of the contour we want to have all children returned.
    :param hierarchy: Hierarchy we want to check against.
    :return: List of the hierarchy data of all children
    """
    children = {}
    for i, h in enumerate(hierarchy[0]):
        if contour_index == h[3]:   # index 3 represents parent contour
            key = str(i)
            children[key] = h

    return children


def get_sorted_contours_for_hierachy_entries(contours, hierarchy_entries, sort_method="top-to-bottom"):
    """
    For all given hierarchy entries (data from the hierarchy list for a contour), give the correct contour in the given
    contours list. Sort and return them afterwards. Only as many contours are returned as hierarchy entries in the
    given list exist.
    :param contours: List of all contours
    :param hierarchy_entries: Dict that contains all the entries
                    key: index of the contour inside the contours list
                    value: hierarchy information of the contour
    :param sort_method: Defines how we want the contours to be returned, default: "top-to-bottom"
    :return: List of all sorted contours, that correspond to the given hierarchy dict
    """
    mixed = []

    for key, he in hierarchy_entries.items():
        mixed.append(contours[int(key)])

    mixed = imutils.contours.sort_contours(mixed, method=sort_method)[0]
    return mixed


def get_sorted_contours_by_parent(contours, hierarchy, discard_contours_without_parent=True):
    """
    Maps the given contours by their parent and groups them together.
    :param contours: Contours you want to sort
    :param hierarchy: Hierarchy of the contours
    :param discard_contours_without_parent: Defines if contours without parent (-1) are dropped
                true    => skip those contours
                false   => keep those contours
    :return: Dictionary that contains the parent ids as key and their contours as list
    """
    sorted_contours = {}
    for i, hierarchy_entry in enumerate(hierarchy[0]):
        contour = contours[i]
        parent_id = hierarchy_entry[3]

        if discard_contours_without_parent and parent_id == -1:
            pass
        else:
            if parent_id not in sorted_contours:
                sorted_contours[parent_id] = []
            sorted_contours[parent_id].append(contour)

    return sorted_contours


def group_contours_by_x_pos(contours):
    """
    Keys will be the first x value that was found for a group. Values of each key will be the contours that are within
    the tolerance of the x value (respectively the key).
    :param contours:
    :return:
    """
    tolerance = 10
    group = {}
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)

        was_added = False
        for key in group.keys():
            if (int(key) - tolerance) <= x <= (int(key) + tolerance):
                group[key].append(c)
                was_added = True
                break

        if not was_added:
            if x not in group:
                group[x] = []
            group[x].append(c)

    return group


def create_canny_edge_image(image, min=100, max=200):
    """
    Applies the canny edge detection to the given image.
    :param image: The image you want the edges of
    :param min:  
    :param max:
    :return: the canny edge image
    """
    return cv2.Canny(image, min, max)


def erode(image, kernel=np.ones((5,5), np.uint8), iterations=1):
    """
    Erodes (removes pixel) to the given image.
    :param image: The image you want to erode
    :param kernel: The kernel size, default: 5x5
    :param iterations: The amount how many time the image will be eroded
    :return: The eroded image
    """
    return cv2.erode(image, kernel, iterations)


def dilate(image, kernel=np.ones((5,5), np.uint8), iterations=1):
    """
    Dilates (adds pixel) to the given image.
    :param image: The image you want to dilate
    :param kernel: The kernel size, default: 5x5
    :param iterations: The amount how many time the image will be dilated
    :return: The dilated image
    """
    return cv2.dilate(image, kernel, iterations)


def remove_generic_entities_in_image(image, generic_entities, type=None, preprocess=True):
    """
    Removes the given generic entities from the image. Uses the contours of the contained shapes in a generic entity.
    The generic entities that you want to be removed can be filtered by a type. If no type is given, all generic
    entities will be removed.
    :param image: Original image (not modified) you want the generic entities removed from
    :param generic_entities: List of generic entities
    :param type: The type of the generic entities you want to remove (None if you want to remove all)
    :return: The image with the generic entitites removed
    """
    image = image.copy()

    if preprocess:
        image = preprocess_image(image)

    if type is not None:
        generic_entities = filter(lambda x: x.type == type, generic_entities)

    for e in generic_entities:
        contours = [s.contour for s in e.shapes]
        image = remove_contours_in_image(image, contours)

    return image


def remove_contours_in_image(image, contours):
    """
    Places white rectangles over the given contours in order to remove them from the given image. The white rectangles
    are drawn bigger than the contours themselves. The amount the drawn rectangle is bigger is defined by the
    EROSION_BY constant. Default is 5 pixel.
    :param image: Image the contours will be removed from
    :param contours: Contours that will be removed
    :return: The image with removed contours
    """
    image = image.copy()
    for c in contours:
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(image, (x-EROSION_BY, y-EROSION_BY), (x+w+EROSION_BY, y+h+EROSION_BY), CONTOUR_REMOVAL_COLOR, -1)
    return image


def create_inverted_image(image):
    """
    Creates an inverted image of the given one.
    :param image: The image you want to invert
    :return: the inverted image
    """
    return cv2.bitwise_not(image)


def distance_between(a, b):
    """
    Calculates the distance between the given points.
    :param a: Point A
    :param b: Point B
    :return: The distance between Point A and Point B
    """
    x1, y1 = a.get_xy_tuple()
    x2, y2 = b.get_xy_tuple()

    s1 = math.pow(x2 - x1, 2)
    s2 = math.pow(y2 - y1, 2)
    return math.sqrt(s1 + s2)


def angle_for_slopes(m1, m2):
    """
    Calculates the angle between two slopes.
    :param m1: Slope a
    :param m2: Slope b
    :return: Returns the angle in degrees
    """
    m1 = float(m1)
    m2 = float(m2)
    talpha = np.absolute((m1 - m2) / (1 + (m1 * m2)))
    return np.rad2deg(np.arctan(talpha))


def angle_between_lines(line_a, line_b):
    """
    Calculates the angle between the given two lines.
    :param line_a: Line a
    :param line_b: Line b
    :return: The angle in degrees
    """
    slope_a = line_a.slope()
    slope_b = line_b.slope()
    log(f"angle between line A and line B: {angle_for_slopes(slope_a, slope_b)}")
    return angle_for_slopes(slope_a, slope_b)


def is_point_in_area(p1, area):
    """
    Checks if the given area contains the given point.
    :param p1: Point as tuple (x, y)
    :param area: Area as tuple (x, y, w, h)
    :return: True if the area contains the point, False otherwise
    """
    px, py = p1
    ax, ay, aw, ah = area
    return ax <= px <= ax+aw and ay <= py <= ay+ah


def log(str):
    """
    Logs the given string to the console.
    :param str:
    :return:
    """
    t = time.strftime("%H:%M:%S")
    print(f"[{t}] {str}")

