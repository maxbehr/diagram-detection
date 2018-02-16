import cv2

from detector import util
from detector.primitives.line import Line
from detector.primitives.shape import Shape


def draw_contours_on_image(contours, image, color=(0, 255, 0)):
    """
    Draws the given contours onto the given image,
    :param contours: Contours that are drawn.
    :param image: The image the contours are being drawn onto.
    :return:
    """

    util.log(f"Draw {len(contours)} contours")
    cv2.drawContours(image, contours, -1, color, 2)


def draw_line(image, l, color=(0, 0, 255)):
    image = image.copy()
    start = l.start_xy()
    end = l.end_xy()
    print(f"Draw line: {l}")
    cv2.line(image, start, end, color, 2)
    return image


def draw_text(image, text, pos, size=0.5, color=(0,0,0), thickness=1):
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


def draw_shapes_on_image(shapes, image):
    """
    Draws the given shapes on the given image and returns it.
    :param shapes: Shapes you want to draw.
    :param image: Image the shapes are drawn onto.
    :return: A copy of the image with the shapes drawn onto.
    """
    image = image.copy()
    contours = [s.contour for s in shapes]
    draw_contours_on_image(contours, image)
    return image


def draw_contours_on_image(contours, image, color=(0, 255, 0)):
    """
    Draws the given contours onto the given image,
    :param contours: Contours that are drawn.
    :param image: The image the contours are being drawn onto.
    :return:
    """

    log(f"Draw {len(contours)} contours")
    cv2.drawContours(image, contours, -1, color, 2)


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
    image = image.copy()
    for i,l in enumerate(lines):
        start = l.start_xy()
        end = l.end_xy()

        if toggle_line_drawing:
            print(f"Draw line: {l}")
            cv2.line(image, start, end, color, 2)

        if toggle_label_drawing:
            x = int(start[0])
            y = int(start[1])
            cv2.putText(image, str(i), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)

    return image


def draw_entities_on_image(image, generic_entities):
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
                image = draw_contours_on_image([s.contour], image)
            elif type(s) is Line:
                image = draw_line(image, s)

    return image
