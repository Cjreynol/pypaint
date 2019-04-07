from tkinter    import Tk


class MainWindow:
    """
    """

    WINDOW_TITLE = "PyPaint"

    def __init__(self, controller, start_view = None):
        self.controller = controller
        self.root = self._create_root()
        
        self.view = None
        if start_view is not None:
            self.view = start_view(self.root, self.controller)
            self.view.pack()

    def _create_root(self):
        root = Tk()
        root.title(self.WINDOW_TITLE)
        root.protocol("WM_DELETE_WINDOW", self.controller.stop)
        return root

    def set_new_view(self, new_view):
        self.view.destroy()
        self.view = new_view(self.root, self.controller)
        self.view.pack()

    def start(self):
        self.root.mainloop()

    def stop(self):
        self.root.destroy()

    def update(self):
        """
        Force a visual update.
        """
        self.root.update()
