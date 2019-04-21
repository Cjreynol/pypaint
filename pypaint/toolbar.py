from tkinter        import (Button, Label, Scale, 
                            BOTTOM, HORIZONTAL, RAISED, SUNKEN)

from chadlib.gui    import View

from .drawing_type  import DrawingType


class Toolbar(View):
    """
    """

    FRAME_BORDER_WIDTH = 2
    FRAME_WIDTH = 120

    def __init__(self, controller, root, paint_state):
        super().__init__(controller, root, paint_state, width = self.FRAME_WIDTH, 
                            relief = RAISED, bd = self.FRAME_BORDER_WIDTH)

    def _create_widgets(self):
        self.buttons = { draw_type : Button(self, text = str(draw_type)) 
                            for draw_type in DrawingType 
                                if not DrawingType.has_no_location(draw_type) }
        self.buttons[self.application_state.current_type]["relief"] = SUNKEN

        self.thickness_label = Label(self, text = "Thickness")
        self.thickness_scale = Scale(self, orient = HORIZONTAL, 
                                from_ = self.application_state.THICKNESS_MIN,
                                to = self.application_state.THICKNESS_MAX)

        self.undo_button = Button(self, text = str(DrawingType.UNDO))
        self.clear_button = Button(self, text = str(DrawingType.CLEAR))

    def _arrange_widgets(self):
        for button in self.buttons.values():
            button.pack()

        self.thickness_label.pack()
        self.thickness_scale.pack()

        self.clear_button.pack(side = BOTTOM)
        self.undo_button.pack(side = BOTTOM)

    def _bind_actions(self):
        for draw_type, button in self.buttons.items():
            button["command"] = self._draw_button_callback(draw_type)

        self.thickness_scale["command"] = self._thickness_callback
        self.undo_button["command"] = self.controller.create_undo
        self.clear_button["command"] = self.controller.create_clear

    def _thickness_callback(self, thickness_value):
        self.application_state.current_thickness = int(thickness_value)

    def _draw_button_callback(self, drawing_type):
        def f():
            self.buttons[self.application_state.current_type]["relief"] = RAISED
            self.application_state.current_type = drawing_type
            self.buttons[self.application_state.current_type]["relief"] = SUNKEN
        return f
