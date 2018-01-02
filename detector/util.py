import cv2
import os
from detector.shape_type import ShapeType
import pytesseract
from PIL import Image

# Defines the accuracy for contour detection
EPSILON_FACTOR = 0.04


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

    print("shape: {shape}, sides: {sides}, ratio: {ratio}, w: {w}, h: {h}, area: {area}".format(
        shape=shape,
        sides=sides,
        ratio=aspect_ratio(c),
        w=w,
        h=h,
        area=area_contour(c)
    ))


def print_image_details(image):
    """
    Prints some information for the given image.
    :param self:
    :param image:
    """

    height, width = image_area(image)
    print("Image - width: {w}, height: {h}, area: {area}".format(w=width, h=height, area=(width * height)))


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


def save_image(image, filename):
    """
    Saves the given image to the disk.
    :param filename: Name of the saved file.
    :return:
    """
    cv2.imwrite(filename, image)


def ocr(image):
    if os.path.isfile(image):
        text = pytesseract.image_to_string(Image.open(image))
        print("OCR: {text}".format(text=text))
    else:
        print("shape ocr: File doesn't exist")


def crop_area(x, y, w, h, image):
    """
    Crops the given area from the given image and returns the pixel data for the cropped area.
    :param area: Area as tuple (x, y, w, h)
    :param image: Image we want to crop the area from
    :return: Array with the pixel data of the cropped area
    """
    return image[y:y+h, x:x+w]


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

    print("Draw "+ str(len(contours)) +" contours")
    cv2.drawContours(image, contours, -1, (0, 255, 0), 2)
