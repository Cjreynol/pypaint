from tkinter    import Tk


class MainWindow:
    """
    A wrapper around the Tk class, MainWindow is intended to be the base 
    of an application.  It provides functionality for creating the root 
    window of the application and easily swapping out views.
    """

    WINDOW_CLOSE_EVENT = "WM_DELETE_WINDOW"

    def __init__(self, controller, window_title = "Tkinter Application", 
                    initial_view_class = None):
        """
        Store the controller for passing to later views as they are created, 
        create the root window, then an initial view if one is given.
        """
        self.controller = controller
        self.root = self._create_root(window_title)
        
        self.current_view = None
        if initial_view_class is not None:
            self._display_view(initial_view_class)

    def _create_root(self, window_title):
        """
        Create the root window with the given title, and register the 
        window close event with the controller so the application can 
        properly shut down.
        """
        root = Tk()
        root.title(window_title)
        root.protocol(self.WINDOW_CLOSE_EVENT, self.controller.stop)

        return root

    def _display_view(self, view):
        """
        Instantiate the new view with the correct arguments, then display it.
        """
        self.current_view = view(self.controller, self.root)
        self.current_view.pack()

    def set_new_view(self, new_view):
        """
        Destroy the last view and display the given view.

        TODO CJR:  Add a boolean flag or a separate method that stores the 
        last view on a stack for view history functionality.  Maybe even a 
        subclass of this to keep functionality separate and the same API.
        Needs:
        -Adding views to history when setting a new view
        -Ability to navigate forward and back in history
        -Cleanup of the entire stack(s) in destroy
        """
        self.current_view.destroy()
        self._display_view(new_view)

    def start(self):
        """
        Begin the root window's event handling loop.
        """
        self.root.mainloop()

    def destroy(self):
        """
        Destroy the window and its resources.
        """
        self.current_view.destroy()
        self.root.destroy()

    def update(self):
        """
        Force a visual update.
        """
        self.root.update()
