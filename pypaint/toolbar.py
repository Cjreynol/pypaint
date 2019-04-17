from tkinter        import (Button, Label, Scale, 
                            BOTTOM, HORIZONTAL, RAISED, SUNKEN)

from chadlib.gui    import View

from .drawing_type  import DrawingType


class Toolbar(View):
    """
    """

    FRAME_BORDER_WIDTH = 2
    FRAME_WIDTH = 120

    def __init__(self, controller, root, default_type, min_thickness, 
                    max_thickness):
        self.current_type = default_type
        self.min_thickness = min_thickness
        self.max_thickness = max_thickness

        super().__init__(controller, root, width = self.FRAME_WIDTH, 
                            relief = RAISED, bd = self.FRAME_BORDER_WIDTH)

    def _create_widgets(self):
        self.buttons = { draw_type : Button(self, text = str(draw_type)) 
                            for draw_type in DrawingType 
                                if draw_type != DrawingType.CLEAR }
        self.buttons[self.current_type]["relief"] = SUNKEN
        self.thickness_label = Label(self, text = "Thickness")
        self.thickness_scale = Scale(self, orient = HORIZONTAL, 
                                    from_ = self.min_thickness,
                                    to = self.max_thickness)
        self.clear_button = Button(self, text = str(DrawingType.CLEAR))

    def _arrange_widgets(self):
        for button in self.buttons.values():
            button.pack()
        self.thickness_label.pack()
        self.thickness_scale.pack()
        self.clear_button.pack(side = BOTTOM)

    def _bind_actions(self):
        for draw_type, button in self.buttons.items():
            button["command"] = self._draw_button_callback(draw_type)

        self.thickness_scale["command"] = self.controller.thickness_callback
        self.clear_button["command"] = self.controller.clear_callback

    def _draw_button_callback(self, drawing_type):
        def f():
            self.buttons[self.current_type]["relief"] = RAISED
            self.current_type = drawing_type
            self.buttons[self.current_type]["relief"] = SUNKEN

            self.controller.current_mode = drawing_type
        return f
