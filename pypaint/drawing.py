from functools import total_ordering
from struct import calcsize, pack, unpack

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

    def __init__(self, timestamp, shape, thickness, coords):
        self.timestamp = timestamp
        self.shape = shape
        self.thickness = thickness
        self.coords = coords
    
    def encode(self):
        """
        Return a byte array representing this instance.
        """
        return pack(self.MSG_PACK_STR, self.timestamp, self.shape.value, 
                        self.thickness, *self.coords)
        
    @staticmethod
    def create_header(msg_body):
        """
        Return a byte array representing a header for the given message body.
        """
        non_header_length = len(msg_body)
        return pack(Drawing.HEADER_PACK_STR, Drawing.HEADER_VERSION, 
                        non_header_length)

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
            timestamp, shape_val, thickness, *coords= unpack(Drawing.MSG_PACK_STR, 
                                                                byte_array)
            drawing = Drawing(timestamp, DrawingType(shape_val), thickness, 
                                coords)
        return drawing

    @staticmethod
    def decode_header(byte_array):
        """
        Return the version number and message length from the byte_array.
        """
        return unpack(Drawing.HEADER_PACK_STR, byte_array)
        
    def __lt__(self, other):
        return self.timestamp < other.timestamp

    def __eq__(self, other):
        equal = False
        if isinstance(self, other.__class__):
            return (self.timestamp == other.timestamp
                        and self.shape == other.shape
                        and self.coords == other.coords)

    def hash(self):
        return hash((self.timestamp, self.shape, self.coords))
