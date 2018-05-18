from functools import total_ordering
from struct import pack, unpack

from pypaint.shape_type import ShapeType


@total_ordering
class Drawing:
    """
    """

    MSG_SIZE = 28
    PACK_STR = "d5i"

    def __init__(self, timestamp, shape, coords):
        self.timestamp = timestamp
        self.shape = shape
        self.coords = coords

    def encode(self):
        """
        Return a byte array representing this instance.
        """
        return pack(self.PACK_STR, self.timestamp, self.shape.value, 
                        *self.coords)

    @staticmethod
    def decode(byte_array):
        """
        Return a Drawing instance using the data from the byte array.
        """
        timestamp, shape_val, *coords = unpack(Drawing.PACK_STR, byte_array)
        return Drawing(timestamp, ShapeType(shape_val), coords)
        
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
