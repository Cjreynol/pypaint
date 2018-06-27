from pypaint.connection import Connection
from pypaint.drawing import Drawing
from pypaint.drawing_type import DrawingType
from pypaint.paint_view import PaintView
from pypaint.setup_view import SetupView


class Controller:
    """
    Manages the View, interface event handling, and the network connection.
    """

    DEFAULT_DRAWING_MODE = DrawingType.PEN
    DEFAULT_THICKNESS = PaintView.THICKNESS_MIN

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
        self.view = self._create_setup_view()
            
    def _create_setup_view(self):
        """
        Return a setup view with the necessary callbacks registered.
        """
        view = SetupView()
        view.bind_host_button_callback(self._generate_setup_button_callback(True))
        view.bind_connect_button_callback(self._generate_setup_button_callback(False))
        view.bind_offline_button_callback(self._swap_views)
        return view

    def _generate_setup_button_callback(self, host):
        """
        """
        def callback_gen(ip_entry, port_entry):
            def f():
                self.connection.startup(int(port_entry.get()),
                                        ip_entry.get() if not host else None)
                self._swap_views()
            return f
        return callback_gen

    def _swap_views(self):
        """
        Destroy the setup view and create/start the paint view.
        """
        self.view.root.destroy()
        self.view = self._create_paint_view()
        self.start_paint_view()

    def _create_paint_view(self):
        """
        Return a paint view with the necessary callbacks registered.
        """
        view = PaintView()
        for event_type in ["<Button-1>", "<ButtonRelease-1>", "<B1-Motion>"]:
            view.bind_canvas_callback(event_type, self.handle_event)
        view.bind_window_callback("<Key>", self.handle_event)
        view.bind_tool_button_callbacks(
                                self._set_mode_generator(DrawingType.PEN),
                                self._set_mode_generator(DrawingType.RECT),
                                self._set_mode_generator(DrawingType.OVAL),
                                self._set_mode_generator(DrawingType.LINE),
                                self._set_mode_generator(DrawingType.ERASER),
                                self._set_mode_generator(DrawingType.PING),
                                self.clear_callback)
        view.bind_thickness_scale_callback(self.thickness_callback)
        view.bind_quit_callback(self.stop)
        view.update_tool_text(str(self.current_mode))
        return view

    def start(self):
        """
        """
        self.view.start()

    def start_paint_view(self):
        """
        Start the controllers components.
        """
        self.connection.start(self._decode_and_draw)
        self.view.start()

    def _decode_and_draw(self, drawing_data):
        """
        Decode the drawing(s) and pass them to the view to be displayed.
        """
        for drawing in Drawing.decode_drawings(drawing_data):
            self.view.draw_shape(drawing)

    def stop(self):
        """
        Shut down the connection and close the view.
        """
        self.connection.close()
        self.view.root.destroy()

    def _set_mode_generator(self, drawing_type):
        """
        Return a function that sets the current drawing mode to the given 
        drawing type.
        """
        def f():
            self.current_mode = drawing_type
            self.view.update_tool_text(str(drawing_type))
        return f

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
        self.view.draw_shape(drawing)
        self._encode_and_enqueue(drawing)

    def handle_event(self, event):
        """
        """
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
                and self.current_mode != DrawingType.PING):
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
            self.view.clear_drawing_by_id(self.last_drawing_id)

        if not self.cancel_drawing:
            event_coord = event.x, event.y
            drawing = Drawing(drawing_type, self.current_thickness, 
                                self.start_pos + event_coord)

            if not drag_drawing:
                self._encode_and_enqueue(drawing)
                self.start_pos = event_coord
            drawing_id = self.view.draw_shape(drawing)

            self.last_drawing_id = drawing_id

    def _handle_button_release_event(self, event, drawing_type, drag_drawing):
        """
        """
        if drag_drawing:
            self.view.clear_drawing_by_id(self.last_drawing_id)

        if not self.cancel_drawing:
            drawing = Drawing(drawing_type, self.current_thickness, 
                                self.start_pos + (event.x, event.y))

            self._encode_and_enqueue(drawing)
            self.view.draw_shape(drawing)

        self.start_pos = None
        self.last_drawing_id = None
        self.cancel_drawing = False

    def _encode_and_enqueue(self, drawing):
        """
        Encode the drawing as bytes and put it in the send queue.
        """
        data = drawing.encode()
        self.connection.add_to_send_queue(data)
