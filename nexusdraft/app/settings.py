
from tkinter import *
from tkinter.ttk import *
import tkinter.font as tkFont
import json
import os


class Slider(Frame):
    """A Tk Scale widget that shows it's value."""
    def __init__(self, master, delegate=None):
        Frame.__init__(self, master)
        self.delegate = delegate
        right_frame = Frame(self)
        right_frame.pack(side=LEFT)
        small_font = tkFont.Font(family="Helvetica", size=10)
        self.display = Label(right_frame, text="0.00", font=small_font)
        self.display.pack()
        self.slider = Scale(right_frame, from_=0, to=4, command=self.set_display)
        self.slider.pack()

    def set_display(self, event):
        self.display.configure(text="{:.2f}".format(self.slider.get()))
        if self.delegate is not None:
            self.delegate(self.slider.get())

    def set(self, i):
        self.slider.set(i)
        self.display.configure(text="{:.2f}".format(i))

    def get(self):
        return self.slider.get()


DEFAULT_SETTING = {
    "grade_model": "std",
    "allow_empty_bans": True,
    "region": 1,
    "team_league": False,
    "meta_script": "default"

}


class SettingsManager:
    """Manage the settings and spawn SettingsWindows."""
    def __init__(self):
        os.system("touch data/settings.json")
        self.data_table = {}
        self.load_settings()

    def load_settings(self):
        try:
            with open("data/settings.json", "r") as file:
                data = json.load(file)
                self.data_table = data
        except Exception:
            self.reset()
            self.save_settings()

    def save_settings(self):
        with open("data/settings.json", "w") as file:
            json.dump(self.data_table, file)

    def get(self, key):
        try:
            return self.data_table[key]
        except KeyError:
            return DEFAULT_SETTING[key]

    def set(self, key, value):
        self.data_table[key] = value

    def set_and_save(self, key, value):
        self.data_table[key] = value
        self.save_settings()

    def setf(self, key):
        return lambda x, k=key: self.set(k, x)

    def reset(self):
        self.data_table = DEFAULT_SETTING

    def spawn_window(self):
        SettingsWindow(self).mainloop()



class SettingsWindow(Tk):
    """A window that allows the user to change the settings of this program."""
    def __init__(self, manager):
        Tk.__init__(self)
        self.manager = manager
        self.title("Settings")
        main_frame = Frame(self)
        main_frame.pack(expand=True, fill=BOTH, ipadx=10, ipady=10)
        title_font = tkFont.Font(family="Helvetica", size=24)
        Label(main_frame, text="Settings", font=title_font).pack(pady=10)

        frame0 = Frame(main_frame)
        frame0.pack(pady=5)

        frame2 = LabelFrame(frame0, text="Grade Model")
        frame2.pack(pady=5, side=LEFT, padx=10)

        grade_strings = [("std", "Standard"), ("exp", "Player Experience"), ("wr", "Win Rate"), ("uni", "Counter Only")]

        self.grade_model = StringVar(self, value=self.manager.get("grade_model"))
        buttons = [Radiobutton(frame2, variable=self.grade_model, value=i, text=j,
                            command=self.set_grade_model) for i, j in grade_strings]
        for i in buttons:
            i.pack(anchor=W)

        self.bind("<Destroy>", lambda x: manager.save_settings())

    def set_grade_model(self):
        self.manager.set("grade_model", self.grade_model.get())

    def on_reset(self):
        """Reset the settings"""
        self.manager.reset()
        self.destroy()
        self.manager.spawn_window()
