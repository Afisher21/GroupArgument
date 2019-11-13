#!python3
import tkinter as tk

class SurveyAnswer(object):
    def __init__(self, response, count):
        self.response = response
        self.count = count

class FullScreenApp(object):
    # Shamelessly stolen from https://stackoverflow.com/questions/7966119/display-fullscreen-mode-on-tkinter
    def __init__(self, master, **kwargs):
        self.master=master
        self.frame = tk.Frame(self.master)
        self.frame.pack()
        self.master.bind("<F11>", self.toggle_fullscreen)
        self.master.bind("<Escape>", self.exit_fullscreen)
        self.state = False
        self.toggle_fullscreen()

    def toggle_fullscreen(self, event=None):
        self.state = not self.state
        self.master.attributes("-fullscreen", self.state)
        return "break"
    
    def exit_fullscreen(self, event=None):
        self.state = False
        self.master.attributes("-fullscreen", False)
        return "break"