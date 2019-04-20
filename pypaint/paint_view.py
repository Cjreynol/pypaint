from threading          import Thread
from tkinter            import BOTH, LEFT, RIGHT

from chadlib.gui        import TextEntryDialog, View

from .drawing_type      import DrawingType
from .paint_canvas      import PaintCanvas
from .toolbar           import Toolbar


class PaintView(View):

    def _create_widgets(self):
        self.canvas = PaintCanvas(self.controller, self, 
                                    self.application_state)
            
        self.toolbar = Toolbar(self.controller, self, self.application_state)

    def _arrange_widgets(self):
        self.canvas.pack(side = RIGHT, fill = BOTH, expand = True)
        self.toolbar.pack(side = LEFT, fill = BOTH, expand = True)

    def start_processing_draw_queue(self):
        def f():
            while self.application_state.active:
                drawing = self.application_state.draw_queue.get()
                if drawing is not None:
                    self.draw_shape(drawing)
        Thread(target = f).start()

    def draw_shape(self, drawing):
        """
        Call the appropriate draw call based on the drawing type
        """
        drawing_id = None
        if drawing.shape == DrawingType.PEN:
            drawing_id = self.canvas.draw_line(drawing.coords, 
                                                drawing.thickness)
        elif drawing.shape == DrawingType.RECT:
            drawing_id = self.canvas.draw_rect(drawing.coords, 
                                                drawing.thickness)
        elif drawing.shape == DrawingType.OVAL:
            drawing_id = self.canvas.draw_oval(drawing.coords, 
                                                drawing.thickness)
        elif drawing.shape == DrawingType.LINE:
            drawing_id = self.canvas.draw_line(drawing.coords, 
                                                drawing.thickness)
        elif drawing.shape == DrawingType.ERASER:
            drawing_id = self.canvas.draw_eraser_line(drawing.coords, 
                                                        drawing.thickness)
        elif drawing.shape == DrawingType.PING:
            drawing_id = self.canvas.draw_ping(drawing.coords, 
                                                drawing.thickness)
        elif drawing.shape == DrawingType.CLEAR:
            drawing_id = self.canvas.clear_canvas()
        elif drawing.shape == DrawingType.TEXT:
            drawing_id = self.canvas.draw_text(drawing.coords, 
                                                drawing.thickness, 
                                                drawing.text)
        return drawing_id

    def clear_drawing_by_id(self, drawing_id):
        """
        Delete the drawing with the given id from the canvas.
        """
        self.canvas.clear_drawing_by_id(drawing_id)

    def create_text_entry(self, coords):
        TextEntryDialog("Enter text to display", self.controller.create_text, 
                        coords)
