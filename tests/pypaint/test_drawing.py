from unittest import TestCase

from time import time

from pypaint.drawing import Drawing
from pypaint.shape_type import ShapeType


class TestDrawing(TestCase):
    
    def setUp(self):
        self.drawing = Drawing(0, ShapeType.RECT, [0, 0, 1, 1])

    def test_encoding_decoding_is_noop(self):
        other = Drawing.decode(self.drawing.encode())
        self.assertEqual(self.drawing, other)
