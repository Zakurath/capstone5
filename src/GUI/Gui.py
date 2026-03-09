import tkinter as tk
import webbrowser
from pathlib import Path
import json

def callback(url):
    webbrowser.open_new_tab(url)


root = tk.Tk()
root.title("AI Threat Aggregator")
root.geometry("1100x700")


# -------------------------
# DATA LOCATIONS
# -------------------------
BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_FILE = BASE_DIR / "docs/data/paper_summaries.json"
# -------------------------
# HEADER
# -------------------------
header = tk.Frame(root, bd=2, relief="solid")
header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

title = tk.Label(header, text="AI Threat Aggregator", font=("Arial", 32))
title.pack(pady=10)

# -------------------------
# SIDEBAR
# -------------------------
sidebar = tk.Frame(root, bd=2, relief="solid", width=200)
sidebar.grid(row=1, column=0, sticky="ns", padx=(10,5), pady=10)

buttons = [
    "All Threats",
    "Hypothetical",
    "Demonstrated",
    "Active Exploitation"
]

for b in buttons:
    btn = tk.Button(sidebar, text=b, width=18, height=2)
    btn.pack(pady=8, padx=10)

# spacer
tk.Frame(sidebar).pack(expand=True)

exit_btn = tk.Button(sidebar, text="Exit", width=18, height=2, command=root.destroy)
exit_btn.pack(pady=10)

# -------------------------
# MAIN CONTENT AREA
# -------------------------
main_frame = tk.Frame(root, bd=2, relief="solid")
main_frame.grid(row=1, column=1, sticky="nsew", padx=(5,10), pady=10)

root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(1, weight=1)

# -------------------------
# SCROLLABLE THREAT LIST
# -------------------------
canvas = tk.Canvas(main_frame)
scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)

list_frame = tk.Frame(canvas)

list_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0,0), window=list_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# -------------------------
# THREAT CARD FUNCTION
# -------------------------
def add_threat(title, classification, text, link_url):

    card = tk.Frame(list_frame, bd=2, relief="solid", padx=10, pady=10)
    card.pack(fill="x", padx=20, pady=10)

    title_label = tk.Label(card, text=title, anchor="w", wraplength= 850,
                           font=("Arial",12,"bold"),
                           bd=1, relief="solid", cursor="hand2")
    title_label.pack(fill="x", pady=(0,5))
    title_label.bind("<Button-1>", lambda e: callback(link_url))

    body = tk.Label(card, text=text, justify="left",
                    wraplength=850, anchor="nw",
                    bd=1, relief="solid")
    body.pack(fill="x")
    card.classification = classification

# -------------------------
# EXAMPLE DATA
# -------------------------

# -------------------------
# LOAD JSON
# -------------------------

with open(INPUT_FILE, 'r', encoding="utf-8") as file:
    data = json.load(file)

for i in data:
    add_threat(
        i["title"],
        i["classification"],
        i["super_summary"],
        i["url"]
    )

root.mainloop()