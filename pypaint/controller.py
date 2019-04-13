from .connection        import Connection
from .drawing           import Drawing
from .drawing_type      import DrawingType
from .main_window       import MainWindow
from .paint_view        import PaintView
from .setup_view        import SetupView
from .text_entry_box    import TextEntryBox


class Controller:
    """
    Manages the View, interface event handling, and the network connection.
    """

    DEFAULT_DRAWING_MODE = DrawingType.PEN
    DEFAULT_THICKNESS = PaintView.THICKNESS_MIN

    TEXT_SIZE_LIMIT = 128

    # aliases for tkinter event types
    BUTTON_PRESS = '4'
    BUTTON_RELEASE = '5'
    MOTION = '6'
    KEYPRESS = '2'

    def __init__(self):
        self.start_pos = None
        self.last_drawing_id = None
        self.cancel_drawing = False

        self.current_mode = self.DEFAULT_DRAWING_MODE
        self.current_thickness = self.DEFAULT_THICKNESS

        self.connection = Connection()
        self.window = MainWindow(self, "PyPaint", SetupView)

    def get_host_callback(self, port_entry):
        def f():
            self.connection.startup_accept(int(port_entry.get()))
            self.swap_views()
        return f

    def get_connect_callback(self, port_entry, ip_entry):
        def f():
            self.connection.startup_connect(int(port_entry.get()), 
                                            ip_entry.get())
            self.swap_views()
        return f

    def swap_views(self):
        """
        Destroy the setup view and create/start the paint view.
        """
        self.window.set_new_view(PaintView)
        self.window.root.bind("<Key>", self.handle_event)
        self.connection.start(self._decode_and_draw)

    def start(self):
        self.window.start()

    def _decode_and_draw(self, drawing_data):
        """
        Decode the drawing(s) and pass them to the view to be displayed.
        """
        for drawing in Drawing.decode_drawings(drawing_data):
            self.window.view.draw_shape(drawing)

    def stop(self):
        self.connection.close()
        self.window.destroy()

    def set_mode_generator(self, drawing_type):
        """
        Return a function that sets the current drawing mode to the given 
        drawing type.
        """
        def f():
            self.current_mode = drawing_type
            self.window.view.update_tool_text(str(drawing_type))
        return f

    def _enqueue(self, drawing):
        """
        Encode the drawing as bytes and put it in the send queue.
        """
        self.connection.add_to_send_queue(drawing.encode())

    def thickness_callback(self, thickness_value):
        """
        Set the current thickness value.
        """
        self.current_thickness = int(thickness_value)

    def clear_callback(self):
        """
        Clear the drawing canvas.
        """
        drawing = Drawing(DrawingType.CLEAR, 0, (0, 0, 0, 0))
        self.window.view.draw_shape(drawing)
        self._enqueue(drawing)

    def handle_event(self, event):
        if event.type in [self.BUTTON_PRESS, self.BUTTON_RELEASE, self.MOTION]:
            self._handle_mouse_event(event, self.current_mode, 
                                    self._is_draggable(self.current_mode))
        elif event.type == self.KEYPRESS:
            self._handle_keyboard_event(event)

    def _is_draggable(self, drawing_type):
        """
        Return if the drawing type is one that is temporarily drawn until 
        button release.
        """
        return drawing_type in {DrawingType.RECT, DrawingType.OVAL, 
                                    DrawingType.LINE}

    def _handle_keyboard_event(self, event):
        """
        """
        if event.keysym == "Escape":
            self.cancel_drawing = True

    def _handle_mouse_event(self, event, drawing_type, drag_drawing):
        """
        Take action based on the given event.
        """
        if event.type == self.BUTTON_PRESS:
            self._handle_button_press_event(event, drawing_type, drag_drawing)
        elif (event.type == self.MOTION 
                and self.current_mode 
                    not in [DrawingType.PING, DrawingType.TEXT]):
            self._handle_motion_event(event, drawing_type, drag_drawing)
        elif event.type == self.BUTTON_RELEASE:
            self._handle_button_release_event(event, drawing_type, drag_drawing)
    
    def _handle_button_press_event(self, event, drawing_type, drag_drawing):
        """
        Save the start point for the drawing.
        """
        self.start_pos = event.x, event.y

    def _handle_motion_event(self, event, drawing_type, drag_drawing):
        """
        """
        if drag_drawing:
            self.window.view.clear_drawing_by_id(self.last_drawing_id)

        if not self.cancel_drawing:
            event_coord = event.x, event.y
            drawing = Drawing(drawing_type, self.current_thickness, 
                                self.start_pos + event_coord)

            if not drag_drawing:
                self._enqueue(drawing)
                self.start_pos = event_coord
            drawing_id = self.window.view.draw_shape(drawing)

            self.last_drawing_id = drawing_id

    def _handle_button_release_event(self, event, drawing_type, drag_drawing):
        """
        """
        if drag_drawing:
            self.window.view.clear_drawing_by_id(self.last_drawing_id)

        if not self.cancel_drawing and self.start_pos is not None:
            if drawing_type != DrawingType.TEXT:
                drawing = Drawing(drawing_type, self.current_thickness, 
                                    self.start_pos + (event.x, event.y))
                self._enqueue(drawing)
                self.window.view.draw_shape(drawing)
            else:
                self._create_text_entry_box(self.current_thickness, 
                                        self.start_pos + (event.x, event.y))

        self.start_pos = None
        self.last_drawing_id = None
        self.cancel_drawing = False

    def _create_text_entry_box(self, thickness, coords):
        """
        """
        TextEntryBox(self._text_box_confirm_callback_generator,
                        self._text_box_cancel_callback_generator, 
                        thickness, coords)

    def _text_box_confirm_callback_generator(self, window, text_entry, 
                                                thickness, coords):
        """
        """
        def f(event = None):   # event is passed when using a keybinding
            drawing = Drawing(DrawingType.TEXT, thickness, coords, 
                                text_entry.get()[:self.TEXT_SIZE_LIMIT])
            self._enqueue(drawing)
            self.window.view.draw_shape(drawing)
            window.destroy()
        return f

    def _text_box_cancel_callback_generator(self, window):
        """
        """
        def f():
            window.destroy()
        return f

    def update(self):
        """
        Force a visual update.
        """
        self.window.update()
