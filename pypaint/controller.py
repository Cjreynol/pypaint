from threading          import Thread
from tkinter            import Toplevel

from chadlib.gui        import ControllerBase, TextEntryDialog
from chadlib.io         import Connection

from .drawing           import Drawing
from .drawing_type      import DrawingType
from .paint_view        import PaintView


class Controller(ControllerBase):
    """
    Manages the interface event handling and the network connection.
    """

    DEFAULT_PORT = 2423
    TEXT_SIZE_LIMIT = 128

    # aliases for tkinter event types
    BUTTON_PRESS = '4'
    BUTTON_RELEASE = '5'
    MOTION = '6'
    KEYPRESS = '2'

    def __init__(self, application_state):
        super().__init__("PyPaint", application_state, PaintView)
        self.connection = Connection(self.application_state.send_queue, 
                                        self.application_state.receive_queue)

    def startup_listening(self):
        self.connection.startup_accept(self.DEFAULT_PORT, 
                                        self.start_processing)

    def get_ip(self):
        TextEntryDialog("Enter IP address of host", self.startup_connect, None)

    def disconnect(self):
        self.connection.close()

    def startup_connect(self, ip_address):
        self.connection.startup_connect(self.DEFAULT_PORT, ip_address,
                                        self.start_processing)

    def start_processing(self):
        self.start_processing_receive_queue()
        self.current_view.start_processing_draw_queue()

    def start_processing_receive_queue(self):
        def f():
            while self.application_state.active:
                data = self.application_state.receive_queue.get()
                if data is not None:
                    for drawing in Drawing.decode_drawings(data):
                        self.application_state.draw_queue.put(drawing)
        Thread(target = f).start()

    def stop(self):
        super().stop()
        self.connection.close()
        self.application_state.receive_queue.put(None)    # release the decoding thread
        self.application_state.draw_queue.put(None)       # release the drawing thread
        self.application_state.active = False

    def _enqueue(self, drawing):
        """
        Encode the drawing as bytes and put it in the send queue.
        """
        encoded_drawing = drawing.encode()
        if encoded_drawing is not None:
            self.application_state.add_to_send_queue(encoded_drawing)

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
        self.application_state.start_pos = event.x, event.y
        if self.application_state.current_type == DrawingType.TEXT:
            self.current_view.create_text_entry(
                                            self.application_state.start_pos 
                                                + (0, 0))

    def _handle_motion_event(self, event):
        """
        If a motion-based drawing is in progress then create a new drawing 
        and either:
            -enqueue it if the drawing is not draggable
            -delete the last intermediate drawing if it is
        """
        if (self.application_state.start_pos is not None 
                and DrawingType.is_motion_related(
                                        self.application_state.current_type)):
            event_coords = event.x, event.y
            drawing = Drawing(self.application_state.current_type, 
                                self.application_state.current_thickness, 
                                self.application_state.start_pos 
                                    + event_coords)
            drawing_id = self.current_view.draw_shape(drawing)

            if not DrawingType.is_draggable(
                                        self.application_state.current_type):
                self._enqueue(drawing)
                self.application_state.start_pos = event_coords
            else:
                self.current_view.clear_drawing_by_id(
                                        self.application_state.last_drawing_id)

            self.application_state.last_drawing_id = drawing_id

    def _handle_button_release_event(self, event):
        """
        Clear the last drawing if it was draggable, draw the final version, 
        and clear the drawing state information.
        """
        if DrawingType.is_draggable(self.application_state.current_type):
            self.current_view.clear_drawing_by_id(
                                        self.application_state.last_drawing_id)

        if (self.application_state.start_pos is not None
            and self.application_state.current_type != DrawingType.TEXT):
                self._create_drawing(self.application_state.current_type, 
                                    self.application_state.current_thickness, 
                                    self.application_state.start_pos 
                                        + (event.x, event.y))
        self.application_state.clear_drawing_state()

    def _handle_keyboard_event(self, event):
        """
        Cancel current drawing when Escape key is pressed.
        """
        if event.keysym == "Escape":
            self.current_view.clear_drawing_by_id(
                                        self.application_state.last_drawing_id)
            self.application_state.clear_drawing_state()

    def create_text(self, text, coords):
        """
        A specialized version of _create_drawing for use by the text tool.
        """
        self._create_drawing(DrawingType.TEXT, 
                                self.application_state.current_thickness, 
                                coords, text[:self.TEXT_SIZE_LIMIT])

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

    def get_menu_data(self):
        """
        Get the default menu setup data, add network control commands.
        """
        menu_setup = super().get_menu_data()
        menu_setup.add_submenu_items("Network", 
                                        [("Host", self.startup_listening),
                                        ("Connect", self.get_ip),
                                        ("Disconnect", self.disconnect)])
        return menu_setup
