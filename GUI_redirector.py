import tkinter as tk
class GUI_Redirector:
    def __init__(self, console_text_widget):
        self.console_text_widget = console_text_widget

    def write(self, msg):
        self.console_text_widget.insert(tk.END, msg)

    def flush(self):
        pass