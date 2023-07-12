"""
This module is not intended for use anywhere except within the Garbage Removeinator
project. Meant to hold the GUI code used in the main script, which should exist in the
same directory as this file.
"""

from typing import Callable
from tkinter import *
from tkinter import ttk
import customTk

# I only imported typing.Callable to use it as a type hint
class GarbageRemoveinatorUI(ttk.Frame):
    def __init__(self, parent:Widget, refreshfunc:Callable, deletefunc:Callable,
                 padding:int=15):
        super().__init__(parent, padding=padding)
        self.grid(column=0, row=0, sticky=(N, S, E, W))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        ### MAIN FRAME ###
        self.label = ttk.Label(self, text="Select the file(s) you want to delete below:")
        self.label.grid(column=0, row=0, sticky=W)

        ### PATHS FRAME ###
        self.paths_frame = ttk.Frame(self, borderwidth=5, padding=(0, 5, 0, 5))
        self.paths_frame.grid(column=0, row=1, sticky=(N, S, W, E))

        self.path_listbox = customTk.MultiSelectListbox(self.paths_frame)
        self.path_listbox.grid(column=0, row=0, sticky=(N, S, W, E))
        self.paths_frame.columnconfigure(0, weight=1)
        self.paths_frame.rowconfigure(0, weight=1)

        self.listbox_scroll = ttk.Scrollbar(
            self.paths_frame,
            orient=VERTICAL,
            command=self.path_listbox.yview
        )
        self.path_listbox.configure(yscrollcommand=self.listbox_scroll.set)
        self.listbox_scroll.grid(column=1, row=0, sticky=(N, S))

        ### BUTTONS FRAME ###
        self.buttons_frame = ttk.Frame(self)
        self.buttons_frame.grid(column=0, row=2, sticky=(W, E))
        
        self.select_button = ttk.Button(
            self.buttons_frame,
            text="Select all",
            command=self.path_listbox.selectAll
        )
        self.select_button.grid(column=0, row=0, sticky=W)

        self.deselect_button = ttk.Button(
            self.buttons_frame,
            text="Deselect all",
            command=self.path_listbox.deselectAll
        )
        self.deselect_button.grid(column=1, row=0, sticky=W)

        self.refresh_button = ttk.Button(
            self.buttons_frame,
            text="Refresh list",
            command=refreshfunc
        )
        self.refresh_button.grid(column=2, row=0, sticky=W)

        self.delete_button = ttk.Button(
            self.buttons_frame,
            text="Delete selected files",
            command=deletefunc
        )
        self.delete_button.grid(column=3, row=0, sticky=E)
        self.buttons_frame.columnconfigure(3, weight=1)