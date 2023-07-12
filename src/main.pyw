"""
Garbage Removeinator
By Raymond Chen

The purpose of this program is to scan for and assist in the deletion of any possible
leftover "garbage" installer files, each of which have likely been used to install a
program and no longer serves purpose.

By displaying these installers' paths together in one window, this program eliminates the
hassle of manually searching the File Explorer for clutter and offers a powerful,
easy-to-use interface for removing them in just a few clicks.
"""

import sys
import os
import subprocess
from tkinter import *
from tkinter import messagebox
import customTk
import mainUI

# When running a one-file build, any resource files used by the program are unpacked
# into a temp directory referenced by sys._MEIPASS. This function is necessary to
# translate paths used during development into paths usable by the build.
def getResourcePath(rel_path:str) -> str:
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, rel_path)

# All graphic elements are defined in the mainUI module, this class is a wrapper for the
# interface and provides callback functions for the buttons.
class GarbageRemoveinator(mainUI.GarbageRemoveinatorUI):
    def __init__(self, parent:Widget, scancommand:str, datafile:str):
        self.scan_cmd = scancommand
        self.data_file = datafile
        super().__init__(
            parent=parent,
            refreshfunc=self.refreshListbox,
            deletefunc=self.deleteHandler
        )
        # Initial garbage scan
        path_list = self.scanGarbage(self.scan_cmd)
        if len(path_list) == 0:
            messagebox.showinfo(
                title="All clear!",
                message="No trash detected. I guess you can close this program now?"
            )
        self.path_listbox.setContent(content_list=path_list)

    def refreshListbox(self) -> None:
        path_list = self.scanGarbage(self.scan_cmd)
        if path_list == self.path_listbox.getContent():
            dialog_msg = "No new possible trash detected."
        else:
            dialog_msg = "List has been updated with new possible trash."
            self.path_listbox.setContent(path_list)
        messagebox.showinfo(
            title="Refresh list",
            message=dialog_msg
        )
    
    def scanGarbage(self, cmd:str=None, datafile:str=None) -> list:
        if cmd == None: cmd = self.scan_cmd
        if datafile == None: datafile = self.data_file
        try:
            with open(getResourcePath(datafile)) as stdin:
                completed_process = subprocess.run(
                    [getResourcePath(cmd)],
                    stdin=stdin,
                    timeout=5,
                    check=True,
                    capture_output=True, 
                    encoding="utf-8"
                )
            # Assumes the subprocess will print one valid path per newline
            if completed_process.stdout.count("\n") > 0:
                path_list = completed_process.stdout.strip("\n").split("\n")
                return path_list
            return []
        except Exception as err:
            print(f"ERROR: {err}")
            messagebox.showinfo(
                title="Scanning error",
                message=f"{err}\n\nThe program will now exit."
            )
        sys.exit(1)
    
    def deleteHandler(self) -> None:
        if len(self.path_listbox.curselection()) == 0:
            messagebox.showinfo(
                title="No file selected",
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
    scan_cmd = ".\scanutil.exe"
    data_file = ".\data.txt"
    root = customTk.TkWindow(
        title="Garbage Removeinator",
        geometry="500x275",
        centerscreen=True
    )
    content = GarbageRemoveinator(
        parent=root,
        scancommand=scan_cmd,
        datafile=data_file
    )
    # root.printHierarchy()
    root.mainloop()