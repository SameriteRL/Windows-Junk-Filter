"""
Module of custom, general-use Tk classes.
By Raymond Chen
"""

from tkinter import *
from tkinter import ttk

class TkWindow(Tk):
    def __init__(self, title:str="Tk", geometry:str="500x500", padding:int=0,
                 includeframe:bool=False):
        super().__init__()
        self.title(title)
        self.geometry(geometry)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Creates a mainframe if specified during initialization
        if includeframe:
            self.mainframe = ttk.Frame(self, padding=padding)
            self.mainframe.grid(column=0, row=0, sticky=(N, S, E, W))
    
    # Mainframe acts as a wrapper for all widgets in the root window
    def getMainframe(self) -> Widget:
        try:
            return self.mainframe
        except:
            print("WARNING: TkWindow object has no built-in mainframe!",
                  "Defaulting to root window.")
            return self

    # Outputs a visual widget hierarchy to the console, mainly for debugging
    def printHierarchy(self, w:Widget=None, depth:int=0) -> None:
        if w == None: w = self
        print('  ' * depth + w.winfo_class() + ' | =' + str(w.winfo_width()) + ' h='
            + str(w.winfo_height()) + ' x=' + str(w.winfo_x()) + ' y=' + str(w.winfo_y()))
        for widget in w.winfo_children():
            self.printHierarchy(widget, depth + 1)

class MultiSelectListbox(Listbox):
    def __init__(self, parent:Widget, listvar:list, height:int=10):
        super().__init__(parent, selectmode=EXTENDED,
                         listvariable=StringVar(value=listvar), height=height)
        self.content_list = listvar
        self.last_selected = ()
        self.bind("<<ListboxSelect>>", self.selectHandler)

        # Colors the background of alternating items
        for i in range(0, len(self.content_list), 2):
            self.itemconfigure(i, background='#F0F0FF')

    def getContent(self) -> list:
        return self.content_list

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