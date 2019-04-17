from unittest               import TestCase
from unittest.mock          import MagicMock

from pypaint.controller     import Controller
from pypaint.drawing_type   import DrawingType
from pypaint.paint_view     import PaintView


class TestController(TestCase):
    
    def setUp(self):
        self.controller = Controller()
        self.controller.window.root = MagicMock()       # supress window pop-up
        self.test_event = MagicMock(type = Controller.BUTTON_PRESS, 
                                    x = 2, y = 3, keysym = "Escape")
        self.default_pos = 1, 1

    def tearDown(self):
        self.controller.stop()

    def test_swap_views(self):
        self.controller.swap_views()
        self.assertIsInstance(self.controller.current_view, PaintView)

    def test_handle_button_press(self):
        self.controller.handle_event(self.test_event)
        self.assertEqual((self.test_event.x, self.test_event.y), 
                            self.controller.start_pos)

    def test_handle_button_press_text(self):
        self.controller.window.current_view = MagicMock()
        self.controller.current_mode = DrawingType.TEXT
        self.controller.handle_event(self.test_event)

        self.controller.current_view.create_text_entry.assert_called_once()

    def test_handle_motion_not_draggable(self):
        self.test_event.type = Controller.MOTION
        self.controller.start_pos = self.default_pos    # not None
        self.controller.swap_views()
        self.controller._enqueue = MagicMock()
        self.controller.handle_event(self.test_event)

        self.controller._enqueue.assert_called_once()
        self.assertEqual((self.test_event.x, self.test_event.y), 
                            self.controller.start_pos)

    def test_handle_motion_draggable(self):
        self.test_event.type = Controller.MOTION
        self.controller.start_pos = self.default_pos    # not None
        self.controller.swap_views()
        self.controller.current_mode = DrawingType.RECT # draggable
        self.controller._enqueue = MagicMock()
        self.controller.handle_event(self.test_event)

        self.assertEqual(self.default_pos, self.controller.start_pos)
        self.controller._enqueue.assert_not_called()

    def test_handle_motion_no_start_pos(self):
        self.test_event.type = Controller.MOTION
        self.controller.swap_views()
        self.controller.handle_event(self.test_event)

        self.assertIsNone(self.controller.last_drawing_id)

    def test_all_events_all_drawing_modes(self):
        self.controller.swap_views()
        self.controller._enqueue = MagicMock()
        event_types = [Controller.BUTTON_PRESS, Controller.MOTION, 
                        Controller.BUTTON_RELEASE, Controller.KEYPRESS]
        for drawing_mode in DrawingType:
            for event_type in event_types:
                self.test_event.type = event_type
                self.controller.current_mode = drawing_mode
                self.controller.handle_event(self.test_event)
