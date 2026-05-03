
# 🛡️ Safety-First AI Support Triage Agent

A deterministic support triage system designed to safely process support tickets and decide whether to **reply automatically** or **escalate for human review**.

Built as part of the *HackerRank Orchestrate (May 2026)* challenge.

---

## 🚀 Overview

This project focuses on building a **safe, explainable, and reliable AI system** that operates under strict constraints:

- Uses only the provided local support corpus  
- Avoids hallucinated or unsupported responses  
- Prioritises escalation for sensitive or uncertain cases  

The goal is not just to answer tickets — but to ensure **correct and safe decision-making**.

---

## 🧠 System Design

The agent follows a simple, auditable pipeline:

```

Ticket Input → Classification → Retrieval → Escalation Decision → Response → Output

```

### Flow:
1. Load support tickets from CSV  
2. Classify product area and request type  
3. Retrieve relevant documents from local corpus  
4. Apply escalation rules for sensitive cases  
5. Generate grounded response and justification  
6. Write structured output to CSV  

---

## ⚙️ Key Principles

- **Safety-first**  
  Escalate instead of guessing when confidence is low  

- **Deterministic**  
  Rule-based logic ensures predictable and consistent behaviour  

- **Grounded**  
  Responses are strictly derived from the provided documentation  

- **Explainable**  
  Every decision includes a clear justification  

---

## 📊 Output

Results are written to:

```

support_tickets/output.csv

````

Each ticket produces:

| Field          | Description |
|----------------|------------|
| response       | Generated reply or escalation message |
| product_area   | Classified topic area |
| request_type   | Type of request |
| status         | `Replied` or `Escalated` |
| justification  | Reason for the decision |

---

## 🛠️ Tech Stack

- Python 3  
- CSV-based data processing  
- Rule-based classification  
- Local corpus retrieval  

---

## ⚖️ Trade-offs

### Strengths
- Safe and predictable behaviour  
- No hallucination risk  
- Easy to audit and debug  
- No dependency on external APIs  

### Limitations
- Keyword-based (limited semantic understanding)  
- Less flexible than embedding/LLM-based systems  

---

## ▶️ How to Run

```bash
python3 main.py
````

---

## 💡 Key Insight

> Building AI systems is not just about intelligence —
> it's about designing systems that are safe, reliable, and know when to escalate.

```


