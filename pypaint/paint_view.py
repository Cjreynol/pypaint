from time               import sleep
from tkinter            import (Button, Canvas, Frame, Label, Scale, Tk, ALL, 
                                BOTH, BOTTOM, HORIZONTAL, LEFT, RIGHT, ROUND, 
                                RAISED, SUNKEN, W)

from chadlib.gui        import View

from .drawing_type      import DrawingType
from .text_entry_box    import TextEntryBox


class PaintView(View):

    FRAME_BORDER_WIDTH = 2
    FRAME_WIDTH = 120

    CANVAS_HEIGHT = 600
    CANVAS_WIDTH = 800
    CANVAS_BACKGROUND_COLOR = "#ffffff"

    PING_DELAY = 0.1
    NUM_PINGS = 3
    PING_RADIUS_FACTOR = 10

    FONT_BASE_SIZE = 10

    def __init__(self, controller, root):
        super().__init__(controller, root)

        self.current_tool_index = 0

    def _create_widgets(self):
        self.canvas = Canvas(self, width = self.CANVAS_WIDTH, 
                                height = self.CANVAS_HEIGHT, 
                                background = self.CANVAS_BACKGROUND_COLOR)
            
        self.toolbar = Frame(self, width = self.FRAME_WIDTH, relief = RAISED, 
                                bd = self.FRAME_BORDER_WIDTH)

        self.buttons = []
        for d_type in DrawingType:
            if d_type != DrawingType.CLEAR:   # clear button has a special action
                button = Button(self.toolbar, text = str(d_type), 
                    # len(buttons) is used instead of the index because some 
                    # drawing types are skipped, so the DrawingType index != 
                    # toolbar button index
                    command = self._create_change_mode_callback(d_type, len(self.buttons)))
                self.buttons.append(button)
        # TODO CJR:  there is a potential disconnect between this, the 
        # current tool index and the default current mode of the controller
        self.buttons[0]["relief"] = SUNKEN

        self.clear_button = Button(self.toolbar, text = str(DrawingType.CLEAR))
        self.thickness_label = Label(self.toolbar, text = "Thickness")
        self.thickness_scale = Scale(self.toolbar, orient = HORIZONTAL, 
                                        from_ = self.controller.THICKNESS_MIN, 
                                        to = self.controller.THICKNESS_MAX)

    def _arrange_widgets(self):
        self.canvas.pack(side = RIGHT, fill = BOTH, expand = True)
        self.toolbar.pack(side = LEFT, fill = BOTH, expand = True)

        for button in self.buttons:
            button.pack()
        self.clear_button.pack(side = BOTTOM)
        
        self.thickness_label.pack()
        self.thickness_scale.pack()

    def _bind_actions(self):
        for event_type in ["<Button-1>", "<ButtonRelease-1>", "<B1-Motion>"]:
            self.canvas.bind(event_type, self.controller.handle_event)
        
        self.clear_button["command"] = self.controller.clear_callback
        self.thickness_scale["command"] = self.controller.thickness_callback

    def draw_shape(self, drawing):
        """
        Call the appropriate draw call based on the drawing type
        """
        drawing_id = None
        if drawing.shape == DrawingType.PEN:
            drawing_id = self._draw_line(drawing.coords, drawing.thickness)
        elif drawing.shape == DrawingType.RECT:
            drawing_id = self._draw_rect(drawing.coords, drawing.thickness)
        elif drawing.shape == DrawingType.OVAL:
            drawing_id = self._draw_oval(drawing.coords, drawing.thickness)
        elif drawing.shape == DrawingType.LINE:
            drawing_id = self._draw_line(drawing.coords, drawing.thickness)
        elif drawing.shape == DrawingType.ERASER:
            drawing_id = self._draw_eraser_line(drawing.coords, 
                                                drawing.thickness)
        elif drawing.shape == DrawingType.PING:
            drawing_id = self._draw_ping(drawing.coords, drawing.thickness)
        elif drawing.shape == DrawingType.CLEAR:
            drawing_id = self._clear_canvas()
        elif drawing.shape == DrawingType.TEXT:
            drawing_id = self._draw_text(drawing.coords, drawing.thickness, 
                                            drawing.text)
        return drawing_id

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
                                        fill = self.CANVAS_BACKGROUND_COLOR)

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
            self.controller.update()  # force the canvas to visually update
            sleep(self.PING_DELAY)
            self.clear_drawing_by_id(circle_id)

    def _draw_text(self, coords, thickness, drawing_text):
        """
        Render text at the first point.
        """
        x, y = coords[0], coords[1]
        font_size = self.FONT_BASE_SIZE + (thickness - 1) * 2
        self.canvas.create_text(x, y, font = "Arial {}".format(font_size),
                                    anchor = W, text = drawing_text)

    def clear_drawing_by_id(self, drawing_id):
        """
        Delete the drawing with the given id from the canvas.
        """
        self.canvas.delete(drawing_id)

    def _create_change_mode_callback(self, drawing_type, button_index):
        """
        Update the controller's drawing mode and the currently selected button.
        """
        def f():
            self.controller.current_mode = drawing_type

            self.buttons[self.current_tool_index]["relief"] = RAISED
            self.current_tool_index = button_index
            self.buttons[self.current_tool_index]["relief"] = SUNKEN
        return f

    def create_text_entry(self, coords):
        TextEntryBox(self.controller, coords)
