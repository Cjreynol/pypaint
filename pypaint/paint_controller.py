from pypaint.drawing import Drawing
from pypaint.paint_view import PaintView
from pypaint.drawing_type import DrawingType


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

    def __init__(self, connection):
        self.start_pos = None
        self.last_drawing_id = None

        self.current_mode = self.DEFAULT_DRAWING_MODE
        self.current_thickness = self.DEFAULT_THICKNESS

        self.connection = connection
        self.view = self._create_view()
            
    def _create_view(self):
        """
        Return a view with the necessary callbacks registered.
        """
        view = PaintView()
        for event_type in ["<Button-1>", "<ButtonRelease-1>", "<B1-Motion>"]:
            view.bind_canvas_callback(event_type, self.handle_event)
        view.bind_tool_button_callbacks(self.set_mode_generator(DrawingType.PEN),
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
        self.thickness_value = int(thickness_value)

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

        Mouse button press      - save start point for the drawing
        Mouse button drag       - potentially delete the last intermediate 
                                    drawing, then draw the next
        Mouse button release    - store the new drawing, potentially clear the 
                                    last drawing, then draw the new one
        """
        event_coord = event.x, event.y
        if event.type == self.BUTTON_PRESS:
            self.start_pos = event_coord
        elif event.type == self.MOTION:
            drawing = Drawing(drawing_type, self.thickness_value, 
                                self.start_pos + event_coord)

            if drag_drawing:
                self.view.clear_drawing_by_id(self.last_drawing_id)
            else:
                if self.connection is not None:
                    self.connection.add_to_send_queue(drawing)
                self.start_pos = event_coord

            drawing_id = self.view.draw_shape(drawing)
            self.last_drawing_id = drawing_id
        elif event.type == self.BUTTON_RELEASE:
            drawing = Drawing(drawing_type, self.thickness_value, 
                                self.start_pos + event_coord)

            if self.connection is not None:
                self.connection.add_to_send_queue(drawing)

            if drag_drawing:
                self.view.clear_drawing_by_id(self.last_drawing_id)

            self.view.draw_shape(drawing)
            self.start_pos = None
            self.last_drawing_id = None
