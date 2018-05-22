from functools import total_ordering
from struct import calcsize, error, pack, unpack
from time import time

from pypaint.drawing_type import DrawingType


@total_ordering
class Drawing:
    """
    Datatype for the drawings created on the canvas, used to encode them for 
    sending/receiving over a network.
    """

    HEADER_VERSION = 1
    HEADER_PACK_STR = "II"
    HEADER_SIZE = calcsize(HEADER_PACK_STR)

    MSG_PACK_STR = "diI4i"
    MSG_SIZE = calcsize(MSG_PACK_STR)

    def __init__(self, shape, thickness, coords, timestamp = None):
        self.shape = shape
        self.thickness = thickness
        self.coords = coords

        self.timestamp = timestamp
        if self.timestamp is None:
            self.timestamp = time()
    
    def encode(self):
        """
        Return a byte array representing this instance.
        """
        try:
            bytes_msg = pack(self.MSG_PACK_STR, self.timestamp, self.shape.value, 
                                self.thickness, *self.coords)
        except error as err:    # struct.error
            print("Error in encoding: {}".format(err))
            bytes_msg = b''

        return bytes_msg
        
    @staticmethod
    def create_header(msg_body):
        """
        Return a byte array representing a header for the given message body.
        """
        non_header_length = len(msg_body)
        try:
            bytes_header = pack(Drawing.HEADER_PACK_STR, 
                                    Drawing.HEADER_VERSION, non_header_length)
        except error as err:    # struct.error
            print("Error in creating header: {}".format(err))
            bytes_header = b''

        return bytes_header

    @staticmethod
    def decode_drawings(byte_array):
        """
        Return a list of the decoded drawings in the byte array.
        """
        drawings = []
        for i in range(len(byte_array) // Drawing.MSG_SIZE):
            msg_start = i * Drawing.MSG_SIZE
            msg_end = msg_start + Drawing.MSG_SIZE
            drawings.append(Drawing.decode_drawing(byte_array[msg_start:msg_end]))
        return drawings

    @staticmethod
    def decode_drawing(byte_array):
        """
        Return a Drawing instance using the data from the byte array.
        """
        drawing = None
        if len(byte_array) == Drawing.MSG_SIZE:
            try:
                timestamp, shape_val, thickness, *coords= unpack(
                                                        Drawing.MSG_PACK_STR, 
                                                        byte_array)
                drawing = Drawing(DrawingType(shape_val), thickness, 
                                coords, timestamp)
            except (ValueError, error) as err:  # struct.error
                print("Error in decoding: {}".format(err))
        return drawing

    @staticmethod
    def decode_header(byte_array):
        """
        Return the version number and message length from the byte_array.
        """
        header = None
        try:
            header =  unpack(Drawing.HEADER_PACK_STR, byte_array)
        except error as err:    # struct.error
            print("Error in decoding header: {}".format(err))
        
        return header

    def __lt__(self, other):
        return self.timestamp < other.timestamp

    def __eq__(self, other):
        equal = False
        if isinstance(self, other.__class__):
            return (self.timestamp == other.timestamp
                        and self.shape == other.shape
                        and self.thickness == other.thickness
                        and self.coords == other.coords)

    def hash(self):
        return hash((self.timestamp, self.shape, self.thickness, self.coords))
