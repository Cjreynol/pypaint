from unittest               import TestCase
from unittest.mock          import MagicMock

from pypaint.drawing_type   import DrawingType
from pypaint.paint_state    import PaintState


class TestPaintState(TestCase):
    
    def setUp(self):
        self.state = PaintState()

    def tearDown(self):
        pass

    def test_undo_removes_from_drawing_history(self):
        """
        Test that an undo added to the history removes the last drawing in it.
        """
        test_drawing = MagicMock(shape = DrawingType.LINE)
        test_undo = MagicMock(shape = DrawingType.UNDO)

        self.state.add_last_drawing(None, test_drawing)
        self.state.add_last_drawing(None, test_undo)

        self.assertFalse(self.state.drawing_history)
