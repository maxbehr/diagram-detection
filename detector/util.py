import cv2
import imutils
import os
import time
from detector.shape_type import ShapeType
import pytesseract
from PIL import Image
import numpy as np
import math

EPSILON_FACTOR = 0.04
""" Defines the accuracy for contour detection """

OUTPUT_PATH = "output/"
""" Defines the path images will be saved to """


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

    log(f"Contour - shape: {shape}, sides: {sides}, ratio: {aspect_ratio(c)}, x: {x}, y: {y}, w: {w}, h: {h}, area: {area_contour(c)}")


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


def label_contours_in_image(contours, image):
    """
    Labels the given contours in the given image. Puts their indices as text onto the image.
    :param contours: Contours we want to label
    :param image: Image we want the labels to be added to
    """
    image = image.copy()
    for i, c in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.putText(image, str(i), (int(x+w/2), int(y+h/2)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
    return image


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


def draw_contours_on_image(contours, image, color=(0, 255, 0)):
    """
    Draws the given contours onto the given image,
    :param contours: Contours that are drawn.
    :param image: The image the contours are being drawn onto.
    :return:
    """

    log(f"Draw {len(contours)} contours")
    cv2.drawContours(image, contours, -1, color, 2)


def draw_labeled_lines(image, lines, color=(0, 0, 255), toggle_line_drawing=True, toggle_label_drawing=True):
    """
    Draws the given lines onto the given image. Labels them as well.
    :param image: Image you want the lines to be drawn on
    :param lines: Lines that will be drawn
    :param color: The color the drawn lines and labels will have
    :param toggle_line_drawing: Defines if the lines will be drawn (true => draw lines, false => draw no lines)
    :param toggle_label_drawing: Defines if the labels will be drawn (true => draw labels, false => draw no labels)
    :return:
    """
    for i,l in enumerate(lines):
        start = l.start_xy()
        end = l.end_xy()

        if toggle_line_drawing:
            print(f"Draw line: {l}")
            cv2.line(image, start, end, color, 2)

        if toggle_label_drawing:
            x = int(start[0])
            y = int(start[1])
            cv2.putText(image, str(i), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)


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


def draw_class_entities_on_img(class_entities, img):
    """
    Draws the contours of the given generic entitites - in this case UML classes. Colours the different parts, such as
    name, attributes and methods differently. The contours will be drawn on the given image.
    :param class_entities: Class entities we want to draw contours of.
    :param img: The image the contours will be drawn on.
    :return:
    """
    img = img.copy()
    for e in class_entities:
        # Draw name contour
        name_contour = e.get("name_contour")
        print_contour_details(name_contour)
        draw_contours_on_image([name_contour], img, color=(255, 0, 0))

        # Draw attribute contour
        attribute_contour = e.get("attribute_contour")
        print_contour_details(attribute_contour)
        draw_contours_on_image([attribute_contour], img, color=(0, 0, 255))

        # Draw method contour
        method_contour = e.get("method_contour")
        print_contour_details(method_contour)
        draw_contours_on_image([method_contour], img)

    return img


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


def log(str):
    """
    Logs the given string to the console.
    :param str:
    :return:
    """
    t = time.strftime("%H:%M:%S")
    print(f"[{t}] {str}")

