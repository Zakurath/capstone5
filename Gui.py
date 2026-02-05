import tkinter as tk

# 1. Create the main window
root = tk.Tk()
root.title("Simple GUI Example")
root.geometry("300x150")

# 2. Add a label widget
label = tk.Label(root, text="Welcome to the Python GUI!", font=("Helvetica", 12))
label.pack(pady=20) # Add padding for better layout

# 3. Add a button widget that changes the label text when clicked
def on_button_click():
    label.config(text="Button Clicked!")

button = tk.Button(root, text="Click Me", command=on_button_click)
button.pack(pady=10)

# 4. Start the event loop
root.mainloop()