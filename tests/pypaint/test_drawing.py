from unittest               import TestCase

from pypaint.drawing        import Drawing
from pypaint.drawing_type   import DrawingType


class TestDrawing(TestCase):
    
    def setUp(self):
        self.drawing = Drawing(DrawingType.RECT, 0, [0, 0, 1, 1])
        self.text_drawing = Drawing(DrawingType.TEXT, 0, [0, 0, 0, 0], "testing")

    def test_encoding_decoding_are_equal(self):
        bytes_array = self.drawing.encode()
        decoded, decoded_length = Drawing.decode_drawing(bytes_array)
        self.assertEqual(len(bytes_array), decoded_length)
        self.assertEqual(self.drawing, decoded)

    def test_decoding_multiple_drawings(self):
        bytes_array = self.drawing.encode() + self.text_drawing.encode()
        decoded = Drawing.decode_drawings(bytes_array)
        self.assertEqual(decoded[0], self.drawing)
        self.assertEqual(decoded[1], self.text_drawing)

    def test_decoding_text(self):
        bytes_array = self.text_drawing.encode()
        decoded, decoded_length = Drawing.decode_drawing(bytes_array)
        self.assertEqual(len(bytes_array), decoded_length)
        self.assertEqual(self.text_drawing, decoded)
