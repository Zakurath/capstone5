from src.gui import interface
from src.pipeline.run_pipeline import run_pipeline
import subprocess
import sys

def main():

    try:
        subprocess.run([sys.executable, "scripts/fetch_arxiv.py"])
        print("arXiv data updated")
    except Exception as e:
        print(f"Error updating arXiv data: {e}")

    # Check if user wants to run pipeline
    if "--update" in sys.argv:
        print("Running full pipeline update...\n")
        run_pipeline()
    else:
        print("Skipping pipeline update (faster startup)...\n")

    # Always launch dashboard
    interface.main_interface()

if __name__ == "__main__":
    main()
