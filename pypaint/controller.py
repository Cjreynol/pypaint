from chadlib.gui        import (ConnComponent, ConnController, ControllerBase, 
                                SLComponent, SLController)

from .drawing           import Drawing
from .drawing_type      import DrawingType
from .paint_view        import PaintView


class Controller(ConnController, SLController, ControllerBase):
    """
    Manages the interface event handling and the network connection.
    """

    TEXT_SIZE_LIMIT = 128
    DEFAULT_PORT = 2423

    # aliases for tkinter event types
    KEYPRESS = '2'
    BUTTON_PRESS = '4'
    BUTTON_RELEASE = '5'
    MOTION = '6'

    def __init__(self, application_name, application_state):
        FILE_EXTENSION = "." + application_name.lower()
        self.sl_component = SLComponent(self, FILE_EXTENSION, 
                                    (("pypaint files", "*" + FILE_EXTENSION),), 
                                    application_name)
        self.conn_component = ConnComponent(self, self.DEFAULT_PORT, 
                                            application_state.send_queue, 
                                            application_state.receive_queue)

        super().__init__(application_name, application_state, PaintView)

    def process_received_data(self, data):
        for drawing in Drawing.decode_drawings(data):
            if drawing.shape is not DrawingType.SYNC:
                self.application_state.add_to_draw_queue(drawing)
            else:# if a sync was received, trigger sending history
                self._sync_to_connected()

    def start(self):
        self.current_view.start_processing_draw_queue()
        # TODO CJR:  find a better place for this
        self.window.root.bind("<Key>", self.handle_event)
        super().start() # must be called at the end, starts the GUI loop

    def connection_start(self):
        self.application_state.send_active = True

    def stop(self):
        self.application_state.stop()
        self.conn_component.stop()
        super().stop()

    def disconnect(self):
        self.application_state.send_active = False
        self.conn_component.disconnect()

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

    def get_menu_data(self):
        menu_setup = super().get_menu_data()
        menu_setup = self.sl_component.get_menu_data(menu_setup)
        menu_setup = self.conn_component.get_menu_data(menu_setup)
        menu_setup.add_submenu_item("Network", "Sync Canvas", 
                                    self.create_sync, "Alt-s")
        return menu_setup

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

    def create_sync(self):
        self._create_drawing(DrawingType.SYNC, 0, "", (0, 0, 0, 0))

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

    def save_logic(self, filename):
        """
        Encode the entire drawing history and write it to the given file.
        """
        data = b''.join([drawing.encode() for drawing in 
                                self.application_state.drawing_history
                                if drawing is not None])
        with open(filename, "wb") as cur_file:
            cur_file.write(data)

    def load_logic(self, filename):
        """
        Clear the current canvas, then decode the drawing data from the file, 
        and put it on the draw queue to be drawn.
        """
        with open(filename, "rb") as cur_file:
            self.application_state.add_to_draw_queue(self._create_clear())
            data = cur_file.read()
            for drawing in Drawing.decode_drawings(data):
                self.application_state.add_to_draw_queue(drawing)


    def _sync_to_connected(self):
        """
        Enqueue the entire drawing history to send to connected application.

        Put a clear at the front to clear their canvas before updating them 
        with the history.
        """
        self.application_state.add_to_send_queue(self._create_clear().encode())
        for drawing in self.application_state.drawing_history:
            if drawing.shape not in {DrawingType.PING, DrawingType.SYNC}:
                encoded_drawing = drawing.encode()
                if encoded_drawing is not None:
                    self.application_state.add_to_send_queue(encoded_drawing)

    def _create_clear(self):
        return Drawing(DrawingType.CLEAR, 0, "", (0, 0, 0, 0))
