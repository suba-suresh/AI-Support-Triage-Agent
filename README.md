Safety-First AI Support Triage Agent
A deterministic support triage system built for the HackerRank Orchestrate (May 2026) challenge.

Overview
This project processes support tickets and decides whether to reply automatically or escalate for human review — using only the provided local support corpus, with no hallucinated or unsupported answers.

Approach
The agent follows a straightforward, auditable pipeline:

Read support tickets from CSV
Classify product area and request type using rule-based logic
Retrieve relevant documents from the local corpus
Apply escalation logic for sensitive or uncertain cases
Generate a grounded response and justification
Write structured output to CSV


Key Design Principles

Safety-first — escalate instead of guessing when uncertain
Deterministic — rule-based decisions for consistency and auditability
Grounded — responses drawn only from provided documentation
Explainable — every output includes a human-readable justification


Output
Results are written to support_tickets/output.csv. Each row includes:
FieldDescriptionresponseGenerated reply or escalation messageproduct_areaClassified topic arearequest_typeType of request detectedstatusReplied or EscalatedjustificationReasoning behind the decision

Tech Stack

Python 3
CSV processing
Rule-based classification
Local file-based corpus retrieval


Trade-offs
Strengths

Safe, predictable, and easy to debug
No risk of hallucinated support policies
No external API dependencies

Limitations

Keyword matching may miss semantic variations in phrasing
Less flexible than embedding-based or LLM-driven retrieval
Future versions could add confidence scoring and semantic search


How to Run
```bash
python3 code/main.py```
