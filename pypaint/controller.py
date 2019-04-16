from threading          import Thread

from chadlib.gui        import ControllerBase
from chadlib.io         import Connection

from .drawing           import Drawing
from .drawing_type      import DrawingType
from .paint_view        import PaintView
from .setup_view        import SetupView


class Controller(ControllerBase):
    """
    Manages the View, interface event handling, and the network connection.
    """

    THICKNESS_MIN = 1
    THICKNESS_MAX = 10

    TEXT_SIZE_LIMIT = 128

    # aliases for tkinter event types
    BUTTON_PRESS = '4'
    BUTTON_RELEASE = '5'
    MOTION = '6'
    KEYPRESS = '2'

    def __init__(self):
        super().__init__("PyPaint", default_view = SetupView)

        self.start_pos = None
        self.last_drawing_id = None

        self.current_mode = DrawingType.PEN
        self.current_thickness = self.THICKNESS_MIN

        self.connection = Connection()

    def startup_listening(self, port_num):
        self.connection.startup_accept(port_num)

    def startup_connect(self, port_num, ip_address):
        self.connection.startup_connect(port_num, ip_address)

    def swap_views(self):
        """
        Swap to the paint view and start a thread to pull received drawings 
        from the queue and display them.
        """
        self.window.set_new_view(PaintView)
        self.window.root.bind("<Key>", self.handle_event)
        self.connection.start()
        self.connection.start_data_processing(self._decode_and_draw)

    def _decode_and_draw(self, drawing_data):
        """
        Decode the drawing(s) and pass them to the view to be displayed.
        """
        for drawing in Drawing.decode_drawings(drawing_data):
            self.current_view.draw_shape(drawing)

    def stop(self):
        super().stop()
        self.connection.close()

    def _enqueue(self, drawing):
        """
        Encode the drawing as bytes and put it in the send queue.
        """
        self.connection.add_to_send_queue(drawing.encode())

    def handle_event(self, event):
        """
        Dispatch the event to the proper handler.
        """
        if event.type == self.BUTTON_PRESS:
            self._handle_button_press_event(event)
        elif event.type == self.MOTION:
            self._handle_motion_event(event)
        elif event.type == self.BUTTON_RELEASE:
            self._handle_button_release_event(event)
        elif event.type == self.KEYPRESS:
            self._handle_keyboard_event(event)
    
    def _handle_button_press_event(self, event):
        """
        Save the start point for the drawing, create a text box if that is 
        the current drawing mode.
        """
        self.start_pos = event.x, event.y
        if self.current_mode == DrawingType.TEXT:
            self.current_view.create_text_entry(self.start_pos + (0, 0))

    def _handle_motion_event(self, event):
        """
        If a motion-based drawing is in progress then create a new drawing 
        and either:
            -enqueue it if the drawing is not draggable
            -delete the last intermediate drawing if it is
        """
        if (self.start_pos is not None 
                and DrawingType.is_motion_related(self.current_mode)):
            event_coords = event.x, event.y
            drawing = Drawing(self.current_mode, self.current_thickness, 
                                self.start_pos + event_coords)
            drawing_id = self.current_view.draw_shape(drawing)

            if not DrawingType.is_draggable(self.current_mode):
                self._enqueue(drawing)
                self.start_pos = event_coords
            else:
                self.current_view.clear_drawing_by_id(self.last_drawing_id)

            self.last_drawing_id = drawing_id

    def _handle_button_release_event(self, event):
        """
        Clear the last drawing if it was draggable, draw the final version, 
        and clear the drawing state information.
        """
        if DrawingType.is_draggable(self.current_mode):
            self.current_view.clear_drawing_by_id(self.last_drawing_id)

        if (self.start_pos is not None
            and self.current_mode != DrawingType.TEXT):
                self._create_drawing(self.current_mode, self.current_thickness, 
                                        self.start_pos + (event.x, event.y))
        self.clear_drawing_state()

    def _handle_keyboard_event(self, event):
        """
        Cancel current drawing when Escape key is pressed.
        """
        if event.keysym == "Escape":
            self.current_view.clear_drawing_by_id(self.last_drawing_id)
            self.clear_drawing_state()

    def clear_drawing_state(self):
        self.start_pos = None
        self.last_drawing_id = None

    def create_text(self, text, coords):
        """
        A specialized version of _create_drawing for use by the TextEntryBox.
        """
        self._create_drawing(DrawingType.TEXT, self.current_thickness, coords, 
                                text[:self.TEXT_SIZE_LIMIT])
        
    def thickness_callback(self, thickness_value):
        """
        Set the current thickness value.
        """
        self.current_thickness = int(thickness_value)

    def clear_callback(self):
        """
        Clear the drawing canvas.
        """
        self._create_drawing(DrawingType.CLEAR, 0, (0, 0, 0, 0))

    def _create_drawing(self, drawing_type, thickness, coords, text = None):
        """
        Create, draw, and queue up the drawing to send out.
        """
        drawing = Drawing(drawing_type, thickness, coords, text)
        self.current_view.draw_shape(drawing)
        self._enqueue(drawing)
