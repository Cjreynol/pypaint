from pypaint.connection import Connection
from pypaint.drawing import Drawing
from pypaint.drawing_type import DrawingType
from pypaint.paint_view import PaintView
from pypaint.setup_view import SetupView


class PaintController:
    """
    Manages the View, interface event handling, and the network connection.

    If the connection does not exist(is None) then the application works solo.
    """

    BUTTON_PRESS = '4'
    BUTTON_RELEASE = '5'
    MOTION = '6'

    DEFAULT_DRAWING_MODE = DrawingType.PEN
    DEFAULT_THICKNESS = PaintView.THICKNESS_MIN

    def __init__(self):
        self.start_pos = None
        self.last_drawing_id = None

        self.current_mode = self.DEFAULT_DRAWING_MODE
        self.current_thickness = self.DEFAULT_THICKNESS

        self.connection = None
        self.view = self._create_setup_view()
            
    def _create_setup_view(self):
        """
        Return a setup view with the necessary callbacks registered.
        """
        view = SetupView()
        view.bind_host_button_callback(self.host_button_callback)
        view.bind_connect_button_callback(self.connect_button_callback)
        view.bind_offline_button_callback(self.offline_button_callback)
        return view

    def host_button_callback(self, ip_entry, port_entry):
        """
        """
        def f():
            self.connection = Connection(True, int(port_entry.get()), 
                                            ip_entry.get())
            self._swap_views()
        return f
    
    def connect_button_callback(self, ip_entry, port_entry):
        """
        """
        def f():
            self.connection = Connection(False, int(port_entry.get()), 
                                            ip_entry.get())
            self._swap_views()
        return f

    def offline_button_callback(self, ip_entry, port_entry):
        """
        """
        def f():
            self._swap_views()
        return f

    def _swap_views(self):
        """
        Destroy the setup view and create/start the paint view.
        """
        self.view.root.destroy()
        self.view = self._create_paint_view()
        self.start()

    def _create_paint_view(self):
        """
        Return a paint view with the necessary callbacks registered.
        """
        view = PaintView()
        for event_type in ["<Button-1>", "<ButtonRelease-1>", "<B1-Motion>"]:
            view.bind_canvas_callback(event_type, self.handle_event)
        view.bind_tool_button_callbacks(
                                self.set_mode_generator(DrawingType.PEN),
                                self.set_mode_generator(DrawingType.RECT),
                                self.set_mode_generator(DrawingType.OVAL),
                                self.set_mode_generator(DrawingType.LINE),
                                self.set_mode_generator(DrawingType.ERASER),
                                self.clear_callback)
        view.bind_thickness_scale_callback(self.thickness_callback)
        view.bind_quit_callback(self.stop)
        view.update_tool_text(str(self.current_mode))
        return view

    def start(self):
        """
        Start the controllers components.
        """
        if self.connection is not None:
            self.connection.start(self.view.draw_shape)
        self.view.start()

    def stop(self):
        """
        Shut down the connection and close the view.
        """
        if self.connection is not None:
            self.connection.close()
        self.view.root.destroy()

    def set_mode_generator(self, drawing_type):
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
        if self.connection is not None:
            self.connection.add_to_send_queue(drawing)

    def handle_event(self, event):
        """
        Call the appropriate event handler based on the current drawing mode.
        """
        self._handle_drawing(event, self.current_mode, 
                                self._is_draggable(self.current_mode))

    def _is_draggable(self, drawing_type):
        """
        Return if the drawing type is one that is temporarily drawn until 
        button release.
        """
        return drawing_type in {DrawingType.RECT, DrawingType.OVAL, 
                                    DrawingType.LINE}

    def _handle_drawing(self, event, drawing_type, drag_drawing):
        """
        Take action based on the given event.
        """
        if event.type == self.BUTTON_PRESS:
            self._handle_button_press_event(event, drawing_type, drag_drawing)
        elif event.type == self.MOTION:
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
        event_coord = event.x, event.y
        drawing = Drawing(drawing_type, self.current_thickness, 
                            self.start_pos + event_coord)

        if drag_drawing:
            self.view.clear_drawing_by_id(self.last_drawing_id)
        else:
            if self.connection is not None:
                self.connection.add_to_send_queue(drawing)
            self.start_pos = event_coord

        drawing_id = self.view.draw_shape(drawing)
        self.last_drawing_id = drawing_id

    def _handle_button_release_event(self, event, drawing_type, drag_drawing):
        """
        """
        drawing = Drawing(drawing_type, self.current_thickness, 
                            self.start_pos + (event.x, event.y))

        if self.connection is not None:
            self.connection.add_to_send_queue(drawing)

        if drag_drawing:
            self.view.clear_drawing_by_id(self.last_drawing_id)

        self.view.draw_shape(drawing)
        self.start_pos = None
        self.last_drawing_id = None
