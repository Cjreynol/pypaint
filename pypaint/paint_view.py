from time import sleep
from tkinter import (Button, Canvas, Frame, Label, Scale, Tk, 
                        ALL, BOTH, BOTTOM, HORIZONTAL, LEFT, RIGHT, ROUND, 
                        RAISED, W)

from .drawing_type  import DrawingType
from .view          import View


class PaintView(View):

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

    def _create_widgets(self):
        self.canvas = Canvas(self, width = self.CANVAS_WIDTH, 
                                height = self.CANVAS_HEIGHT, 
                                background = self.CANVAS_BACKGROUND_COLOR)
            
        self.toolbar = Frame(self, width = self.FRAME_WIDTH, relief = RAISED, 
                                bd = self.FRAME_BORDER_WIDTH)
        self.current_tool_label = Label(self.toolbar, 
                                    text = (self.TOOL_LABEL_TEXT 
                                        + str(self.controller.current_mode)))

        self.buttons = []
        for tool in DrawingType:
            if tool != DrawingType.CLEAR:   # clear button has a special action
                button = Button(self.toolbar, text = str(tool), 
                    command = self.controller.set_mode_generator(tool))
                self.buttons.append(button)

        self.clear_button = Button(self.toolbar, text = str(DrawingType.CLEAR))
        self.thickness_label = Label(self.toolbar, 
                                        text = self.THICKNESS_LABEL_TEXT)
        self.thickness_scale = Scale(self.toolbar, from_ = self.THICKNESS_MIN, 
                                to = self.THICKNESS_MAX, orient = HORIZONTAL)

    def _arrange_widgets(self):
        self.canvas.pack(side = RIGHT, fill = BOTH, expand = True)
        self.toolbar.pack(side = LEFT, fill = BOTH, expand = True)
        self.current_tool_label.pack()

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

    def update_tool_text(self, text):
        """
        Update the toolbar label text with its default text + the given text.
        """
        self.current_tool_label["text"] = self.TOOL_LABEL_TEXT + text
