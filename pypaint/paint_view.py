from time import sleep
from tkinter import (Button, Canvas, Frame, Label, Scale, Tk, 
                        ALL, BOTH, BOTTOM, HORIZONTAL, LEFT, RIGHT, ROUND, 
                        RAISED)

from pypaint.drawing_type import DrawingType


class PaintView:
    """
    Manages the Tkinter window for a PyPaint instance.
    """

    WINDOW_TITLE = "PyPaint"

    FRAME_BORDER_WIDTH = 2
    FRAME_WIDTH = 120
    TOOL_LABEL_TEXT = "Current Tool:\n"

    THICKNESS_LABEL_TEXT = "Thickness"
    THICKNESS_MIN = 1
    THICKNESS_MAX = 10

    CANVAS_HEIGHT = 600
    CANVAS_WIDTH = 800
    CANVAS_BACKGROUND_COLOR = "#ffffff"

    ERASER_COLOR = CANVAS_BACKGROUND_COLOR

    PING_DELAY = 0.1
    NUM_PINGS = 3
    PING_RADIUS_FACTOR = 10
    FONT_BASE_SIZE = 10

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
        self.canvas = Canvas(self.root, width = self.CANVAS_WIDTH, 
                                height = self.CANVAS_HEIGHT, 
                                background = self.CANVAS_BACKGROUND_COLOR)
        self.toolbar = Frame(self.root, width = self.FRAME_WIDTH, 
                                relief = RAISED, bd = self.FRAME_BORDER_WIDTH)
        self.current_tool_label = Label(self.toolbar, 
                                            text = self.TOOL_LABEL_TEXT)

        self.pen_button = Button(self.toolbar, text = str(DrawingType.PEN))
        self.rect_button = Button(self.toolbar, text = str(DrawingType.RECT))
        self.oval_button = Button(self.toolbar, text = str(DrawingType.OVAL))
        self.line_button = Button(self.toolbar, text = str(DrawingType.LINE))
        self.eraser_button = Button(self.toolbar, 
                                        text = str(DrawingType.ERASER))
        self.text_button = Button(self.toolbar, text = str(DrawingType.TEXT))
        self.ping_button = Button(self.toolbar, text = str(DrawingType.PING))
        self.clear_button = Button(self.toolbar, 
                                    text = str(DrawingType.CLEAR))

        self.thickness_label = Label(self.toolbar, 
                                        text = self.THICKNESS_LABEL_TEXT)
        self.thickness_scale = Scale(self.toolbar, from_ = self.THICKNESS_MIN, 
                                        to = self.THICKNESS_MAX, 
                                        orient = HORIZONTAL)

    def _place_widgets(self):
        """
        Use a geometry manager to put the widgets in the root window.
        """
        self.canvas.pack(side = RIGHT, fill = BOTH, expand = True)
        self.toolbar.pack(side = LEFT, fill = BOTH, expand = True)
        self.current_tool_label.pack()

        for button in [self.pen_button, self.rect_button, self.oval_button, 
                        self.line_button, self.eraser_button, 
                        self.text_button, self.ping_button]:
            button.pack()
        self.clear_button.pack(side = BOTTOM)
        
        self.thickness_label.pack()
        self.thickness_scale.pack()

    def bind_canvas_callback(self, event_id, callback):
        """
        Register the callback for the given event.
        """
        self.canvas.bind(event_id, callback)

    def bind_window_callback(self, event_id, callback):
        """
        """
        self.root.bind(event_id, callback)

    def bind_tool_button_callbacks(self, pen, rect, oval, line, eraser, text,
                                    ping, clear):
        """
        Register the callbacks for the toolbar buttons.
        """
        self.pen_button["command"] = pen
        self.rect_button["command"] = rect
        self.oval_button["command"] = oval
        self.line_button["command"] = line
        self.eraser_button["command"] = eraser
        self.text_button["command"] = text
        self.ping_button["command"] = ping
        self.clear_button["command"] = clear

    def bind_thickness_scale_callback(self, callback):
        """
        Register the callback for the thickness scale.
        """
        self.thickness_scale["command"] = callback

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

    def draw_shape(self, drawing):
        """
        Determine and call the appropriate drawing function based on the 
        shape type.
        """
        lookup = {DrawingType.PEN : self._draw_line, 
                    DrawingType.RECT : self._draw_rect,
                    DrawingType.OVAL : self._draw_oval,
                    DrawingType.LINE : self._draw_line,
                    DrawingType.ERASER : self._draw_eraser_line,
                    DrawingType.PING : self._draw_ping,
                    DrawingType.CLEAR : self._clear_canvas,
                    DrawingType.TEXT : self._draw_text}
        draw_func = lookup[drawing.shape]
        if drawing.shape == DrawingType.CLEAR:
            args = []
        elif drawing.shape == DrawingType.TEXT:
            args = [drawing.coords, drawing.thickness, drawing.text]
        else:
            args = [drawing.coords, drawing.thickness]
        return draw_func(*args)

    def _draw_rect(self, coords, thickness):
        """
        Draw a rectangle using the opposite corner pairs specified in coords.
        """
        return self.canvas.create_rectangle(*coords, width = thickness)

    def _draw_oval(self, coords, thickness):
        """
        Draw an oval using the corners specificed in coords.
        """
        return self.canvas.create_oval(*coords, width = thickness)

    def _draw_line(self, coords, thickness):
        """
        Draw a line with the start/end pairs specified in coords.
        """
        return self.canvas.create_line(*coords, width = thickness, 
                                        capstyle = ROUND)

    def _draw_eraser_line(self, coords, thickness):
        """
        Draw a line that is white, to "erase" previous drawings.
        """
        return self.canvas.create_line(*coords, width = thickness,
                                        capstyle = ROUND, 
                                        fill = self.ERASER_COLOR)

    def _clear_canvas(self):
        """
        Clear the canvas of all drawings.
        """
        self.canvas.delete(ALL)

    def _draw_ping(self, coords, thickness):
        """
        Draw increasingly large circles around the center point.
        """
        x, y = coords[0], coords[1]
        for i in range(1, self.NUM_PINGS + 1):
            r = i * self.PING_RADIUS_FACTOR
            circle_coords = [x - r, y - r, x + r, y + r]
            circle_id = self.canvas.create_oval(circle_coords, 
                width = thickness)
            self.root.update()  # force the canvas to visually update
            sleep(self.PING_DELAY)
            self.clear_drawing_by_id(circle_id)

    def _draw_text(self, coords, thickness, drawing_text):
        """
        Render text at the first point.
        """
        x, y = coords[0], coords[1]
        font_size = self.FONT_BASE_SIZE + (thickness - 1) * 2 # 8 to 26
        self.canvas.create_text(x, y, font = "Arial {}".format(font_size),
                                    text = drawing_text)

    def clear_drawing_by_id(self, drawing_id):
        """
        Delete the drawing with the given id from the canvas.
        """
        self.canvas.delete(drawing_id)

    def update_tool_text(self, text):
        """
        Update the toolbar label text with its default text + the given text.
        """
        self.current_tool_label["text"] = self.TOOL_LABEL_TEXT + text
