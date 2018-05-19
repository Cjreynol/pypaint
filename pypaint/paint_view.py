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
        """
        Create the Tkinter window, then create and place the widgets in it.
        """
        self.root = self._create_root()
        self._initialize_widgets()
        self._place_widgets()

    def _create_root(self):
        """
        Return the root window with the proper attributes set.
        """
        root = Tk()
        root.title(self.WINDOW_TITLE)
        return root

    def _initialize_widgets(self):
        """
        Instantiate the widgets for the GUI.
        """
        self.canvas = Canvas(self.root, width = self.CANVAS_DIMENSION, 
                                height = self.CANVAS_DIMENSION)
        self.toggle_button = Button(self.root, text = self.BUTTON_TEXT)

    def _place_widgets(self):
        """
        Use a geometry manager to put the widgets in the root window.
        """
        self.canvas.pack()
        self.toggle_button.pack()

    def bind_canvas_callback(self, event_id, callback):
        """
        Register the callback for the given event.
        """
        self.canvas.bind(event_id, callback)

    def bind_toggle_callback(self, callback):
        """
        Set the button's command callback.
        """
        self.toggle_button["command"] = callback

    def bind_quit_callback(self, callback):
        """
        Set the callback for when the window closes.
        """
        self.root.protocol("WM_DELETE_WINDOW", callback)

    def start(self):
        """
        Start the GUI's update loop.
        """
        self.root.mainloop()

    def draw_shape(self, shape_type, coords):
        """
        Determine and call the appropriate drawing function based on the 
        shape type.
        """
        if shape_type == ShapeType.RECT:
            self.draw_rect(coords)
        elif shape_type == ShapeType.LINE:
            self.draw_line(coords)
        else:
            raise RuntimeError("Unexpected shape type {}".format(shape_type))

    def draw_rect(self, coords):
        """
        Draw a rectangle using the opposite corner pairs specified in coords.
        """
        return self.canvas.create_rectangle(*coords)

    def draw_line(self, coords):
        """
        Draw a line with the start/end pairs specified in coords.
        """
        return self.canvas.create_line(*coords, width = self.LINE_WIDTH, 
                                    capstyle = ROUND)

    def clear_drawing_by_id(self, drawing_id):
        """
        Delete the drawing with the given id from the canvas.
        """
        self.canvas.delete(drawing_id)
