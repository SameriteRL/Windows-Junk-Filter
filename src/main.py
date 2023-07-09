import os
import subprocess
import customTk
from tkinter import *
from tkinter import ttk
from argparse import ArgumentParser

class GarbageRemovalUtilityUI(ttk.Frame):
    def __init__(self, parent:Widget):
        super().__init__(parent, padding=15)
        self.grid(column=0, row=0, sticky=(N, S, E, W))
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        ### MAIN FRAME ### 
        self.label = ttk.Label(self, text="Select the files you want to delete below")
        self.label.grid(column=0, row=0, sticky=(N, W))

        # self.paths_frame_style = ttk.Style()
        # self.paths_frame_style.configure("test.TFrame", background="green")

        ### PATHS FRAME ###
        self.paths_frame = ttk.Frame(self, borderwidth=5, relief=FLAT, padding=(0, 5, 0, 5))
        self.paths_frame.grid(column=0, row=1, columnspan=3, sticky=(N, W, E))
        self.columnconfigure(2, weight=1)

        path_listbox = customTk.MultiSelectListbox(self.paths_frame, self.scanGarbage("main_modified.exe"))
        path_listbox.grid(column=0, row=0, sticky=(W, E))
        self.paths_frame.columnconfigure(0, weight=1)

        listbox_scroll = ttk.Scrollbar(self.paths_frame, orient=VERTICAL, command=path_listbox.yview)
        path_listbox.configure(yscrollcommand=listbox_scroll.set)
        listbox_scroll.grid(column=3, row=0, sticky=(N, S))

        ### MAIN FRAME ###
        select_button = ttk.Button(self, text="Select all", command=path_listbox.selectAll)
        select_button.grid(column=0, row=2, sticky=W)

        deselect_button = ttk.Button(self, text="Deselect all", command=path_listbox.deselectAll)
        deselect_button.grid(column=1, row=2, sticky=W)

        delete_button = ttk.Button(self, text="Delete selected files")
        delete_button.grid(column=2, row=2, sticky=E)
    
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
    
    def purgeFiles(path_query:set) -> bool:
        for path in path_query:
            try:
                os.remove(path)
            except OSError as err:
                print(f"Error while removing {path}: {err}")
                return False
        return True
    
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-c", "--command",
        help="the command to run",
    )
    args = parser.parse_args()
    command = args.command if args.command != None else "./main_modified.exe"

    root = customTk.TkWindow(title="Garbage Remover for Windows", geometry="500x300")
    content = GarbageRemovalUtilityUI(parent=root.getMainframe())
    # root.printHierarchy()
    root.mainloop()