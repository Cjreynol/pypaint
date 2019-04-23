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

    APPLICATION_NAME = "PyPaint"
    FILE_EXTENSION = ".pypaint"
    FILETYPES = (("pypaint files", "*" + FILE_EXTENSION),)

    DEFAULT_PORT = 2423
    TEXT_SIZE_LIMIT = 128

    # aliases for tkinter event types
    BUTTON_PRESS = '4'
    BUTTON_RELEASE = '5'
    MOTION = '6'
    KEYPRESS = '2'

    def __init__(self, application_state):
        super().__init__(application_state, PaintView)
        self.connection = Connection(self.application_state.send_queue, 
                                        self.application_state.receive_queue)

    def startup_listening(self):
        self.application_state.active = True
        self.connection.startup_accept(self.DEFAULT_PORT, 
                                        self.start_processing_receive_queue)

    def startup_connect(self, ip_address):
        self.application_state.active = True
        self.connection.startup_connect(self.DEFAULT_PORT, ip_address,
                                        self.start_processing_receive_queue)

    def disconnect(self):
        self.connection.close()

    def get_ip(self):
        TextEntryDialog("Enter IP address of host", self.startup_connect, None)

    def start_processing_receive_queue(self):
        """
        Start up the thread to decode drawings and put them on the drawing 
        queue.
        """
        def f():
            while self.application_state.active:
                data = self.application_state.receive_queue.get()
                if data is not None:
                    for drawing in Drawing.decode_drawings(data):
                        self.application_state.add_to_draw_queue(drawing)
        Thread(target = f).start()

    def start(self):
        self.current_view.start_processing_draw_queue()
        # TODO CJR:  find a better place for this
        self.window.root.bind("<Key>", self.handle_event)
        super().start() # must be called at the end, starts the GUI loop

    def stop(self):
        super().stop()
        self.connection.close()
        self.application_state.receive_queue.put(None)  # release decoding thread
        self.application_state.add_to_draw_queue(None)  # release drawing thread
        self.application_state.active = False
        self.application_state.draw_active = False

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
        if self.application_state.current_type is DrawingType.TEXT:
            self.current_view.create_text_entry(
                                            self.application_state.start_pos 
                                                + (0, 0))

    def _handle_motion_event(self, event):
        """
        Create a new drawing if it triggers off of motion events.

        If this is the first motion event since a button press, trigger the 
        dragging state so that undos are created for the following motion 
        events.

        If it is not a draggable shape, then reset the start position for the 
        next drawing.
        """
        if (self.application_state.start_pos is not None 
                and DrawingType.is_motion_related(
                                        self.application_state.current_type)):
            if self.application_state.dragging:
                self.create_undo()
            event_coords = event.x, event.y
            self._create_drawing(self.application_state.current_type, 
                                    self.application_state.current_thickness, 
                                    self.application_state.current_color,
                                    self.application_state.start_pos 
                                        + event_coords)

            if not DrawingType.is_draggable(
                                        self.application_state.current_type):
                self.application_state.start_pos = event_coords
            else:   # used to start undoing on the second motion event
                self.application_state.dragging = True

    def _handle_button_release_event(self, event):
        """
        Create the final drawing in the sequence, undoing the last one if 
        necessary, and clearing the drawing state.
        """
        if DrawingType.is_draggable(self.application_state.current_type):
            self.create_undo()

        if (self.application_state.start_pos is not None
            and self.application_state.current_type != DrawingType.TEXT):
            self._create_drawing(self.application_state.current_type, 
                                    self.application_state.current_thickness, 
                                    self.application_state.current_color,
                                    self.application_state.start_pos 
                                        + (event.x, event.y))
        self.application_state.clear_drawing_state()

    def _handle_keyboard_event(self, event):
        """
        Cancel current drawing when Escape key is pressed.
        """
        if event.keysym == "Escape":
            self.create_undo()
            self.application_state.clear_drawing_state()

    def create_text(self, text, coords):
        """
        A specialized version of _create_drawing for use by the text tool.
        """
        self._create_drawing(DrawingType.TEXT, 
                                self.application_state.current_thickness, 
                                self.application_state.current_color,
                                coords, text[:self.TEXT_SIZE_LIMIT])

    def create_clear(self):
        self._create_drawing(DrawingType.CLEAR, 0, "", (0, 0, 0, 0))

    def create_undo(self):
        self._create_drawing(DrawingType.UNDO, 0, "", (0, 0, 0, 0))

    def _create_drawing(self, drawing_type, thickness, color, coords, 
                        text = None):
        """
        Create, draw, and queue up the drawing to send out.
        """
        drawing = Drawing(drawing_type, thickness, color, coords, text)
        self.application_state.add_to_draw_queue(drawing)

        encoded_drawing = drawing.encode()
        if encoded_drawing is not None:
            self.application_state.add_to_send_queue(encoded_drawing)

    def get_menu_data(self):
        """
        Get the default menu setup data, add network control commands.
        """
        menu_setup = super().get_menu_data()
        menu_setup.add_submenu_items("Network", 
                            [("Host", self.startup_listening, "Alt-h"),
                            ("Connect", self.get_ip, "Alt-c"),
                            ("Disconnect", self.disconnect, "Alt-d")])
        return menu_setup

    def _save_logic(self, filename):
        with open(filename, "wb") as cur_file:
            # TODO CJR:  remove undos and the drawings prior to them
            data = b''.join([drawing.encode() for drawing in 
                                    self.application_state.drawing_history
                                    if drawing.shape is not DrawingType.PING])
            cur_file.write(data)

    def _open_logic(self, filename):
        with open(filename, "rb") as cur_file:
            self.create_clear() # clear the canvas when loading a file
            data = cur_file.read()
            for drawing in Drawing.decode_drawings(data):
                self.application_state.add_to_draw_queue(drawing)
                self.application_state.add_to_send_queue(drawing)
