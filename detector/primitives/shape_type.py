class ShapeType:
    UNIDENTIFIED = 0
    TRIANGLE = 1
    SQUARE = 2
    RECTANGLE = 3
    PENTAGON = 4
    HEXAGON = 5
    HEPTAGON = 6
    OCTAGON = 7
    CIRCLE = 8

    @staticmethod
    def to_s(shape_type):
        names = {
            0: "unidentified",
            1: 'triangle',
            2: 'square',
            3: 'rectangle',
            4: 'pentagon',
            5: 'hexagon',
            6: 'heptagon',
            7: 'octagon',
            8: 'circle'
        }

        return names[shape_type]
