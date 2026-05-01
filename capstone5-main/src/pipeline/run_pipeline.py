

from ingestion import the_hacker_news_ingest 
from ingestion import cisa_kev_ingest
from ingestion import mitre_atlas_ingest
from ingestion import sematics_scholar_abstract
from ai_agent import ai_agent_abstract
from processing import combine_sources


def run_pipeline():
    print("\n=== Starting AI Threat Intelligence Pipeline ===\n")

    # Step 1: Update CISA KEV source
    try:
        print("[1/6] Updating CISA KEV data...")
        cisa_kev_ingest.main()
        print("CISA KEV update complete.\n")
    except Exception as e:
        print(f"Error updating CISA KEV data: {e}\n")

    # Step 2: Update MITRE ATLAS source
    try:
        print("[2/6] Updating MITRE ATLAS data...")
        mitre_atlas_ingest.main()
        print("MITRE ATLAS update complete.\n")
    except Exception as e:
        print(f"Error updating MITRE ATLAS data: {e}\n")

    # Step 3: Fetch new Semantic Scholar papers
    try:
        print("[3/6] Fetching new Semantic Scholar paper abstracts...")
        updated = sematics_scholar_abstract.fetch_abstracts({
            "query": "attacks against ai systems",
            "fields": "paperId,title,url",
            "year": "2023-",
        })

        if updated:
            print("New paper abstracts found.\n")
        else:
            print("No new paper abstracts found.\n")
    except Exception as e:
        print(f"Error fetching paper abstracts: {e}\n")
        updated = False

    # Step 4: Classify paper abstracts with LLM
    try:
        print("[4/6] Classifying research paper abstracts...")
        ai_agent_abstract.update_abstracts()
        print("Paper abstract classification complete.\n")
    except Exception as e:
        print(f"Error classifying paper abstracts: {e}\n")

    # Step 5: Process AI-related CISA KEV entries with LLM
    try:
        print("[5/6] Processing AI-related CISA KEV entries...")
        ai_agent_abstract.update_cisa_kev()
        print("CISA KEV AI filtering complete.\n")
    except Exception as e:
        print(f"Error processing CISA KEV AI filtering: {e}\n")



        # Step 6: Fetch The Hacker News AI/cybersecurity stories
    try:
        print("[6/7] Fetching The Hacker News AI-related cybersecurity stories...")
        the_hacker_news_ingest.main()
        print("The Hacker News update complete.\n")
    except Exception as e:
        print(f"Error updating The Hacker News data: {e}\n")

    # Step 7: Combine sources
    try:
        print("[7/7] Combining all available sources...")
        combine_sources.main()
        print("Source combination complete.\n")
    except Exception as e:
        print(f"Error combining sources: {e}\n")


    