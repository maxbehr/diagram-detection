import cv2

from detector import util
from detector.constants import constants
from detector.primitives.line import Line
from detector.primitives.shape import Shape


def draw_line(image, l, color=constants.COLOR_RED):
    image = image.copy()
    start = l.start_xy()
    end = l.end_xy()
    cv2.line(image, start, end, color, 2)
    return image


def draw_text(image, text, pos, size=0.4, color=(0,0,0), thickness=1):
    """
    Creates a copy of the given image and draws text on it.
    Wraps the OpenCV putText method.
    :param image: Image the text is drawn onto
    :param text: Text you want to draw
    :param pos: xy-Coordinates as tuple the text will be drawn at
    :param size: Size of the text, default: 0.5
    :param color: Color of the text, default: (0,0,0)
    :param thickness: Thickness of the text, default: 1
    :return: Copy of the given image with the text drawn onto.
    """
    image = image.copy()
    cv2.putText(image, text, pos, cv2.FONT_HERSHEY_SIMPLEX, size, color, thickness, cv2.LINE_AA)
    return image


def draw_rectangle(image, p1, p2, color=(0, 0, 255), thickness=2):
    """
    Creates a copy of the given image and draws a rectangle on it.
    Wraps the OpenCV rectangle method.
    :param image: Image the rectangle is drawn onto
    :param p1: (x, y) tuple of the first point of the rectangle
    :param p2: (x, y) tuple of the second point of the rectangle
    :param color: Color of the rectangle
    :param thickness: Thickness of the rectangle
    :return: Copy of the given image with the rectangle drawn onto.
    """
    image = image.copy()
    cv2.rectangle(image, p1, p2, color, thickness)
    return image


def draw_shapes_on_image(image, shapes):
    """
    Draws the given shapes on the given image and returns it.
    :param shapes: Shapes you want to draw.
    :param image: Image the shapes are drawn onto.
    :return: A copy of the image with the shapes drawn onto.
    """
    image = image.copy()
    contours = [s.contour for s in shapes]
    image = draw_contours_on_image(contours, image)
    return image


def draw_contours_on_image(contours, image, color=(0, 255, 0)):
    """
    Draws the given contours onto the given image,
    :param contours: Contours that are drawn.
    :param image: The image the contours are being drawn onto.
    :return:
    """
    image = image.copy()
    util.log(f"Draw {len(contours)} contours")
    cv2.drawContours(image, contours, -1, color, 2)
    return image


def draw_labeled_contours(contours, hierachy, image, color=(0, 0, 255)):
    # Draw contours
    draw_contours_on_image(contours, image, color)
    image = image.copy()

    # Draw shape names beside contour
    for i, c in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(c)
        shape_name = detect_shape(c)
        parent_id = hierachy[0][i][3]
        txt = f"{ShapeType.to_s(shape_name)} ({parent_id})"
        cv2.putText(image, txt, (int(x+w/2), int(y+h/2)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
    return image


def draw_labeled_lines(image, lines, color=(0, 0, 255), line_width=2, draw_lines=True, draw_labels=True):
    """
    Draws the given lines onto the given image. Labels them as well.
    :param image: Image you want the lines to be drawn on
    :param lines: Lines that will be drawn
    :param color: The color the drawn lines and labels will have
    :param line_width: Width of the lines
    :param toggle_line_drawing: Defines if the lines will be drawn (true => draw lines, false => draw no lines)
    :param toggle_label_drawing: Defines if the labels will be drawn (true => draw labels, false => draw no labels)
    :return:
    """
    image = image.copy()
    for i,l in enumerate(lines):
        start = l.start_xy()
        end = l.end_xy()

        if draw_lines:
            cv2.line(image, start, end, color, line_width)

        if draw_labels:
            x = int(start[0])
            y = int(start[1])
            cv2.putText(image, str(i), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)

    return image


def draw_entities_on_image(image, generic_entities, color=constants.COLOR_BLUE):
    """
    Draws the contours of all contained shapes of the given generic entities.
    :param image: The image the contours will be drawn on
    :param generic_entities: The generic entities we extract the shapes and its contours from
    :return: A copy of the image that contains the drawn contours.
    """
    image = image.copy()
    for e in generic_entities:
        for s in e.shapes:
            if type(s) is Shape:
                image = draw_contours_on_image([s.contour], image, color=color)
            elif type(s) is Line:
                image = draw_line(image, s, color=color)

    return image


def draw_labels(image, generic_entities, adjustment=constants.DRAWN_BOUNDING_BOX_ADJUSTMENT):
    """
    Draws the entity names of the generic entities onto the image.
    :param image: The image you want to draw the text on
    :param generic_entities: The generic entities you want the names to be drawn of
    :param adjustment: Bounding Box adjustment
    :return: A copy of the given image that contains the drawn labels
    """
    image = image.copy()
    for e in generic_entities:
        bb_x, bb_y, bb_w, bb_h = e.bounding_box(adjustment=adjustment)
        for s in e.shapes:
            name = "" if not e.get(constants.STR_GENERIC_ENTITY_LABEL_NAME) else e.get(
                constants.STR_GENERIC_ENTITY_LABEL_NAME)
            image = draw_text(image, f"{name}", (bb_x, bb_y - 5))
    return image


def draw_bounding_boxes(image, generic_entities, adjustment=constants.DRAWN_BOUNDING_BOX_ADJUSTMENT, color=constants.COLOR_BLUE, labels=False):
    """
    Draws the bounding boxes of the given entities.
    :param image: The image the bounding boxes are drawn on
    :param generic_entities: The entities you want the bounding boxes to be drawn of. Only entities from type Shape are considered
    :param adjustment: Will be applied to the bounding box size. Can be used to make the drawn bounding box smaller or bigger
    :param labels: Boolean that defines if labels should be drawn (True), or not (False)
    :return: A copy of the given image that contains the drawn bounding boxes
    """
    image = image.copy()

    for e in generic_entities:
        for s in e.shapes:
            if type(s) is Shape:
                bb_x, bb_y, bb_w, bb_h = e.bounding_box(adjustment=adjustment)
                image = draw_rectangle(image, (bb_x, bb_y), (bb_x + bb_w, bb_y + bb_h), color=color)

                if labels:
                    name = "" if not e.get(constants.STR_GENERIC_ENTITY_LABEL_NAME) else e.get(constants.STR_GENERIC_ENTITY_LABEL_NAME)
                    image = draw_text(image, f"{name}", (bb_x, bb_y - 5))

            elif type(s) is Line:
                image = draw_line(image, s, color)

    return image


def draw(image, generic_entities, draw_label=True, draw_bounding_box=True, draw_contour=False):
    """
    Generic draw method to draw labels, bounding boxes and the contours of the given entities.
    :param image: The image everything is drawn on.
    :param generic_entities: The entities
    :param draw_label: Defines whether labels are being drawn
    :param draw_bounding_box: Defines whether the bounding boxes of the entities are being drawn
    :param draw_contour: Defines whether the contours of the entitites are being drawn
    :return: A copy of the given image that everything is drawn of
    """
    image = image.copy()

    if draw_label:
        image = draw_labels(image, generic_entities)

    if draw_bounding_box:
        image = draw_bounding_boxes(image, generic_entities)

    if draw_contour:
        image = draw_entities_on_image(image, generic_entities)

    return image
