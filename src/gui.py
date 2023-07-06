import os
from argparse import ArgumentParser
from tkinter import *
from tkinter import ttk
import subprocess

def purgeFiles(path_query:set) -> bool:
    for path in path_query:
        try:
            os.remove(path)
        except OSError as err:
            print(f"Error while removing {path}: {err}")
            return False
    return True

class TkWindow(Tk):
    def __init__(self, title:str="", geometry:str="500x500"):
        super().__init__()
        self.title(title)
        self.geometry(geometry)

        mainframe_style = ttk.Style()
        mainframe_style.configure("gray.TFrame", background="gray")

        mainframe = ttk.Frame(self, style="gray.TFrame", padding=10)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        mainframe.grid(column=0, row=0, sticky=(N, S, E, W))

    # Outputs a visual widget hierarchy to the console, mainly for debugging
    def printHierarchy(self, w:Widget=None, depth:int=0) -> None:
        print("WINDOW HIERARCHY:")
        if w == None: w = self
        print('  ' * depth + w.winfo_class() + ' | =' + str(w.winfo_width()) + ' h='
            + str(w.winfo_height()) + ' x=' + str(w.winfo_x()) + ' y=' + str(w.winfo_y()))
        for widget in w.winfo_children():
            self.printHierarchy(widget, depth + 1)
    
class ContentFrame(ttk.Frame):
    def __init__(self, parent:Widget, bw:int=5, rt:str="flat", pad:int=10):
        super().__init__(
            parent,
            borderwidth=bw,
            relief=rt,
            padding=pad
        )
        self.grid(column=0, row=0, sticky=(N, S, E, W))
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        # Temporary, will move outside frame later
        # delButton = ttk.Button(self, text="delete", command=purgeFiles(self.scanGarbage(command)))
        # delButton.grid(column=0, row=20, sticky=(N, S, E, W))
        # Why does initializing the button also run purgeFiles()?
    
    def scanGarbage(self, cmd:str) -> set:
        try:
            completed_process = subprocess.run(
                [cmd],
                timeout=5,
                check=True,
                capture_output=True,
                encoding="utf-8"
            )
            path_set = set(completed_process.stdout.strip("\n").split("\n"))
            for i, path in enumerate(path_set):
                ttk.Checkbutton(self, text=path).grid(column=0, row=i, sticky=W)
            return path_set
        except TimeoutError:
            print("Subprocess timed out!")
        except FileNotFoundError:
            print("Could not find the subprocess file!")
        return {"ERROR"}
    
    def deleteGarbage(self) -> None:
        pass
    
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-c", "--command",
        help="the command to run",
    )
    args = parser.parse_args()
    command = args.command if args.command != None else "./main_modified.exe"

    root = TkWindow("Garbage Remover for Windows", "500x120")
    # root.printHierarchy()
    content = ContentFrame(root)
    path_set = content.scanGarbage(command)
    root.mainloop()