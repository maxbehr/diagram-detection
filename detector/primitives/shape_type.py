class ShapeType:
    UNIDENTIFIED = 0
    TRIANGLE = 1
    SQUARE = 2
    RECTANGLE = 3
    PENTAGON = 4
    CIRCLE = 5

    @staticmethod
    def to_s(shape_type):
        names = {
            0: "unidentified",
            1: 'triangle',
            2: 'square',
            3: 'rectangle',
            4: 'pentagon',
            5: 'circle'
        }

        return names[shape_type]
