from logging    import getLogger
from queue      import Queue
from selectors  import DefaultSelector, EVENT_READ
from socket     import socket, timeout, SO_REUSEADDR, SOL_SOCKET
from struct     import calcsize, pack, unpack
from threading  import Lock, Thread
from time       import sleep


class Connection:
    """
    Provides a multi-threaded interface for socket I/O without blocking the 
    thread of execution utilizing the Connection.
    """

    HEADER_VERSION = 1
    HEADER_PACK_STR = "II"      # version, length
    HEADER_SIZE = calcsize(HEADER_PACK_STR)

    CONNECT_ATTEMPTS = 3
    SELECT_TIMEOUT_INTERVAL = 0.3

    def __init__(self):
        self.socket = None
        self.socket_lock = None
        self.send_queue = None

    def startup(self, port, ip_address = None, callback = None):
        """
        Start a thread to either accept a connection or attempt to connect to 
        a peer.
        """
        if self.socket is None:
            if ip_address is None:
                thread_target = self._wait_for_connection
            else:
                thread_target = self._connect_to_peer

            t = Thread(target = thread_target, args = (port, ip_address))
            t.start()

            if callback is None:
                t.join()
            else:
                callback()

    def _wait_for_connection(self, port, *args):
        """
        Open a listening socket to wait for incoming peer connection.
        """
        getLogger(__name__).info("Waiting for connection on port {}..."
                                    .format(port))
        listener = self._create_new_socket()
        listener.bind(("", port))
        listener.listen(1)
        conn, addr = listener.accept()

        self._set_socket(conn)
        getLogger(__name__).info("Connected to peer at {}:{}"
                                    .format(addr[0], addr[1]))

    def _connect_to_peer(self, port, ip_address):
        """
        Create a socket and attempt to connect to a waiting peer.
        """
        getLogger(__name__).info("Attempting to connect to peer {}:{}..."
                                    .format(ip_address, port))
        conn = self._create_new_socket()
        connected = False

        for i in range(self.CONNECT_ATTEMPTS):
            try:
                conn.connect((ip_address, port))
                connected = True
                break
            except (ConnectionRefusedError, OSError):
                getLogger(__name__).info("Attempt {}/{} failed"
                                            .format(i + 1, self.CONNECT_ATTEMPTS))
                if i < self.CONNECT_ATTEMPTS:
                    sleep(i + 1)

        if connected:
            self._set_socket(conn)
            getLogger(__name__).info("Connection established")
        else:
            getLogger(__name__).info(("Connection could not be established, "
                                        "starting in offline mode."))

    def _set_socket(self, socket):
        """
        Change any options needed to the socket and initialize the other data 
        structures needed for sending and receiving.
        """
        socket.setblocking(False)
        self.socket = socket
        self.socket_lock = Lock()
        self.send_queue = Queue()

    def _create_new_socket(self):
        """
        Return a socket with the re-use option set.
        """
        sock = socket()
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, True)
        return sock

    def start(self, receive_callback):
        """
        Begin the sending and receiving threads for normal operation.
        """
        if self.socket is not None:
            Thread(target = self._send).start()
            Thread(target = self._receive, args = (receive_callback,)).start()

    def close(self):
        """
        Release resources held by the connection, putting it back into an 
        uninitialized state.
        """
        if self.socket is not None:
            self.socket.close()
            self.socket = None
            self.socket_lock = None

            # help blocking send thread close
            self.send_queue.put(None)
            self.send_queue = None
            getLogger(__name__).info("Connection closed.")

    def add_to_send_queue(self, data):
        """
        Add the given data to the queue to be sent.
        """
        if self.socket is not None:
            self.send_queue.put(data)

    def _send(self):
        """
        Loop retrieving data from the send queue and sending it on the socket.
        """
        while self.socket is not None:
            try:
                data = self._get_data_from_send_queue()
                if self.socket is not None:
                    header = self._create_data_header(data)
                    with self.socket_lock:
                        self.socket.sendall(header + data)
            except Exception as err:
                getLogger(__name__).debug(("Unexpected exception occurred,"
                                            " send thread may be in a"
                                            " corrupted state\n"
                                            "Error: {}".format(err)))

    def _get_data_from_send_queue(self):
        """
        Retrieve data from the queue.  If there are more than a single item, 
        batch retrieve them to improve throughput.
        """
        size = self.send_queue.qsize()
        if size > 1:
            data = b''.join([self.send_queue.get() for _ in range(size)])
        else:
            data = self.send_queue.get()
        return data

    def _create_data_header(self, data):
        """
        Create a bytes header for variable-sized data messages.
        """
        return pack(self.HEADER_PACK_STR, self.HEADER_VERSION, len(data))

    def _receive(self, callback):
        """
        Loop reading data from the socket and passing it to the callback.
        """
        selector = DefaultSelector()
        selector.register(self.socket, EVENT_READ)

        while self.socket is not None:
            try:
                _ = selector.select(self.SELECT_TIMEOUT_INTERVAL)
                header = self.socket.recv(self.HEADER_SIZE)
                if header:
                    data = self._read_data(header)
                    callback(data)
                else:   # connection closed from other end
                    self.close()
            except Exception as err:
                getLogger(__name__).debug(("Unexpected exception occurred,"
                                            " receive thread may be in a"
                                            " corrupted state\n"
                                            "Error: {}".format(err)))

    def _read_data(self, header):
        """
        Use the header to read the body of the message from the socket.
        """
        # TODO: Handle version number in potential later versions
        _, msg_size = unpack(self.HEADER_PACK_STR, header)
        data = self.socket.recv(msg_size)
        return data
