from time               import sleep
from tkinter            import Canvas, ALL, ROUND, W

from chadlib.gui        import View


class PaintCanvas(View):
    """
    """
    
    CANVAS_HEIGHT = 600
    CANVAS_WIDTH = 800
    CANVAS_BACKGROUND_COLOR = "#ffffff"

    PING_DELAY = 0.1
    NUM_PINGS = 3
    PING_RADIUS_FACTOR = 10

    FONT_BASE_SIZE = 10

    def _create_widgets(self):
        self.canvas = Canvas(self, width = self.CANVAS_WIDTH, 
                                height = self.CANVAS_HEIGHT, 
                                background = self.CANVAS_BACKGROUND_COLOR)

    def _arrange_widgets(self):
        self.canvas.pack()

    def _bind_actions(self):
        for event_type in ["<Key>", "<Button-1>", "<ButtonRelease-1>", 
                            "<B1-Motion>"]:
            self.canvas.bind(event_type, self.controller.handle_event)

    def draw_rect(self, coords, thickness):
        """
        Draw a rectangle using the opposite corner pairs specified in coords.
        """
        return self.canvas.create_rectangle(*coords, width = thickness)

    def draw_oval(self, coords, thickness):
        """
        Draw an oval using the corners specificed in coords.
        """
        return self.canvas.create_oval(*coords, width = thickness)

    def draw_line(self, coords, thickness):
        """
        Draw a line with the start/end pairs specified in coords.
        """
        return self.canvas.create_line(*coords, width = thickness, 
                                        capstyle = ROUND)

    def draw_eraser_line(self, coords, thickness):
        """
        Draw a line that is white, to "erase" previous drawings.
        """
        return self.canvas.create_line(*coords, width = thickness,
                                        capstyle = ROUND, 
                                        fill = self.CANVAS_BACKGROUND_COLOR)

    def clear_canvas(self):
        """
        Clear the canvas of all drawings.
        """
        self.canvas.delete(ALL)

    def draw_ping(self, coords, thickness):
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

    def draw_text(self, coords, thickness, drawing_text):
        """
        Render text at the first point.
        """
        font_size = self.FONT_BASE_SIZE + (thickness - 1) * 2
        self.canvas.create_text(coords[0], coords[1], anchor = W,
                                    font = "Arial {}".format(font_size),
                                    text = drawing_text)

    def clear_drawing_by_id(self, drawing_id):
        """
        Delete the drawing with the given id from the canvas.
        """
        self.canvas.delete(drawing_id)
