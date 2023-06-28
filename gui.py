from tkinter import *
from tkinter import ttk
import subprocess as sp

def callSubProcess() -> None:
    obj = sp.run("./test.exe", capture_output=True)
    print(str(obj.stdout).replace(R"\r", ""))

# Base Tk window
root = Tk()
root.title("Test")

# Main content frame
mainframe = ttk.Frame(root)

# Simple button that calls a callback function
button = ttk.Button(mainframe, text="Click me to start the subprocess", command=callSubProcess)

# Places the widget(s) appropriately in the window
mainframe.grid()
button.grid()
button.columnconfigure(0, weight=1)
button.rowconfigure(0, weight=1)

root.mainloop()