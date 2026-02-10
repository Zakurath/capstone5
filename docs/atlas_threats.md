# MITRE ATLAS Threats (Selected)

This document summarizes selected AI-related threat techniques from the MITRE ATLAS framework that are included in our threat intelligence dataset.

---

## LLM Jailbreak (AML.T0054)

**Source:** MITRE ATLAS  
**Tactic:** Defense Evasion  
**Maturity:** Demonstrated  

Attackers use carefully crafted prompts to bypass LLM safety controls and guardrails, forcing the model to generate unrestricted or unsafe responses.

**Reference:**  
https://atlas.mitre.org/techniques/AML.T0054/

---

## LLM Prompt Injection (AML.T0051)

**Source:** MITRE ATLAS  
**Tactic:** Execution  
**Maturity:** Realized  

Adversaries craft malicious prompts that cause an LLM to ignore its original instructions and follow attacker-controlled behavior, enabling unintended or privileged actions.

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
