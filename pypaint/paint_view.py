from tkinter import Button, Canvas, Tk, ALL, ROUND

from pypaint.shape_type import ShapeType


class PaintView:
    """
    Manages the Tkinter window and its widgets.
    """

    WINDOW_TITLE = "PyPaint"

    CANVAS_DIMENSION = 600
    BUTTON_TEXT = "Toggle"
    LINE_WIDTH = 5

    def __init__(self):
        self.root = None
        self.canvas = None
        self.toggle_button = None

    def _create_root(self):
        root = Tk()
        root.title(self.WINDOW_TITLE)
        return root

    def initialize(self):
        self.root = self._create_root()
        self._initialize_widgets()
        self._place_widgets()

    def _initialize_widgets(self):
        self.canvas = Canvas(self.root, width = self.CANVAS_DIMENSION, 
                                height = self.CANVAS_DIMENSION)
        self.toggle_button = Button(self.root, text = self.BUTTON_TEXT)

    def _place_widgets(self):
        self.canvas.pack()
        self.toggle_button.pack()

    def bind_canvas_callback(self, event_id, callback):
        self.canvas.bind(event_id, callback)

    def bind_toggle_callback(self, callback):
        self.toggle_button["command"] = callback

    def start(self):
        self.root.mainloop()

    def clear_draw_history(self, history):
        """
        Clear the canvas of all previous drawings, and then draw every item 
        in the history list.
        """
        self.canvas.delete(ALL)

        for shape_type, coords in history:
            if shape_type == ShapeType.RECT:
                self.draw_rect(coords)
            elif shape_type == ShapeType.LINE:
                self.draw_line(coords)
            else:
                raise RuntimeError("Unexpected shape type {}".format(shape_type))

    def draw_rect(self, coords):
        self.canvas.create_rectangle(*coords)

    def draw_line(self, coords):
        self.canvas.create_line(*coords, width = self.LINE_WIDTH, 
                                    capstyle = ROUND)
