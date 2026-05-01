# MITRE ATLAS Threats (Selected)

This document summarizes selected AI-related threat techniques from the MITRE ATLAS framework that are included in our threat intelligence dataset.

## LLM Jailbreak (AML.T0054)
**Source:** MITRE ATLAS  
**Tactic:** Defense Evasion  
**Maturity:** Demonstrated  

Adversaries use carefully crafted prompts to bypass LLM safety controls and guardrails, forcing the model to generate unrestricted or unsafe responses.

**Reference:**  
https://atlas.mitre.org/techniques/AML.T0054/

---

## LLM Prompt Injection (AML.T0051)
**Source:** MITRE ATLAS  
**Tactic:** Execution  
**Maturity:** Realized  

Adversaries craft malicious prompts that cause an LLM to ignore original instructions and follow attacker-controlled behavior, enabling unintended or privileged actions.

**Reference:**  
https://atlas.mitre.org/techniques/AML.T0051/

---

## RAG Poisoning (AML.T0070)
**Source:** MITRE ATLAS  
**Tactic:** Persistence  
**Maturity:** Demonstrated  

Adversaries inject malicious or misleading content into documents indexed by a RAG system so poisoned content appears in future retrieval results.

**Reference:**  
https://atlas.mitre.org/techniques/AML.T0070/

---

## False RAG Entry Injection (AML.T0071)
**Source:** MITRE ATLAS  
**Tactic:** Defense Evasion  
**Maturity:** Demonstrated  

Adversaries introduce false documents into a RAG database so that when retrieved, the LLM treats malicious content as a legitimate RAG result.

**Reference:**  
https://atlas.mitre.org/techniques/AML.T0071/

---

## Training Data Poisoning (AML.T0034)
**Source:** MITRE ATLAS  
**Tactic:** Impact  
**Maturity:** Demonstrated  

Adversaries manipulate training data to influence model behavior and cause incorrect or malicious outputs.

**Reference:**  
https://atlas.mitre.org/techniques/AML.T0034/

---

## AI Model Extraction (AML.T0042)
**Source:** MITRE ATLAS  
**Tactic:** Collection  
**Maturity:** Demonstrated  

Adversaries attempt to extract or replicate the functionality of a deployed AI model by repeatedly querying it and analyzing the outputs.

**Reference:**  
https://atlas.mitre.org/techniques/AML.T0042/

---

## Model Evasion (AML.T0021)
**Source:** MITRE ATLAS  
**Tactic:** Defense Evasion  
**Maturity:** Demonstrated  

Adversaries craft inputs designed to evade AI-based detection and bypass classification or security controls.

**Reference:**  
https://atlas.mitre.org/techniques/AML.T0021/

---

## AI Artifact Collection (AML.T0060)
**Source:** MITRE ATLAS  
**Tactic:** Collection  
**Maturity:** Demonstrated  

Adversaries collect artifacts related to AI systems such as models, training data, prompts, or configuration files.

**Reference:**  
https://atlas.mitre.org/techniques/AML.T0060/

---

## Model Backdoor (AML.T0038)
**Source:** MITRE ATLAS  
**Tactic:** Persistence  
**Maturity:** Hypothetical  

Adversaries embed hidden triggers or backdoors in AI models so that specific inputs activate malicious behavior.

**Reference:**  
https://atlas.mitre.org/techniques/AML.T0038/

---

## Adversarial Examples (AML.T0019)
**Source:** MITRE ATLAS  
**Tactic:** Execution  
**Maturity:** Demonstrated  

Adversaries craft carefully modified inputs that cause AI models to produce incorrect predictions or classifications.

**Reference:**  
https://atlas.mitre.org/techniques/AML.T0019/

---

## Model Inversion (AML.T0050)
**Source:** MITRE ATLAS  
**Tactic:** Collection  
**Maturity:** Demonstrated  

Adversaries attempt to reconstruct sensitive training information by analyzing a model’s outputs.

**Reference:**  
https://atlas.mitre.org/techniques/AML.T0050/

---

## AI Supply Chain Compromise (AML.T0064)
**Source:** MITRE ATLAS  
**Tactic:** Initial Access  
**Maturity:** Demonstrated  

Adversaries compromise AI supply chain components such as models, datasets, or libraries to introduce malicious behavior.

**Reference:**  
https://atlas.mitre.org/techniques/AML.T0064/
