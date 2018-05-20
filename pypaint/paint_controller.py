
from pypaint.drawing import Drawing
from pypaint.paint_view import PaintView
from pypaint.shape_type import ShapeType


class PaintController:
    """
    Manages the View, interface event handling, and the network connection.

    If the connection does not exist(is None) then the application works solo.
    """

    BUTTON_PRESS = '4'
    BUTTON_RELEASE = '5'
    MOTION = '6'

    def __init__(self, connection):
        self.connection = connection
        self.view = self._create_view()

        self.start_pos = None
        self.last_drawing_id = None
        self.current_mode = ShapeType.RECT
            
    def _create_view(self):
        """
        Return a view with the necessary callbacks registered.
        """
        view = PaintView()
        for event_type in ["<Button-1>", "<ButtonRelease-1>", "<B1-Motion>"]:
            view.bind_canvas_callback(event_type, self.handle_event)
        view.bind_toggle_callback(self.toggle)
        view.bind_quit_callback(self.stop)
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

    def toggle(self):
        """
        Change the current drawing mode.
        """
        if self.current_mode == ShapeType.RECT:
            self.current_mode = ShapeType.LINE
        elif self.current_mode == ShapeType.LINE:
            self.current_mode = ShapeType.RECT
        else:
            raise RuntimeError("Unexpected shape type {}".format(self.current_mode))

    def handle_event(self, event):
        """
        Call the appropriate event handler based on the current drawing mode.
        """
        if self.current_mode == ShapeType.RECT:
            self._handle_event_rect(event)
        elif self.current_mode == ShapeType.LINE:
            self._handle_event_line(event)
        else:
            raise RuntimeError("Unexpected shape type {}".format(self.current_mode))

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
                self.connection.add_to_send_queue(ShapeType.RECT, self.start_pos + event_coord)
            self.view.clear_drawing_by_id(self.last_drawing_id)
            self.view.draw_rect(self.start_pos + event_coord)

            self.start_pos = None
            self.last_drawing_id = None
        elif event.type == self.MOTION:
            self.view.clear_drawing_by_id(self.last_drawing_id)
            drawing_id = self.view.draw_rect(self.start_pos + event_coord)
            self.last_drawing_id = drawing_id
        else:
            raise RuntimeError("Unexpected event type {}".format(event.type))

    def _handle_event_line(self, event):
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
            self.start_pos = None
        elif event.type == self.MOTION:
            coords = self.start_pos + event_coord
            if self.connection is not None:
                self.connection.add_to_send_queue(ShapeType.LINE, coords)
            self.view.draw_line(coords)
            self.start_pos = event_coord
        else:
            raise RuntimeError("Unexpected event type {}".format(event.type))
