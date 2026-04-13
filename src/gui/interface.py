import random
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
INPUT_MITRE_OLD = BASE_DIR / "data/atlas_data.json"
INPUT_MITRE_TECHNIQUES = BASE_DIR / "data/atlas_techniques_normalized.json"
INPUT_MITRE_CASE_STUDIES = BASE_DIR / "data/atlas_case_studies_normalized.json"

#----------------------------------------
#        LOADING DATA
#----------------------------------------
REQUIRED_FIELDS = ["title", "classification", "abstract", "url"]



with open(INPUT_PAPER_FILE, 'r', encoding="utf-8") as file:
    PAPER_DATA = json.load(file)

DATA = PAPER_DATA.copy()

with open(INPUT_CISA_FILE, 'r', encoding="utf-8") as file:
    CISA_DATA = json.load(file)

with open(INPUT_MITRE_OLD, 'r', encoding="utf-8") as file:
    MITRE_DATA = json.load(file)

with open(INPUT_MITRE_TECHNIQUES, 'r', encoding="utf-8") as file:
    MITRE_TECHNIQUE_DATA = json.load(file)

with open(INPUT_MITRE_CASE_STUDIES, 'r', encoding="utf-8") as file:
   MITRE_CASE_STUDY_DATA = json.load(file)

DATA.extend(CISA_DATA)


DATA.extend(MITRE_TECHNIQUE_DATA)
DATA.extend(MITRE_CASE_STUDY_DATA)

MITRE_DATA = MITRE_TECHNIQUE_DATA.copy()
MITRE_DATA.extend(MITRE_CASE_STUDY_DATA)

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

    random.shuffle(DATA)

#----------------------------------------
#        GLOBAL VARIABLES
#----------------------------------------
current_page = 0
current_data_set = DATA
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
        add_threat(entry, list_frame)

def change_dataset(data, list_frame):
    global current_page
    global current_data_set

    current_data_set = data
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
def add_threat(data, list_frame):

    card = tk.Frame(list_frame, bd=2, relief="solid", padx=10, pady=10)
    card.pack(fill="x", padx=20, pady=10)

    # Modified title for MITRE ATLAS to include the ID number for clarity

    if data['source'] == "MITRE ATLAS":
        title_label = tk.Label(card, text=f"{data['id']}: {data['title']}", anchor="w", wraplength= 850,
                               font=("Arial",12,"bold"),
                               bd=1, relief="solid", cursor="hand2", justify="left")
        title_label.pack(fill="x", pady=(0,5))
        title_label.bind("<Button-1>", lambda e: callback(data['url']))
    else:
        title_label = tk.Label(card, text=data['title'], anchor="w", wraplength=850,
                               font=("Arial", 12, "bold"),
                               bd=1, relief="solid", cursor="hand2")
        title_label.pack(fill="x", pady=(0, 5))
        title_label.bind("<Button-1>", lambda e: callback(data['url']))

    # Classification and data source
    classification_label = tk.Label(card, text=f"{data['classification']}. {data['source']} \n\n{data['abstract']}", anchor="w", wraplength= 850, font=("Arial",10),
                           bd=1, relief="solid", justify="left")
    classification_label.pack(fill="x", pady=(0,5))


    # Extra row to tie sub-techniques back to the overaching one for better usability

    if data['source'] == "MITRE ATLAS":
        if data['type'] == "technique":
            if data['subtechniques'] is not None:
                subtechniques_label = tk.Label(card, text=f"Subtechnique of: {data['subtechniques']}", anchor="w",
                                                wraplength=850, font=("Arial", 10),
                                                bd=1, relief="solid", cursor="hand2" )
                subtechniques_label.pack(fill="x", pady=(0, 5))
                subtechniques_label.bind("<Button-1>", lambda e: callback(f"https://atlas.mitre.org/techniques/{data['subtechniques']}"))
        else:
            procedure_label = tk.Label(card, text=f"Techniques used: {data['techniques']}", anchor="w",
                                           wraplength=850, font=("Arial", 10),
                                           bd=1, relief="solid", justify="left")
            procedure_label.pack(fill="x", pady=(0, 5))


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

    # Sort by threat types

    all_threats_button =tk.Button(sidebar, text="All Threats", width=18, height=2, command=lambda:change_dataset(DATA, list_frame))
    all_threats_button.pack(pady=8, padx=10)

    hypothetical_button =tk.Button(sidebar, text="Hypothetical", width=18, height=2, command=lambda:change_dataset(THREATS["Hypothetical"], list_frame))
    hypothetical_button.pack(pady=8, padx=10)

    demonstrated_button =tk.Button(sidebar, text="Demonstrated", width=18, height=2, command=lambda:change_dataset(THREATS["Demonstrated"], list_frame))
    demonstrated_button.pack(pady=8, padx=10)

    active_exploitation_button =tk.Button(sidebar, text="Active Exploitation", width=18, height=2, command=lambda:change_dataset(THREATS["Active Exploitation"], list_frame))
    active_exploitation_button.pack(pady=8, padx=10)

    # Spacer
    tk.Label(sidebar, text="").pack(pady=30)

    # Sort by data source

    semantics_scholar_button = tk.Button(sidebar, text="Semantics Scholar", width=18, height=2, command=lambda: change_dataset(PAPER_DATA, list_frame))
    semantics_scholar_button.pack(pady=8, padx=10)

    cisa_button = tk.Button(sidebar, text="CISA KEV", width=18, height=2, command=lambda: change_dataset(CISA_DATA, list_frame))
    cisa_button.pack(pady=8, padx=10)

    mitre_button = tk.Button(sidebar, text="MITRE ATLAS", width=18, height=2, command=lambda: change_dataset(MITRE_DATA, list_frame))
    mitre_button.pack(pady=8, padx=10)

    # spacer
    tk.Frame(sidebar).pack(expand=True)

    # Navigation controls

    next_page_button = tk.Button(sidebar, text="Next Page", width=18, height=2, command=lambda:next_page(current_data_set, list_frame))
    next_page_button.pack(pady=8, padx=10)

    previous_page_button = tk.Button(sidebar, text="Previous Page", width=18,height=2, command=lambda:previous_page(current_data_set, list_frame))
    previous_page_button.pack(pady=8, padx=10)

    exit_btn = tk.Button(sidebar, text="Exit", width=18, height=2, command=root.destroy)
    exit_btn.pack(pady=10)


    render_page(DATA, list_frame)
    root.mainloop()

if __name__ == "__main__":
    main_interface()