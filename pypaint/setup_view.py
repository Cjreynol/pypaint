from tkinter    import Button, Entry, Label

from .view      import View


class SetupView(View):
    """
    View for setting initial options of the program.
    """

    DEFAULT_PORT = 2423

    def _create_widgets(self):
        self.ip_label = Label(self, text = "Enter IP:")
        self.ip_entry = Entry(self)
        self.port_label = Label(self, text = "Enter Port:")
        self.port_entry = Entry(self)
        self.port_entry.insert(0, str(self.DEFAULT_PORT))

        self.host_button = Button(self, text = "Host")
        self.connect_button = Button(self, text = "Connect")
        self.offline_button = Button(self, text = "Offline")

    def _arrange_widgets(self):
        self.ip_label.grid(row = 0, column = 0)
        self.ip_entry.grid(row = 0, column = 1, columnspan = 2)
        self.port_label.grid(row = 1, column = 0)
        self.port_entry.grid(row = 1, column = 1, columnspan = 2)
        self.host_button.grid(row = 2, column = 1)
        self.connect_button.grid(row = 2, column = 2)
        self.offline_button.grid(row = 2, column = 0)

    def _bind_actions(self):
        self.offline_button["command"] = self.controller.swap_views
        self.host_button["command"] = self.controller.get_host_callback(
                                                            self.port_entry)
        self.connect_button["command"] = self.controller.get_connect_callback(
                                                self.port_entry, self.ip_entry)
