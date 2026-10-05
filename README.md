# AI Threat Intelligence Aggregator

## Project Overview
The AI Threat Intelligence Aggregator is a Python-based cybersecurity tool designed to help analysts identify and prioritize emerging threats involving artificial intelligence.

The system collects threat intelligence from multiple sources, normalizes the information, filters out irrelevant threats, and uses Llama 3 to classify AI-related threats into three categories:

- Hypothetical: Threats shown in research or academic settings. 
- Demonstrated: Threats shown to be active in red team exercises or demonstration on a realistic AI-enabled system.
- Active Exploitation: Threats that are actively being used by a threat actor in real-world incidents targeting AI-enabled systems.

The goal is to provide security teams with a centralized view of emerging AI-related threats and reduce the amount of irrelevant information analysts need to review.

## Features

- **Multi-Source Threat Intelligence** — Aggregates AI-related threat intelligence from CISA KEV, MITRE ATLAS, Semantic Scholar, arXiv, and The Hacker News.
- **Threat Classification** — Categorizes threats as Hypothetical, Demonstrated, or Active Exploitation.
- **AI Threat Filtering** — Centralizes AI-related threats to help security teams prioritize emerging risks.
- **Threat Data Processing** — Ingests and processes raw and structured threat intelligence from multiple sources, with the option to delay updates when needed.
- **Graphical User Interface** — Provides a GUI for reviewing collected threat intelligence.
- **Search and Filtering** — Allows users to search, navigate, and filter collected threat information.
- **Source Linking** — Provides direct access to the original source associated with each threat.
- **LLM Integration** — Uses a locally hosted Llama 3 model as part of the threat analysis pipeline.
- **Risk Demonstration** — Uses simulated untrusted data sources to demonstrate how the system could be susceptible to data poisoning if unverified sources are introduced.
  
## Example Execution
<img width="800" height="572" alt="Capstoneupdated-ezgif com-video-to-gif-converter" src="https://github.com/user-attachments/assets/08b5c8c1-f321-45d2-a8bc-97be4969c84a" />

This demonstrates the project's threat classification filters, search functionality, scrolling interface, and clickable threat entries. Each entry links to the original source for further investigation.


## Data Sources
- CISA Known Exploited Vulnerabilities (KEV)
- MITRE ATLAS
- Semantic Scholar
- ArXiv
- The Hacker News

## Project Structure
/docs        -> documentation

/data        -> raw and processed threat data

/src         -> ingestion, processing, API logic, gui

<img width="835" height="765" alt="image" src="https://github.com/user-attachments/assets/fcac1aa8-7f87-479d-93c0-503477d44348" />


## Requirements
- Python runtime environment
- Local installation of Llama3  

## Technologies Used 
- Python
- Llama3
- Ollama
- JSON
- Tkinter
- API Integration

## Contributors
Group 5 – CSUSM Capstone
