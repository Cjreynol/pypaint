from tkinter import Button, Entry, Label, Tk


class SetupView:
    """
    Manages the Tkinter window for accepting options to start a PyPaint 
    instance.
    """

    WINDOW_TITLE = "PyPaint"
    IP_LABEL_TEXT = "Enter IP address:"
    PORT_LABEL_TEXT = "Enter Port:"
    HOST_BUTTON_TEXT = "Host"
    CONNECT_BUTTON_TEXT = "Connect"
    OFFLINE_BUTTON_TEXT = "Offline"

    def __init__(self):
        """
        Create the Tkinter window, then create and place the widgets in it.
        """
        self.root = self._create_root()
        self._initialize_widgets()
        self._place_widgets()

    def _create_root(self):
        """
        Return the root window with the proper attributes set.
        """
        root = Tk()
        root.title(self.WINDOW_TITLE)
        return root

    def _initialize_widgets(self):
        """
        Instantiate the widgets for the GUI.
        """
        self.ip_label = Label(self.root, text = self.IP_LABEL_TEXT)
        self.ip_entry = Entry(self.root)
        self.port_label = Label(self.root, text = self.PORT_LABEL_TEXT)
        self.port_entry = Entry(self.root)
        self.host_button = Button(self.root, text = self.HOST_BUTTON_TEXT)
        self.connect_button = Button(self.root, 
                                        text = self.CONNECT_BUTTON_TEXT)
        self.offline_button = Button(self.root, 
                                        text = self.OFFLINE_BUTTON_TEXT)

    def _place_widgets(self):
        """
        Use a geometry manager to put the widgets in the root window.
        """
        self.ip_label.grid(row = 0, column = 0)
        self.ip_entry.grid(row = 0, column = 1)
        self.port_label.grid(row = 1, column = 0)
        self.port_entry.grid(row = 1, column = 1)
        self.host_button.grid(row = 2, column = 1)
        self.connect_button.grid(row = 2, column = 2)
        self.offline_button.grid(row = 2, column = 3)

    def start(self):
        """
        Start the GUI's update loop.
        """
        self.root.mainloop()

    def bind_host_button_callback(self, callback):
        """
        Register the callback for starting a hosting pypaint instance.
        """
        self.host_button["command"] = callback(self.ip_entry, self.port_entry)

    def bind_connect_button_callback(self, callback):
        """
        Register the callback for starting a peer pypaint instance.
        """
        self.connect_button["command"] = callback(self.ip_entry, self.port_entry)

    def bind_offline_button_callback(self, callback):
        """
        Register the callback for starting a non-connected pypaint instance.
        """
        self.offline_button["command"] = callback(self.ip_entry, self.port_entry)
