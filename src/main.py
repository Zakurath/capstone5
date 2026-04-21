from gui import interface
from ingestion import sematics_scholar_abstract as papers
from ai_agent import ai_agent_abstract as abstract
import subprocess
import sys

def main():

    try:
        subprocess.run([sys.executable, "scripts/fetch_arxiv.py"])
        print("arXiv data updated")
    except Exception as e:
        print(f"Error updating arXiv data: {e}")

    update_abstracts = papers.fetch_abstracts({
        "query": "attacks against ai systems",
        "fields": "paperId,title,url",
        "year": "2023-",
    })

    if update_abstracts:
        print("Updating abstracts...")
        abstract.update_abstracts()
        print("Updated abstracts...")
    else:
        print("No updates found.")

    interface.main_interface()

if __name__ == "__main__":
    main()
