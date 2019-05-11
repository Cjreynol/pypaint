from time               import sleep
from tkinter            import Canvas, ALL, ROUND, W


class PaintCanvas(Canvas):
    """
    Specialized canvas for drawing, holds logic for different PyPaint 
    drawings and binds the correct events to the canvas.
    """
    
    CANVAS_HEIGHT = 600
    CANVAS_WIDTH = 800
    CANVAS_BACKGROUND_COLOR = "#ffffff"

    PING_DELAY = 0.1
    NUM_PINGS = 3
    PING_RADIUS_FACTOR = 10

    FONT_BASE_SIZE = 10

    def __init__(self, controller, root, application_state):
        super().__init__(root, width = self.CANVAS_WIDTH, 
                            height = self.CANVAS_HEIGHT,
                            background = self.CANVAS_BACKGROUND_COLOR)

        self.controller = controller
        self.application_state = application_state

        for event_type in ["<Button-1>", "<ButtonRelease-1>", "<B1-Motion>"]:
            self.bind(event_type, self.controller.handle_event)

    def draw_rect(self, coords, thickness, color):
        """
        Draw a rectangle using the opposite corner pairs specified in coords.
        """
        return self.create_rectangle(*coords, width = thickness, 
                                            outline = color)

    def draw_oval(self, coords, thickness, color):
        """
        Draw an oval using the corners specificed in coords.
        """
        return self.create_oval(*coords, width = thickness, 
                                        outline = color)

    def draw_line(self, coords, thickness, color):
        """
        Draw a line with the start/end pairs specified in coords.
        """
        return self.create_line(*coords, width = thickness, 
                                        capstyle = ROUND, fill = color)

    def draw_eraser_line(self, coords, thickness, color):
        """
        Draw a line that is white, to "erase" previous drawings.
        """
        return self.create_line(*coords, width = thickness,
                                        capstyle = ROUND, 
                                        fill = self.CANVAS_BACKGROUND_COLOR)

    def undo(self):
        """
        Clear the last drawing available from the history.
        """
        if self.application_state.id_available:
            drawing_id = self.application_state.get_last_drawing_id()
            self.delete(drawing_id)

    def clear_canvas(self):
        """
        Clear the canvas of all drawings.
        """
        self.delete(ALL)

    def draw_ping(self, coords, thickness, color):
        """
        Draw increasingly large circles around the center point.
        """
        x, y = coords[0], coords[1]
        for i in range(1, self.NUM_PINGS + 1):
            r = i * self.PING_RADIUS_FACTOR
            circle_coords = [x - r, y - r, x + r, y + r]
            drawing_id = self.draw_oval(circle_coords, thickness, color)
            self.application_state.add_last_drawing(drawing_id, None)
            self.controller.update()  # force the canvas to visually update
            sleep(self.PING_DELAY)
            self.undo()

    def draw_text(self, coords, thickness, color, drawing_text):
        """
        Render text at the first point.
        """
        font_size = self.FONT_BASE_SIZE + (thickness - 1) * 2
        return self.create_text(coords[0], coords[1], anchor = W,
                                    font = "Arial {}".format(font_size),
                                    text = drawing_text,
                                    fill = color)
