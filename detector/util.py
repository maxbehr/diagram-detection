import cv2
import imutils
import os
import time
from detector.shape_type import ShapeType
import pytesseract
from PIL import Image

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

    log(f"shape: {shape}, sides: {sides}, ratio: {aspect_ratio(c)}, w: {w}, h: {h}, area: {area_contour(c)}")


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
    return cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)


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
    for i, c in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.putText(image, str(i), (int(x+w/2), int(y+h/2)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)


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


def draw_contours_on_image(contours, image):
    """
    Draws the given contours onto the given image,
    :param contours: Contours that are drawn.
    :param image: The image the contours are being drawn onto.
    :return:
    """

    log(f"Draw {len(contours)} contours")
    cv2.drawContours(image, contours, -1, (0, 255, 0), 2)


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
    Returns all child contours of the given contour_index from the given hierarchy.
    :param contour_index: Index of the contour we want to have all children returned.
    :param hierarchy: Hierarchy we want to check against.
    :return: List of all children
    """
    children = []
    for h in hierarchy[0]:
        if contour_index == h[3]:
            children.append(h)

    return children


def log(str):
    """
    Logs the given string to the console.
    :param str:
    :return:
    """
    t = time.strftime("%H:%M:%S")
    print(f"[{t}] {str}")
