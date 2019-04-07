from logging        import getLogger
from struct         import calcsize, error, pack, unpack

from .drawing_type import DrawingType


class Drawing:
    """
    Datatype for the drawings created on the canvas, used to encode them for 
    sending/receiving over a network.
    """

    MSG_PACK_STR = "iI4i"      # shape, thickness, 4 coord values
    MSG_SIZE = calcsize(MSG_PACK_STR)

    def __init__(self, shape, thickness, coords, text = None):
        self.shape = shape
        self.thickness = thickness
        self.coords = coords
        self.text = text

    def encode(self):
        """
        Return a byte array representing this instance.
        """
        try:
            bytes_msg = pack(self.MSG_PACK_STR, self.shape.value, 
                                self.thickness, *self.coords)
            if self.text is not None:
                text_pack_str = "I{}s".format(len(self.text))
                bytes_msg += pack(text_pack_str, len(self.text), 
                                    self.text.encode())
        except error as err:    # struct.error
            getLogger(__name__).debug("Error in encoding: {}".format(err))
            bytes_msg = b''

        return bytes_msg

    @staticmethod
    def decode_drawings(byte_array):
        """
        Return a list of the decoded drawings in the byte array.
        """
        drawings = []
        i = 0
        while i < len(byte_array):
            drawing, length = Drawing.decode_drawing(byte_array[i:])
            drawings.append(drawing)
            i += length
        assert i == len(byte_array) # decoded all drawings exactly as sent
        return drawings

    @staticmethod
    def decode_drawing(byte_array):
        """
        Return a Drawing instance, and its length, using the data from the 
        byte array.
        """
        try:
            shape_val, thickness, *coords = unpack(Drawing.MSG_PACK_STR, 
                                                byte_array[:Drawing.MSG_SIZE])
            length = Drawing.MSG_SIZE
            if len(byte_array) == Drawing.MSG_SIZE:
                text = None
            else:   
                text_len = unpack("I", 
                        byte_array[Drawing.MSG_SIZE:Drawing.MSG_SIZE + 4])[0]
                text = unpack(str(text_len) + "s", 
                                byte_array[Drawing.MSG_SIZE + 4:])[0].decode()
                length += text_len + 4  # 4 is the size in bytes of the I text length field
            drawing = Drawing(DrawingType(shape_val), thickness, coords, text)
        except (ValueError, error) as err:  # struct.error
            getLogger(__name__).debug("Error in decoding: {}".format(err))
            drawing = None
            length = 0
        return drawing, length

    def __str__(self):
        return "{}:{}:{}:{}".format(self.shape, self.thickness, self.coords, self.text)

    def __eq__(self, other):
        equal = False
        if isinstance(self, other.__class__):
            equal = (self.shape == other.shape
                        and self.thickness == other.thickness
                        and tuple(self.coords) == tuple(other.coords))
            if self.text is not None:
                equal = equal and self.text == other.text
        return equal

    def __hash__(self):
        return hash((self.shape, self.thickness, tuple(self.coords), self.text))
