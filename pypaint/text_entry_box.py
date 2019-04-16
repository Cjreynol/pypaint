from tkinter import Button, Entry, Toplevel


class TextEntryBox(Toplevel):
    """
    """

    def __init__(self, controller, coords):
        super().__init__()

        self.title("Enter your text")
        self.bind("<Return>", lambda event: self._confirm())

        self.controller = controller
        self.coords = coords

        self.text_entry = Entry(self)
        self.confirm_button = Button(self, text = "Confirm", 
                                        command = self._confirm)
        self.cancel_button = Button(self, text = "Cancel", 
                                    command = self._cancel)

        self.text_entry.grid(row = 0, column = 0, columnspan = 2)
        self.text_entry.focus()

        self.confirm_button.grid(row = 1, column = 1)
        self.cancel_button.grid(row = 1, column = 0)

    def _confirm(self):
        self.controller.create_text(self.text_entry.get(), self.coords)
        self._cancel()

    def _cancel(self):
        self.destroy()
