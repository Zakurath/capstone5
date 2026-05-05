import random
import tkinter as tk
import webbrowser
from pathlib import Path
import json

# ----------------------------------------
#       DATA LOCATIONS
# ----------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_PAPER_FILE = BASE_DIR / "data/research_papers_abstract/paper_summaries_abstract2.json"
INPUT_CISA_FILE = BASE_DIR / "data/cisa_kev_processed.json"
INPUT_MITRE_OLD = BASE_DIR / "data/atlas_data.json"
INPUT_MITRE_TECHNIQUES = BASE_DIR / "data/atlas_techniques_normalized.json"
INPUT_MITRE_CASE_STUDIES = BASE_DIR / "data/atlas_case_studies_normalized.json"
INPUT_HACKER_NEWS = BASE_DIR / "data/the_hacker_news_data.json"
INPUT_ARXIV_FILE = BASE_DIR / "data/arxiv_threat_data.json"

# Optional combined file for future use
INPUT_ALL_THREATS_FILE = BASE_DIR / "data/all_threats.json"

# ----------------------------------------
#        LOADING DATA
# ----------------------------------------
REQUIRED_FIELDS = ["title", "classification", "abstract", "url"]


def load_json_file(file_path):
    if not file_path.exists():
        print(f"Warning: File not found -> {file_path}")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
            print(f"Warning: Expected a list in {file_path}, but got {type(data).__name__}")
            return []
    except Exception as e:
        print(f"Warning: Could not load {file_path}: {e}")
        return []


# ----------------------------------------
#        LOAD COMBINED DATA (NEW)
# ----------------------------------------
DATA = load_json_file(INPUT_ALL_THREATS_FILE)

# Ensure source-specific variables exist even when using combined file
PAPER_DATA = []
CISA_DATA = []
MITRE_TECHNIQUE_DATA = []
MITRE_CASE_STUDY_DATA = []
THE_HACKER_NEWS_DATA = []
ARXIV_DATA = load_json_file(INPUT_ARXIV_FILE)

# Fallback if file is empty or missing
if not DATA:
    print("Warning: all_threats.json not found or empty, falling back to individual sources.")

    PAPER_DATA = load_json_file(INPUT_PAPER_FILE)
    CISA_DATA = load_json_file(INPUT_CISA_FILE)
    MITRE_TECHNIQUE_DATA = load_json_file(INPUT_MITRE_TECHNIQUES)
    MITRE_CASE_STUDY_DATA = load_json_file(INPUT_MITRE_CASE_STUDIES)
    THE_HACKER_NEWS_DATA = load_json_file(INPUT_HACKER_NEWS)

    DATA = []
    DATA.extend(PAPER_DATA)
    DATA.extend(CISA_DATA)
    DATA.extend(MITRE_TECHNIQUE_DATA)
    DATA.extend(MITRE_CASE_STUDY_DATA)
    DATA.extend(ARXIV_DATA)

MITRE_DATA = []
MITRE_DATA.extend(MITRE_TECHNIQUE_DATA)
MITRE_DATA.extend(MITRE_CASE_STUDY_DATA)

THREATS = {
    "Hypothetical": [],
    "Demonstrated": [],
    "Active Exploitation": []
}

VALID_DATA = []

for entry in DATA:
    if not isinstance(entry, dict):
        continue

    if not all(field in entry for field in REQUIRED_FIELDS):
        continue

    if entry["classification"] not in THREATS:
        continue

    VALID_DATA.append(entry)
    THREATS[entry["classification"]].append(entry)

DATA = VALID_DATA
random.shuffle(DATA)

# ----------------------------------------
#        GLOBAL VARIABLES
# ----------------------------------------
current_page = 0
current_data_set = DATA
PAGE_SIZE = 40


# ----------------------------------------
#        FUNCTIONS
# ----------------------------------------
def callback(url):
    webbrowser.open_new_tab(url)


def render_page(data, list_frame):
    for widget in list_frame.winfo_children():
        widget.destroy()

    start = current_page * PAGE_SIZE
    end = start + PAGE_SIZE

    page_data = data[start:end]

    if not page_data:
        empty_label = tk.Label(
            list_frame,
            text="No threats found for this selection.",
            font=("Arial", 14),
            pady=20
        )
        empty_label.pack()
        return

    for entry in page_data:
        add_threat(entry, list_frame)


def change_dataset(data, list_frame):
    global current_page
    global current_data_set

    current_data_set = data
    current_page = 0
    render_page(current_data_set, list_frame)


def next_page(data, list_frame):
    global current_page

    max_page = max(0, (len(data) - 1) // PAGE_SIZE)
    if current_page < max_page:
        current_page += 1

    render_page(data, list_frame)


def previous_page(data, list_frame):
    global current_page

    if current_page > 0:
        current_page -= 1

    render_page(data, list_frame)


def normalize_text(value):
    if value is None:
        return ""
    return str(value).strip().lower()


def get_source_name(entry):
    return entry.get("source", "Unknown")


def apply_filters(search_text, selected_source, selected_classification):
    search_text = normalize_text(search_text)

    ranked_results = []

    for entry in DATA:
        title = normalize_text(entry.get("title", ""))
        abstract = normalize_text(entry.get("abstract", ""))
        source = entry.get("source", "Unknown")
        classification = entry.get("classification", "Unknown")
        source_normalized = normalize_text(source)

        # Source filter
        if selected_source != "All Sources":
            if normalize_text(source) != normalize_text(selected_source):
                continue

        # Classification filter
        if selected_classification != "All Classifications":
            if classification != selected_classification:
                continue

        # Search ranking
        score = 0

        if search_text:
            if search_text == source_normalized:
                score += 300
            if search_text in title:
                score += 200
            if search_text in abstract:
                score += 100
            if search_text in source_normalized:
                score += 250

            if score == 0:
                continue

        ranked_results.append((score, entry))

    ranked_results.sort(key=lambda item: item[0], reverse=True)

    return [entry for score, entry in ranked_results]


# ----------------------------------------
#        THREAT CARD FUNCTION
# ----------------------------------------

def add_threat(data, list_frame):
    if data.get("type") == "fake":
        card = tk.Frame(list_frame, bd=3, relief="solid", padx=10, pady=10, bg="#ffe6e6")
    else:
        card = tk.Frame(list_frame, bd=2, relief="solid", padx=10, pady=10)

    card.pack(fill="x", padx=20, pady=10)

    source = data.get("source", "Unknown")
    title = data.get("title", "Untitled")
    url = data.get("url", "")
    classification = data.get("classification", "Unknown")
    abstract = data.get("abstract", "No abstract available.")
    entry_id = data.get("id", "")
    entry_type = data.get("type", "")
    subtechniques = data.get("subtechniques")
    techniques = data.get("techniques", "")

    if source == "MITRE ATLAS" and entry_id:
        title_text = f"{entry_id}: {title}"
    else:
        title_text = title

    title_label = tk.Label(
        card,
        text=title_text,
        anchor="w",
        wraplength=850,
        font=("Arial", 12, "bold"),
        bd=1,
        relief="solid",
        cursor="hand2" if url else "arrow",
        justify="left",
        bg=card.cget("bg")
    )
    title_label.pack(fill="x", pady=(0, 5))

    if url:
        title_label.bind("<Button-1>", lambda e: callback(url))

    classification_label = tk.Label(
        card,
        text=f"{classification}. {source}\n\n{abstract}",
        anchor="w",
        wraplength=850,
        font=("Arial", 10),
        bd=1,
        relief="solid",
        justify="left",
        bg=card.cget("bg")
    )
    classification_label.pack(fill="x", pady=(0, 5))

    if source == "MITRE ATLAS":
        # If a technique has a subtechnique display that
        if entry_type == "technique":
            title_label.bind("<Button-1>",lambda e: callback(f"https://atlas.mitre.org/techniques/{entry_id}"))
            if subtechniques:
                subtechniques_label = tk.Label(
                    card,
                    text=f"Subtechnique of: {subtechniques}",
                    anchor="w",
                    wraplength=850,
                    font=("Arial", 10),
                    bd=1,
                    relief="solid",
                    cursor="hand2",
                    bg=card.cget("bg")
                )
                subtechniques_label.pack(fill="x", pady=(0, 5))
                subtechniques_label.bind(
                    "<Button-1>",
                    lambda e: callback(f"https://atlas.mitre.org/techniques/{subtechniques}")
                )
        else:
            # displays a case study's techniques used
            title_label.bind("<Button-1>", lambda e: callback(f"https://atlas.mitre.org/studies/{entry_id}"))
            if techniques:
                techniques_box = tk.Frame(
                    card,
                    bd=1,
                    relief="solid",
                    padx=8,
                    pady=6,
                    bg=card.cget("bg")
                )
                techniques_box.pack(fill="x", pady=(5, 0))

                # Header inside box
                tk.Label(
                    techniques_box,
                    text="Techniques Used:",
                    anchor="w",
                    font=("Arial", 10, "bold"),
                    bg=card.cget("bg")
                ).pack(fill="x")

                for t in techniques:
                        techniques_id = t.get("technique", "UNKNOWN")
                        descriptions = t.get("description", "Unknown")

                        label = tk.Label(
                            techniques_box,
                            text=f"{techniques_id} - {descriptions}",
                            anchor="w",
                            wraplength=850,
                            justify="left",
                            font=("Arial", 10),
                            fg="black",
                            cursor="hand2",
                            bg=card.cget("bg")
                        )
                        label.pack(fill="x", padx=10)

                        url = f"https://atlas.mitre.org/techniques/{techniques_id}"
                        label.bind("<Button-1>", lambda e, u=url: callback(u))

        # Mitigations
        if entry_type == "technique":
            if data.get("type") == "technique":
                mitigations = data.get("mitigations") or []

                # 🔲 ONE BOX CONTAINER
                mitigation_box = tk.Frame(
                    card,
                    bd=1,
                    relief="solid",
                    padx=8,
                    pady=6,
                    bg=card.cget("bg")
                )
                mitigation_box.pack(fill="x", pady=(5, 0))

                # Header inside box
                tk.Label(
                    mitigation_box,
                    text="Mitigations:",
                    anchor="w",
                    font=("Arial", 10, "bold"),
                    bg=card.cget("bg")
                ).pack(fill="x")

                if mitigations:
                    for m in mitigations:
                        mitigation_id = m.get("mitigation_id", "UNKNOWN")
                        mitigation_name = m.get("mitigation_name", "Unknown")

                        label = tk.Label(
                            mitigation_box,
                            text=f"{mitigation_id} - {mitigation_name}",
                            anchor="w",
                            wraplength=850,
                            font=("Arial", 10),
                            fg="black",
                            cursor="hand2",
                            bg=card.cget("bg")
                        )
                        label.pack(fill="x", padx=10)

                        url = f"https://atlas.mitre.org/mitigations/{mitigation_id}"
                        label.bind("<Button-1>", lambda e, u=url: callback(u))
                else:
                    tk.Label(
                        mitigation_box,
                        text="No known mitigations",
                        anchor="w",
                        font=("Arial", 10, "italic"),
                        fg="black",
                        bg=card.cget("bg")
                    ).pack(fill="x", padx=10)

def main_interface():
    global current_data_set

    # ----------------------------------------
    #        GUI INITIALIZATION
    # ----------------------------------------
    root = tk.Tk()
    root.title("AI Threat Aggregator")
    root.geometry("1250x980")

    # ----------------------------------------
    #        HEADER
    # ----------------------------------------
    header = tk.Frame(root, bd=2, relief="solid")
    header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

    title = tk.Label(header, text="AI Threat Aggregator", font=("Arial", 32))
    title.pack(pady=10)

    # ----------------------------------------
    #        MAIN CONTENT AREA
    # ----------------------------------------
    main_frame = tk.Frame(root, bd=2, relief="solid")
    main_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)

    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(1, weight=1)

    # ----------------------------------------
    #        SCROLLABLE THREAT LIST
    # ----------------------------------------
    canvas = tk.Canvas(main_frame)
    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)

    list_frame = tk.Frame(canvas)

    list_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=list_frame, anchor="nw", width=950)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ----------------------------------------
    #        SIDEBAR
    # ----------------------------------------
    sidebar = tk.Frame(root, bd=2, relief="solid", width=220)
    sidebar.grid(row=1, column=0, sticky="ns", padx=(10, 5), pady=10)
    sidebar.grid_propagate(False)

    # ----------------------------------------
    #        FILTER STATE
    # ----------------------------------------
    source_options = ["All Sources", "Semantic Scholar", "CISA KEV", "MITRE ATLAS", "The Hacker News", "arXiv", "Fake Data"]
    classification_options = [
        "All Classifications",
        "Hypothetical",
        "Demonstrated",
        "Active Exploitation"
    ]

    search_var = tk.StringVar()
    source_var = tk.StringVar(value="All Sources")
    classification_var = tk.StringVar(value="All Classifications")

    def refresh_filters():
        global current_data_set
        filtered = apply_filters(
            search_var.get(),
            source_var.get(),
            classification_var.get()
        )
        current_data_set = filtered
        change_dataset(filtered, list_frame)

    def clear_filters():
        search_var.set("")
        source_var.set("All Sources")
        classification_var.set("All Classifications")
        refresh_filters()

    # ----------------------------------------
    #        SEARCH BAR
    # ----------------------------------------
    tk.Label(sidebar, text="Search", font=("Arial", 11, "bold")).pack(pady=(10, 4), padx=10, anchor="w")

    search_entry = tk.Entry(sidebar, textvariable=search_var, width=24)
    search_entry.pack(pady=(0, 8), padx=10, fill="x")
    search_entry.bind("<KeyRelease>", lambda event: refresh_filters())

    # ----------------------------------------
    #        SOURCE DROPDOWN
    # ----------------------------------------
    tk.Label(sidebar, text="Source", font=("Arial", 11, "bold")).pack(pady=(8, 4), padx=10, anchor="w")

    source_menu = tk.OptionMenu(sidebar, source_var, *source_options, command=lambda _: refresh_filters())
    source_menu.config(width=18)
    source_menu.pack(pady=(0, 8), padx=10)

    # ----------------------------------------
    #        CLASSIFICATION DROPDOWN
    # ----------------------------------------
    tk.Label(sidebar, text="Classification", font=("Arial", 11, "bold")).pack(pady=(8, 4), padx=10, anchor="w")

    classification_menu = tk.OptionMenu(sidebar, classification_var, *classification_options,
                                        command=lambda _: refresh_filters())
    classification_menu.config(width=18)
    classification_menu.pack(pady=(0, 8), padx=10)

    reset_button = tk.Button(sidebar, text="Reset Filters", width=18, height=2, command=clear_filters)
    reset_button.pack(pady=10, padx=10)

    # spacer

    # ----------------------------------------
    #        NAVIGATION CONTROLS
    # ----------------------------------------
    next_page_button = tk.Button(sidebar, text="Next Page", width=18, height=2,
                                 command=lambda: next_page(current_data_set, list_frame))
    next_page_button.pack(pady=8, padx=10)

    previous_page_button = tk.Button(sidebar, text="Previous Page", width=18, height=2,
                                     command=lambda: previous_page(current_data_set, list_frame))
    previous_page_button.pack(pady=8, padx=10)

    exit_btn = tk.Button(sidebar, text="Exit", width=18, height=2, command=root.destroy)
    exit_btn.pack(pady=10)

    current_data_set = DATA
    render_page(DATA, list_frame)
    root.mainloop()


if __name__ == "__main__":
    main_interface()
