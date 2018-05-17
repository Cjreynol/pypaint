from bisect import insort
from queue import Queue
from socket import socket, timeout, SO_REUSEADDR, SOL_SOCKET
from threading import Lock, Thread
from time import sleep, time

from pypaint.drawing import Drawing
from pypaint.paint_view import PaintView
from pypaint.shape_type import ShapeType


class PaintController:
    """
    Manages the View, drawing history, and interface event handling.
    """

    BUTTON_PRESS = '4'
    BUTTON_RELEASE = '5'
    MOTION = '6'

    SLEEP_DURATION = 0.5

    def __init__(self, is_host, port = None, peer_ip = None):
        self.view = self._create_view()
        self.history = []

        self.start_pos = None
        self.current_mode = ShapeType.RECT

        self.send_queue = Queue()

        self.socket_lock = Lock()
        self.history_lock = Lock()
        self.done = False

        if is_host and port is not None:
            self.connection = self._wait_for_peer(port)
        elif not is_host and port is not None peer_ip is not None:
            self.connection = self._connect_to_peer(peer_ip, port)
        else:
            raise RuntimeError("Proper arguments not provided.")

    def _send(self, socket_lock):
        """
        Loop getting drawings from the queue and sending them to the peer 
        connection.
        """
        while not self.done:
            drawing = self.send_queue.get()
            with socket_lock:
                self.connection.sendall(drawing.encode())

    def _receive(self, socket_lock, history_lock):
        """
        Loop attempting to receive drawings from the peer connection and 
        place them in the history.
        """
        while not self.done:
            sleep(self.SLEEP_DURATION)
            with socket_lock:
                try:
                    bytes_msg = self.connection.recv(Drawing.MSG_SIZE)
                except timeout:
                    continue
            drawing = Drawing.decode(bytes_msg)
            with history_lock:
                insort(self.history, drawing)
            
    def _wait_for_peer(self, port):
        """
        Wait for a connection on the port, then return the new socket.
        """
        listener = socket()
        listener.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        listener.bind(("", port))
        listener.listen(1)

        print("Waiting for peer to connect...")
        conn, addr = listener.accept()
        self._set_socket_options(conn)
        print("Connected to peer at {}:{}".format(addr[0], addr[1]))

        return conn

    def _connect_to_peer(self, peer_ip, port):
        """
        Return a new socket connected to the given address.
        """
        conn = socket()

        print("Connecting to peer at {}:{}...".format(peer_ip, port))
        conn.connect((peer_ip, port))
        self._set_socket_options(conn)
        print("Connected to peer")

        return conn

    def _set_socket_options(self, socket):
        """
        Set the socket to be non-blocking and to allow address re-use.
        """
        socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        socket.setblocking(False)
        return socket

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
        Start the view and the send and receive helper threads.
        """
        self.view.start()
        Thread(target = self._send, args = 
                (self.socket_lock)).start()
        Thread(target = self._receive, args = 
                (self.socket_lock, self.history_lock)).start()

    def stop(self):
        """
        Put the controller in a final state.
        """
        self.done = True
        self.connection.close()
        self.send_queue("dummy value")  # aid send thread to stop blocking

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
        Mouse button release    - store the coordinates for the rectangle, 
                                    clear the canvas, and (re)draw everything 
                                    stored in history
        Mouse button drag       - clear the canvas, redraw all of the 
                                    previous drawings, then draw but do not
                                    store the current rectangle
        """
        event_coord = event.x, event.y
        if event.type == self.BUTTON_PRESS:
            self.start_pos = event_coord
        elif event.type == self.BUTTON_RELEASE:
            self._add_to_history(ShapeType.RECT, self.start_pos + event_coord)
            self.start_pos = None
            self.view.clear_draw_shapes(self.history)
        elif event.type == self.MOTION:
            self.view.clear_draw_shapes(self.history)
            self.view.draw_rect(self.start_pos + event_coord)
        else:
            raise RuntimeError("Unexpected event type {}".format(event.type))

    def _handle_event_line(self, event):
        """
        Take action based on the given event.

        Mouse button press      - save start point for the line
        Mouse button release    - stop drawing
        Mouse button drag       - draw a line from last registered position 
                                    to the current position
        """
        event_coord = event.x, event.y
        if event.type == self.BUTTON_PRESS:
            self.start_pos = event_coord
        elif event.type == self.BUTTON_RELEASE:
            self.start_pos = None
        elif event.type == self.MOTION:
            coords = self.start_pos + event_coord
            self._add_to_history(ShapeType.LINE, coords)
            self.view.draw_line(coords)
            self.start_pos = event_coord
        else:
            raise RuntimeError("Unexpected event type {}".format(event.type))

    def _add_to_history(self, shape, coords):
        """
        """
        drawing = Drawing(time(), shape, coords)
        with self.history_lock:
            self.history.append(drawing)
        self.send_queue.put(drawing)