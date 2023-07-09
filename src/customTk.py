"""
Module of custom Tk classes made by Raymond Chen.
"""

from tkinter import *
from tkinter import ttk

class TkWindow(Tk):
    def __init__(self, title:str="Tk", geometry:str="500x500", padding:int=0):
        super().__init__()
        self.title(title)
        self.geometry(geometry)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.mainframe = ttk.Frame(self, padding=padding)
        self.mainframe.grid(column=0, row=0, sticky=(N, S, E, W))
    
    # Acts as a wrapper for all widgets in the root window
    def getMainframe(self) -> ttk.Frame:
        return self.mainframe

    # Outputs a visual widget hierarchy to the console, mainly for debugging
    def printHierarchy(self, w:Widget=None, depth:int=0) -> None:
        if w == None: w = self
        print('  ' * depth + w.winfo_class() + ' | =' + str(w.winfo_width()) + ' h='
            + str(w.winfo_height()) + ' x=' + str(w.winfo_x()) + ' y=' + str(w.winfo_y()))
        for widget in w.winfo_children():
            self.printHierarchy(widget, depth + 1)

class MultiSelectListbox(Listbox):
    def __init__(self, parent:Widget, listvar:list, height:int=10):
        super().__init__(parent, selectmode=EXTENDED, listvariable=StringVar(value=listvar), height=height)
        self.content_list = listvar
        self.last_selected = ()
        self.bind("<<ListboxSelect>>", self.selectHandler)

    def selectHandler(self, *args) -> None:
        for i in self.last_selected:
            self.selection_set(i)
        self.last_selected = self.curselection()

    def selectAll(self) -> None:
        self.selection_set(0, len(self.content_list))
        self.last_selected = self.curselection()
    
    def deselectAll(self) -> None:
        self.selection_clear(0, len(self.content_list))
        self.last_selected = ()