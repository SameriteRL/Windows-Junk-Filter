"""
Garbage Removeinator
By Raymond Chen

The purpose of this program is to scan for and assist in the deletion of any possible
leftover installer files, each of which have likely been used to install a program and now
serves no purpose. By displaying these installers' paths together in one window, this
program eliminates the hassle of manually searching the File Explorer for clutter and
offers a powerful, easy-to-use interface for removing them in just a few clicks.
"""

import sys
import os
import subprocess
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import customTk

# When running a one-file build, any resource files used by the program are unpacked
# into a temp directory referenced by sys._MEIPASS. This function is necessary to
# translate paths used during development into paths usable by the build.
def getResourcePath(rel_path:str) -> str:
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, rel_path)

class GarbageRemovalUtilityUI(ttk.Frame):
    def __init__(self, parent:Widget, scancommand:str, padding:int=15):
        self.scan_cmd = scancommand
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

        self.path_listbox = customTk.MultiSelectListbox(
            self.paths_frame,
            listvar=self.scanGarbage(self.scan_cmd)
        )
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
            command=self.refreshListbox
        )
        self.refresh_button.grid(column=2, row=0, sticky=W)

        self.delete_button = ttk.Button(
            self.buttons_frame,
            text="Delete selected files",
            command=self.deleteHandler
        )
        self.delete_button.grid(column=3, row=0, sticky=E)
        self.buttons_frame.columnconfigure(3, weight=1)

    def refreshListbox(self) -> None:
        path_list = self.scanGarbage(self.scan_cmd)
        if path_list == self.path_listbox.getContent():
            dialog_msg = "No new possible trash detected."
        else:
            dialog_msg = "List has been updated with new possible trash."
            self.path_listbox.setContent(path_list)
        messagebox.showinfo(
            title="List Refresh",
            message=dialog_msg
        )
    
    def scanGarbage(self, cmd:str=None) -> list:
        if cmd == None: cmd = self.scan_cmd
        try:
            completed_process = subprocess.run(
                [getResourcePath(cmd)],
                timeout=10,
                check=True,
                capture_output=True, 
                encoding="utf-8"
            )
            # Assumes the subprocess will print one valid path per newline
            if completed_process.stdout.count("\n") > 0:
                path_set = completed_process.stdout.strip("\n").split("\n")
                return path_set
            return list()
        except Exception as err:
            print(err)
        return ["ERROR"]
    
    def deleteHandler(self, *args) -> None:
        if len(self.path_listbox.curselection()) == 0:
            messagebox.showinfo(
                title="Error",
                message="Please select one or more files to delete!"
            )
            return
        if messagebox.askyesno(
            title="Confirmation",
            message="Are you sure you want to delete these files?"
        ):
            path_query = [e[1] for e in [pair for pair in
                         enumerate(self.path_listbox.getContent())
                         if pair[0] in self.path_listbox.curselection()]]
            for path in path_query:
                try:
                    os.remove(path)
                    self.path_listbox.removeContent(path)
                    print(f"REMOVED: {path}")
                except OSError as err:
                    print(f"ERROR REMOVING {path}: {err}")
            print("QUERY CLEARED")
            self.path_listbox.deselectAll()
            messagebox.showinfo(
                title="Success",
                message="Files have been deleted."
            )

if __name__ == "__main__":
    run_cmd = ".\scanutil.exe"
    root = customTk.TkWindow(
        title="Garbage Removeinator",
        geometry="500x275",
        centerscreen=True
    )
    content = GarbageRemovalUtilityUI(
        parent=root,
        scancommand=run_cmd
    )
    # root.printHierarchy()
    root.mainloop()