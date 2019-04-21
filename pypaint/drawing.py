from logging        import getLogger
from struct         import calcsize, error, pack, unpack

from .drawing_type import DrawingType


class Drawing:
    """
    Datatype for the drawings created on the canvas, used to encode them for 
    sending/receiving over a network.
    """

    # shape, thickness, # + 6 hex digits for color, 4 coord values, text length
    MSG_PACK_STR = "iI7s4iI"      
    MSG_SIZE = calcsize(MSG_PACK_STR)

    def __init__(self, shape, thickness, color, coords, text = None):
        self.shape = shape
        self.thickness = thickness
        self.color = color
        self.coords = coords
        self.text = text

    def encode(self):
        """
        Return a byte array representing this instance.
        """
        bytes_msg = None
        try:
            text_length = 0 if self.text is None else len(self.text)
            bytes_msg = pack(self.MSG_PACK_STR, self.shape.value, 
                                self.thickness, self.color.encode(), 
                                *self.coords, text_length)
            if self.text is not None:
                text_pack_str = "{}s".format(len(self.text))
                bytes_msg += pack(text_pack_str, self.text.encode())

        except error as err:    # struct.error
            getLogger(__name__).debug("Error in encoding: {}".format(err))

        return bytes_msg

    @staticmethod
    def decode_drawings(byte_array):
        """
        Return a list of the decoded drawings in the byte array.
        """
        drawings = []
        i = 0
        try:
            while i < len(byte_array):
                drawing, length = Drawing.decode_drawing(byte_array[i:])
                drawings.append(drawing)
                i += length
            assert i == len(byte_array) # decoded all drawings exactly as sent

        except (ValueError, error) as err:  # struct.error
            getLogger(__name__).debug("Error in decoding: {}".format(err))
        except AssertionError as err:
            getLogger(__name__).debug("Error decoding, decoded length does "
                                    "not match byte length\n Decoded - "
                                    "{} bytes - {}".format(i, len(byte_array)))
        return drawings

    @staticmethod
    def decode_drawing(byte_array):
        """
        Return a Drawing instance, and its length, using the data from the 
        byte array.
        """
        drawing = None
        length = Drawing.MSG_SIZE
        shape_val, thickness, color, *coords, text_length = unpack(
                                                Drawing.MSG_PACK_STR, 
                                                byte_array[:Drawing.MSG_SIZE])
        text = None
        if text_length > 0:
            # [0].decode() because unpack will always returns a singleton 
            # list of a bytes object
            text = unpack(str(text_length) + "s", 
                            byte_array[Drawing.MSG_SIZE:])[0].decode()
            length += text_length

        drawing = Drawing(DrawingType(shape_val), thickness, color.decode(), 
                            coords, text)
        return drawing, length

    def __str__(self):
        return "{}:{}:{}:{}:{}".format(self.shape, self.thickness, self.color, 
                                    self.coords, self.text)

    def __eq__(self, other):
        equal = False
        if isinstance(self, other.__class__):
            equal = (self.shape == other.shape
                        and self.thickness == other.thickness
                        and self.color == other.color
                        and tuple(self.coords) == tuple(other.coords))
            if self.text is not None:
                equal = equal and self.text == other.text
        return equal

    def __hash__(self):
        return hash((self.shape, self.thickness, tuple(self.coords), 
                        self.text))
