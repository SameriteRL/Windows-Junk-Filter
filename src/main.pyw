import os
import subprocess
import customTk
from tkinter import *
from tkinter import ttk
from argparse import ArgumentParser

class GarbageRemovalUtilityUI(ttk.Frame):
    def __init__(self, parent:Widget, padding:int=15):
        super().__init__(parent, padding=padding)
        self.grid(column=0, row=0, sticky=(N, S, E, W))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        ### MAIN FRAME ###
        self.label = ttk.Label(self, text="Select the files you want to delete below")
        self.label.grid(column=0, row=0, sticky=W)

        ### PATHS FRAME ###
        self.paths_frame = ttk.Frame(self, borderwidth=5, padding=(0, 5, 0, 5))
        self.paths_frame.grid(column=0, row=1, sticky=(N, S, W, E))

        self.path_listbox = customTk.MultiSelectListbox(
            self.paths_frame,
            # NOTE TO SELF: Don't hardcode the executable name
            listvar=self.scanGarbage("scanGarbage.exe")
        )
        self.path_listbox.grid(column=0, row=0, sticky=(N, S, W, E))
        self.paths_frame.columnconfigure(0, weight=1)
        self.paths_frame.rowconfigure(0, weight=1)

        listbox_scroll = ttk.Scrollbar(
            self.paths_frame,
            orient=VERTICAL,
            command=self.path_listbox.yview
        )
        self.path_listbox.configure(yscrollcommand=listbox_scroll.set)
        listbox_scroll.grid(column=1, row=0, sticky=(N, S))

        ### BUTTONS FRAME ###
        self.buttons_frame = ttk.Frame(self)
        self.buttons_frame.grid(column=0, row=2, sticky=(W, E))
        
        select_button = ttk.Button(
            self.buttons_frame,
            text="Select all",
            command=self.path_listbox.selectAll
        )
        select_button.grid(column=0, row=0, sticky=W)

        deselect_button = ttk.Button(
            self.buttons_frame,
            text="Deselect all",
            command=self.path_listbox.deselectAll
        )
        deselect_button.grid(column=1, row=0, sticky=W)

        delete_button = ttk.Button(
            self.buttons_frame,
            text="Delete selected files",
            command=self.purgeSelectedFiles
        )
        delete_button.grid(column=2, row=0, sticky=E)
        self.buttons_frame.columnconfigure(2, weight=1)
    
    def getPathsFrame(self) -> ttk.Frame:
        return self.paths_frame

    def getButtonsFrame(self) -> ttk.Frame:
        return self.buttons_frame
    
    def scanGarbage(self, cmd:str) -> list:
        try:
            completed_process = subprocess.run(
                [cmd],
                timeout=5,
                check=True,
                capture_output=True, 
                encoding="utf-8"
            )
            # Assumes the subprocess will print one valid path per newline
            if completed_process.stdout.count("\n") > 0:
                path_set = completed_process.stdout.strip("\n").split("\n")
                return path_set
            return list()
        except TimeoutError:
            print("Subprocess timed out!")
        return {"ERROR"}
    
    # NOTE TO SELF: Make accessing of the listbox properties more modular
    def purgeSelectedFiles(self, *args) -> None:
        path_query = [e[1] for e in [pair for pair in
                     enumerate(self.path_listbox.getContent())
                     if pair[0] in self.path_listbox.curselection()]]
        for path in path_query:
            try:
                os.remove(path)
                print("REMOVED:", path)
            except OSError as err:
                print(f"Error while removing {path}: {err}")

if __name__ == "__main__":
    # NOTE TO SELF: Do something with this argument
    parser = ArgumentParser()
    parser.add_argument(
        "-c", "--command",
        help="the command to run",
    )
    args = parser.parse_args()
    run_cmd = args.command if args.command != None else "./scanGarbage.exe"

    root = customTk.TkWindow(title="Garbage Removeinator", geometry="500x275")
    content = GarbageRemovalUtilityUI(parent=root)
    root.printHierarchy()
    root.mainloop()