from tkinter import Button, Entry, Toplevel


class TextEntryBox:
    """
    """

    def __init__(self, confirm_callback_generator, 
                    cancel_callback_generator, thickness, coords):
        window = Toplevel()
        window.title("Enter your text")

        entry = Entry(window)
        confirm = Button(window, text = "Confirm",
                            command = confirm_callback_generator(window, 
                                                                entry,
                                                                thickness, 
                                                                coords))
        cancel = Button(window, text = "Cancel", 
                            command = cancel_callback_generator(window))
        window.bind("<Return>", confirm_callback_generator(window, entry, 
                                                            thickness,
                                                            coords))
        entry.grid(row = 0, column = 0, columnspan = 2)
        entry.focus()

        confirm.grid(row = 1, column = 1)
        cancel.grid(row = 1, column = 0)
