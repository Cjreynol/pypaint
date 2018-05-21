from queue import Queue
from socket import socket, timeout, SO_REUSEADDR, SOL_SOCKET
from threading import Lock, Thread
from time import sleep, time

from pypaint.drawing import Drawing


class Connection:
    """
    Manages the peer connection between two clients.
    """

    SLEEP_DURATION = 0.01
    CLOSE_MSG = "close"

    def __init__(self, is_host, port, peer_ip = None):
        """
        Initialize the state needed for data sending, then create/connect the 
        socket.
        """
        self.done = False
        self.socket_lock = Lock()
        self.send_queue = Queue()

        self.receive_callback = None

        if is_host:
            self.socket = self._wait_for_peer(port)
        elif not is_host and peer_ip is not None:
            self.socket = self._connect_to_peer(peer_ip, port)
        else:
            raise RuntimeError("Proper arguments not provided.")
    
    def start(self, receive_callback):
        """
        Start the send and receive threads.
        """
        self.receive_callback = receive_callback
        Thread(target = self._send, args = (self.socket_lock,)).start()
        Thread(target = self._receive, args = (self.socket_lock,)).start()

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

    def close(self):
        """
        Put the connection in a final state.
        """
        self.done = True
        self.send_queue.put(self.CLOSE_MSG)
        self.socket.close()

    def add_to_send_queue(self, shape, thickness, coords):
        """
        Create and add the new drawing to the send queue.
        """
        drawing = Drawing(time(), shape, thickness, coords)
        self.send_queue.put(drawing)

    def _send(self, socket_lock):
        """
        Loop getting drawings from the queue and sending them to the peer 
        connection.
        """
        while not self.done:
            size = self.send_queue.qsize()
            if size > 1:    # clear out the queue and send the batch
                drawings = [self.send_queue.get() for _ in range(size)]
            else:
                drawings = [self.send_queue.get()]

            drawings_bytes = b''.join([x.encode() for x in drawings])
            msg = Drawing.create_header(drawings_bytes) + drawings_bytes

            with socket_lock:
                self.socket.sendall(msg)

    def _receive(self, socket_lock):
        """
        Loop attempting to receive drawings from the peer connection.
        """
        while not self.done:
            with socket_lock:
                try:
                    header_bytes = self.socket.recv(Drawing.HEADER_SIZE)
                    _, remaining_bytes = Drawing.decode_header(header_bytes)
                    drawing_bytes = self.socket.recv(remaining_bytes)
                except (BlockingIOError, timeout):
                    sleep(self.SLEEP_DURATION)
                    continue
            drawings = Drawing.decode_drawings(drawing_bytes)

            for drawing in drawings:
                self.receive_callback(drawing)
