import tkinter as tk
from pathlib import Path
from tkinter import *


def open_file_active():
    file_path = Path("Active Exploitation.txt")
    if file_path:
        with open(file_path, 'r') as file:
            content = file.read()
            text_widget.delete(1.0, tk.END)  # Clear previous content
            text_widget.insert(tk.END, content)

def open_file_demonstrated():
    file_path = Path("Demonstrated.txt")
    if file_path:
        with open(file_path, 'r') as file:
            content = file.read()
            text_widget.delete(1.0, tk.END)  # Clear previous content
            text_widget.insert(tk.END, content)

def open_file_hypothetical():
    file_path = Path("Hypothetical.txt")
    if file_path:
        with open(file_path, 'r') as file:
            content = file.read()
            text_widget.delete(1.0, tk.END)  # Clear previous content
            text_widget.insert(tk.END, content)

# Create the main window
root = tk.Tk()
root.title("AI Threat Intelligence Aggregator")

text_widget = tk.Text(root, wrap="word", width=40, height=10)
text_widget.pack(pady=10)

commands = {
    "Active Exploitation": open_file_active,
    "Demonstrated": open_file_demonstrated,
    "Hypothetical": open_file_hypothetical
}

def on_select():
    commands[opt.get()]()

opt = StringVar(value="Active Exploitation")

for lang in commands:
    Radiobutton(
        root,
        text=lang,
        value=lang,
        variable=opt,
        command=on_select
    ).pack()


lbl = Label(root, text="")
lbl.pack()

# Run the Tkinter event loop
root.mainloop()