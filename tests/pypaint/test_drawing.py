from unittest               import TestCase

from pypaint.drawing        import Drawing
from pypaint.drawing_type   import DrawingType


class TestDrawing(TestCase):
    
    def setUp(self):
        self.drawing = Drawing(DrawingType.RECT, 0, [0, 0, 1, 1])

    def test_encoding_decoding_are_equal(self):
        bytes_array = self.drawing.encode()
        decoded, decoded_length = Drawing.decode_drawing(bytes_array)
        self.assertEqual(len(bytes_array), decoded_length)
        self.assertEqual(self.drawing, decoded)
