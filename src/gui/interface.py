import tkinter as tk
import webbrowser
from pathlib import Path
import json

#----------------------------------------
#       DATA LOCATIONS
#----------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_PAPER_FILE = BASE_DIR / "data/research_papers_abstract/paper_summaries_abstract2.json"
INPUT_CISA_FILE =  BASE_DIR / "data/cisa_kev_processed.json"
INPUT_MITRE = BASE_DIR / "data/atlas_data.json"

#----------------------------------------
#        LOADING DATA
#----------------------------------------
REQUIRED_FIELDS = ["title", "classification", "abstract", "url"]



with open(INPUT_PAPER_FILE, 'r', encoding="utf-8") as file:
    PAPER_DATA = json.load(file)

DATA = PAPER_DATA.copy()

with open(INPUT_CISA_FILE, 'r', encoding="utf-8") as file:
    CISA_DATA = json.load(file)

with open(INPUT_MITRE, 'r', encoding="utf-8") as file:
    MITRE_DATA = json.load(file)

    DATA.extend(CISA_DATA)
    DATA.extend(MITRE_DATA)

THREATS = {
    "Hypothetical": [],
    "Demonstrated": [],
    "Active Exploitation": []
}

for entry in DATA:
    if not all(field in entry for field in REQUIRED_FIELDS):
        continue

        # skip invalid classification
    if entry["classification"] not in THREATS:
        continue

    THREATS[entry["classification"]].append(entry)

#----------------------------------------
#        GLOBAL VARIABLES
#----------------------------------------
current_page = 0
PAGE_SIZE = 40

#----------------------------------------
#        FUNCTIONS
#----------------------------------------

def callback(url):
    webbrowser.open_new_tab(url)

def render_page(data, list_frame):
    for widget in list_frame.winfo_children():
        widget.destroy()

    start = current_page * PAGE_SIZE
    end = start + PAGE_SIZE

    for entry in data[start:end]:
        add_threat(
            entry["title"],
            entry["classification"],
            entry["abstract"],
            entry["url"], list_frame
        )

def change_dataset(data, list_frame):
    global current_page
    current_page = 0
    render_page(data, list_frame)

def next_page(data, list_frame):
    global current_page
    current_page += 1
    render_page(data, list_frame)

def previous_page(data, list_frame):
    global current_page
    current_page -= 1
    render_page(data, list_frame)

#----------------------------------------
#        THREAT CARD FUNCTION
#----------------------------------------
def add_threat(title, classification, text, link_url, list_frame):

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
    body.pack(fill="x", expand=True)
    card.classification = classification

def main_interface():
    #----------------------------------------
    #        GUI INITIALIZATION
    #----------------------------------------
    root = tk.Tk()
    root.title("AI Threat Aggregator")
    root.geometry("1100x900")

    #----------------------------------------
    #        HEADER
    #----------------------------------------
    header = tk.Frame(root, bd=2, relief="solid")
    header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

    title = tk.Label(header, text="AI Threat Aggregator", font=("Arial", 32))
    title.pack(pady=10)

    #----------------------------------------
    #        MAIN CONTENT AREA
    #----------------------------------------
    main_frame = tk.Frame(root, bd=2, relief="solid")
    main_frame.grid(row=1, column=1, sticky="nsew", padx=(5,10), pady=10)

    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(1, weight=1)

    #----------------------------------------
    #        SCROLLABLE THREAT LIST
    #----------------------------------------
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

    #----------------------------------------
    #        SIDEBAR
    #----------------------------------------
    sidebar = tk.Frame(root, bd=2, relief="solid", width=200)
    sidebar.grid(row=1, column=0, sticky="ns", padx=(10,5), pady=10)

    all_threats_button =tk.Button(sidebar, text="All Threats", width=18, height=2, command=lambda:change_dataset(DATA, list_frame))
    all_threats_button.pack(pady=8, padx=10)

    hypothetical_button =tk.Button(sidebar, text="Hypothetical", width=18, height=2, command=lambda:change_dataset(THREATS["Hypothetical"], list_frame))
    hypothetical_button.pack(pady=8, padx=10)

    demonstrated_button =tk.Button(sidebar, text="Demonstrated", width=18, height=2, command=lambda:change_dataset(THREATS["Demonstrated"], list_frame))
    demonstrated_button.pack(pady=8, padx=10)

    active_exploitation_button =tk.Button(sidebar, text="Active Exploitation", width=18, height=2, command=lambda:change_dataset(THREATS["Active Exploitation"], list_frame))
    active_exploitation_button.pack(pady=8, padx=10)

    tk.Label(sidebar, text="").pack(pady=30)

    semantics_scholar_button = tk.Button(sidebar, text="Semantics Scholar", width=18, height=2, command=lambda: change_dataset(PAPER_DATA, list_frame))
    semantics_scholar_button.pack(pady=8, padx=10)

    cisa_button = tk.Button(sidebar, text="CISA KEV", width=18, height=2, command=lambda: change_dataset(CISA_DATA, list_frame))
    cisa_button.pack(pady=8, padx=10)

    mitre_button = tk.Button(sidebar, text="MITRE ATLAS", width=18, height=2, command=lambda: change_dataset(MITRE_DATA, list_frame))
    mitre_button.pack(pady=8, padx=10)

    # spacer
    tk.Frame(sidebar).pack(expand=True)

    next_page_button = tk.Button(sidebar, text="Next Page", width=18, height=2, command=lambda:next_page(DATA, list_frame))
    next_page_button.pack(pady=8, padx=10)

    previous_page_button = tk.Button(sidebar, text="Previous Page", width=18,height=2, command=lambda:previous_page(DATA, list_frame))
    previous_page_button.pack(pady=8, padx=10)

    exit_btn = tk.Button(sidebar, text="Exit", width=18, height=2, command=root.destroy)
    exit_btn.pack(pady=10)


    render_page(DATA, list_frame)
    root.mainloop()

if __name__ == "__main__":
    main_interface()