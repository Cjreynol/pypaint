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
    DEFAULT_THICKNESS = 1

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
        self.view.clear_canvas()
        if self.connection is not None:
            self.connection.add_to_send_queue(DrawingType.CLEAR, 0, 
                                                (0, 0, 0, 0))

    def handle_event(self, event):
        """
        Call the appropriate event handler based on the current drawing mode.
        """
        if self.current_mode == DrawingType.PEN:
            self._handle_event_pen(event)
        elif self.current_mode == DrawingType.RECT:
            self._handle_event_rect(event)
        elif self.current_mode == DrawingType.OVAL:
            self._handle_event_oval(event)
        elif self.current_mode == DrawingType.LINE:
            self._handle_event_line(event)
        elif self.current_mode == DrawingType.ERASER:
            self._handle_event_eraser(event)

    def _handle_event_pen(self, event):
        """
        Take action based on the given event.

        Mouse button press      - save start point for the line
        Mouse button drag       - draw a line from the last point the current 
        """
        event_coord = event.x, event.y
        if event.type == self.BUTTON_PRESS:
            self.start_pos = event_coord
        elif event.type == self.BUTTON_RELEASE:
            self.start_pos = None
        elif event.type == self.MOTION:
            coords = self.start_pos + event_coord
            if self.connection is not None:
                self.connection.add_to_send_queue(DrawingType.PEN, 
                                                    self.thickness_value,
                                                    coords)
            self.view.draw_line(coords, self.thickness_value)
            self.start_pos = event_coord

    def _handle_event_rect(self, event):
        """
        Take action based on the given event.

        Mouse button press      - save start point for the square
        Mouse button release    - store the new drawing, clear the last 
                                    intermediate rect, then draw the new one
        Mouse button drag       - delete the last intermediate rectangle, 
                                    then draw the next
        """
        event_coord = event.x, event.y
        if event.type == self.BUTTON_PRESS:
            self.start_pos = event_coord
        elif event.type == self.BUTTON_RELEASE:
            if self.connection is not None:
                self.connection.add_to_send_queue(DrawingType.RECT, 
                                                    self.thickness_value,
                                                    (self.start_pos 
                                                        + event_coord))
            self.view.clear_drawing_by_id(self.last_drawing_id)
            self.view.draw_rect(self.start_pos + event_coord, 
                                    self.thickness_value)

            self.start_pos = None
            self.last_drawing_id = None
        elif event.type == self.MOTION:
            self.view.clear_drawing_by_id(self.last_drawing_id)
            drawing_id = self.view.draw_rect(self.start_pos + event_coord, 
                                                self.thickness_value)
            self.last_drawing_id = drawing_id
    
    def _handle_event_oval(self, event):
        """
        Take action based on the given event.

        Mouse button press      - save start point for the oval
        Mouse button release    - store the new drawing, clear the last 
                                    intermediate oval, then draw the new one
        Mouse button drag       - delete the last intermediate oval, then 
                                    draw the next
        """
        event_coord = event.x, event.y
        if event.type == self.BUTTON_PRESS:
            self.start_pos = event_coord
        elif event.type == self.BUTTON_RELEASE:
            if self.connection is not None:
                self.connection.add_to_send_queue(DrawingType.OVAL, 
                                                    self.thickness_value,
                                                    (self.start_pos 
                                                        + event_coord))
            self.view.clear_drawing_by_id(self.last_drawing_id)
            self.view.draw_oval(self.start_pos + event_coord, 
                                    self.thickness_value)

            self.start_pos = None
            self.last_drawing_id = None
        elif event.type == self.MOTION:
            self.view.clear_drawing_by_id(self.last_drawing_id)
            drawing_id = self.view.draw_oval(self.start_pos + event_coord,
                                                self.thickness_value)
            self.last_drawing_id = drawing_id
    
    def _handle_event_line(self, event):
        """
        Take action based on the given event.

        Mouse button press      - save start point for the line
        Mouse button release    - store the new drawing, clear the last 
                                    intermediate line, then draw the new one
        Mouse button drag       - delete the last intermediate line, then 
                                    draw the next
        """
        event_coord = event.x, event.y
        if event.type == self.BUTTON_PRESS:
            self.start_pos = event_coord
        elif event.type == self.BUTTON_RELEASE:
            if self.connection is not None:
                self.connection.add_to_send_queue(DrawingType.LINE, 
                                                    self.thickness_value,
                                                    (self.start_pos 
                                                        + event_coord))
            self.view.clear_drawing_by_id(self.last_drawing_id)
            self.view.draw_line(self.start_pos + event_coord, 
                                    self.thickness_value)

            self.start_pos = None
            self.last_drawing_id = None
        elif event.type == self.MOTION:
            self.view.clear_drawing_by_id(self.last_drawing_id)
            drawing_id = self.view.draw_line(self.start_pos + event_coord, 
                                                self.thickness_value)
            self.last_drawing_id = drawing_id
    
    def _handle_event_eraser(self, event):
        """
        Take action based on the given event.

        Mouse button press      - save start point for the line
        Mouse button drag       - draw a line from the last point the current 
        """
        event_coord = event.x, event.y
        if event.type == self.BUTTON_PRESS:
            self.start_pos = event_coord
        elif event.type == self.BUTTON_RELEASE:
            self.start_pos = None
        elif event.type == self.MOTION:
            coords = self.start_pos + event_coord
            if self.connection is not None:
                self.connection.add_to_send_queue(DrawingType.ERASER, 
                                                    self.thickness_value,
                                                    coords)
            self.view.draw_eraser_line(coords, self.thickness_value)
            self.start_pos = event_coord
