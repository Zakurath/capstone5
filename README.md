# AI Threat Intelligence Aggregator

## Project Overview
The AI Threat Intelligence Aggregator is a Python-based cybersecurity tool designed to help analysts identify and prioritize emerging threats involving artificial intelligence.

The system collects threat intelligence from multiple sources, normalizes the information, filters out irrelevant threats, and uses Llama 3 to classify AI-related threats into three categories:

- Hypothetical: Threats shown in research or academic settings. 
- Demonstrated: Threats shown to be active in red team exercises or demonstration on a realistic AI-enabled system.
- Active Exploitation: Threats that are actively being used by a threat actor in real-world incidents targeting AI-enabled systems.

The goal is to provide security teams with a centralized view of emerging AI-related threats and reduce the amount of irrelevant information analysts need to review.

## Example Execution
<img width="1251" height="806" alt="image" src="https://github.com/user-attachments/assets/2dc1f83f-fc29-437b-86fe-bf7428524973" />

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
- Llama3/ Ollama
- Json
- Tkinter
- API

## Contributors
Group 5 – CSUSM Capstone
