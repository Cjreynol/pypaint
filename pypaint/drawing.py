from functools import total_ordering
from struct import pack, unpack


@total_ordering
class Drawing:
    """
    """

    MSG_SIZE = 123

    def __init__(self, timestamp, shape, coords):
        self.timestamp = timestamp
        self.shape = shape
        self.coords = coords

    def encode(self):
        """
        Return a byte array representing this instance.
        """
        pass

    @staticmethod
    def decode(byte_array):
        """
        Return a Drawing instance using the data from the byte array.
        """
        pass
        
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
