"""
TODO description of pointing technique
Upon initialization the pointer gets the available circles.
Filter is called when the mouse is moved.
"""


class PointingTechnique:

    def __init__(self, available_circles):
        print(str(available_circles))

    def filter(self, current_position):
        print(current_position)
        # TODO get nearest circle
        # highlight the nearest circle
