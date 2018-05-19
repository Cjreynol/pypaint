from unittest import TestCase

from time import time

from pypaint.drawing import Drawing
from pypaint.shape_type import ShapeType


class TestDrawing(TestCase):
    
    def setUp(self):
        self.drawing = Drawing(0, ShapeType.RECT, [0, 0, 1, 1])

    def test_encoding_decoding_are_equal(self):
        bytes_array = self.drawing.encode()
        other = Drawing.decode_drawing(bytes_array[Drawing.HEADER_SIZE:])
        self.assertEqual(self.drawing, other)
