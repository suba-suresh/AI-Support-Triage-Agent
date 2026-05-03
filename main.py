import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TICKETS_FILE = BASE_DIR / "support_tickets" / "support_tickets.csv"
OUTPUT_FILE = BASE_DIR / "support_tickets" / "output.csv"
LOG_FILE = BASE_DIR / "log.txt"
DATA_DIR = BASE_DIR / "data"


def load_tickets():
    tickets = []

    with open(TICKETS_FILE, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            tickets.append({
                "issue": row.get("Issue", "").strip(),
                "subject": row.get("Subject", "").strip(),
                "company": row.get("Company", "").strip()
            })

    return tickets


def load_corpus():
    corpus = []

    if not DATA_DIR.exists():
        return corpus

    for company_folder in DATA_DIR.iterdir():
        if not company_folder.is_dir():
            continue

        company = company_folder.name.lower()

        for file_path in company_folder.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in [".md", ".txt"]:
                content = file_path.read_text(encoding="utf-8", errors="ignore")

                corpus.append({
                    "company": company,
                    "path": str(file_path.relative_to(DATA_DIR)),
                    "content": content
                })

    return corpus


def classify_request(issue, subject, company):
    text = f"{issue} {subject} {company}".lower()
    company_value = str(company).strip().lower()

    if company_value in ["", "none"]:
        return "invalid", "invalid"

    if any(word in text for word in [
        "security vulnerability", "vulnerability", "bug bounty", "infosec"
    ]):
        return "security", "security"

    if any(word in text for word in [
        "identity", "stolen", "fraud", "blocked card", "card blocked", "carte bloquée"
    ]):
        return "fraud", "fraud"

    if any(word in text for word in [
        "not working", "down", "failing", "error", "blocker", "connectivity",
        "stopped working", "submissions not working", "resume builder",
        "unable to take the test", "all requests are failing",
        "none of the submissions"
    ]):
        return "technical_issue", "bug"
    
    if any(word in text for word in [
        "lost access", "workspace", "seat", "admin", "owner", "login",
        "remove them", "remove an interviewer", "remove a user", "employee has left"
    ]):
        return "account_access", "account_access"

    if any(word in text for word in [
        "test score", "score dispute", "recruiter", "increase my score",
        "move me to the next round", "graded me unfairly", "review my answers",
        "test", "assessment", "candidate", "score", "certificate", "interviewer",
        "rescheduling", "mock interview", "compatible check", "inactivity",
        "submissions", "challenge", "graded"
    ]):
        return "assessment", "product_issue"

    if any(word in text for word in [
        "refund", "payment", "charge", "money", "subscription", "order id",
        "dispute", "pause our subscription"
    ]):
        return "billing", "billing"

    if any(word in text for word in [
        "privacy", "data", "crawl", "crawling", "models", "website"
    ]):
        return "privacy", "privacy"

    if any(word in text for word in [
        "lti", "students", "college", "professor"
    ]):
        return "education", "product_issue"

    if any(word in text for word in [
        "cash", "urgent cash", "minimum spend", "visa card", "merchant"
    ]):
        return "general_support", "product_issue"

    return "general_support", "product_issue"


def retrieve_docs(issue, subject, company, corpus):
    text = f"{issue} {subject}".lower()
    company_value = str(company).strip().lower()

    if company_value in ["", "none"]:
        return []

    stop_words = {
        "the", "and", "for", "with", "this", "that", "have", "from",
        "your", "please", "help", "need", "what", "when", "where",
        "about", "into", "after", "before", "because", "can", "you",
        "are", "was", "were", "has", "had", "our", "their", "them"
    }

    words = []
    for word in text.split():
        cleaned = word.strip(".,!?;:'\"()[]{}").lower()
        if len(cleaned) > 3 and cleaned not in stop_words:
            words.append(cleaned)

    scored_docs = []

    for doc in corpus:
        if doc["company"].lower() != company_value:
            continue

        content = doc["content"].lower()
        path = doc["path"].lower()

        score = 0

        for word in words:
            if word in content:
                score += 1
            if word in path:
                score += 2

        scored_docs.append((score, doc))

    scored_docs.sort(reverse=True, key=lambda item: item[0])

    return [doc for score, doc in scored_docs[:2] if score > 0]


def should_escalate(issue, subject, company, request_type, docs):
    text = f"{issue} {subject} {company}".lower()
    company_value = str(company).strip().lower()

    if company_value in ["", "none"]:
        return "Escalated"

    risky_phrases = [
        "restore my access",
        "not the workspace owner",
        "not the workspace owner or admin",
        "increase my score",
        "move me to the next round",
        "refund me today",
        "refund asap",
        "ban the seller",
        "identity has been stolen",
        "security vulnerability",
        "all requests are failing",
        "delete all files",
        "internal rules",
        "logic exact",
        "order id",
        "please make visa refund",
        "review my answers",
        "tell the company",
        "none of the submissions",
        "submissions across any challenges",
        "submissions not working",
        "graded me unfairly",
        "platform must have graded",
        "unable to take the test",
        "connectivity",
        "blocker",
        "urgent cash",
        "cash"
    ]

    if any(phrase in text for phrase in risky_phrases):
        return "Escalated"

    if request_type in ["account_access", "billing", "fraud", "security", "bug"]:
        return "Escalated"

    if not docs:
        return "Escalated"

    return "Replied"


def clean_doc_excerpt(text, limit=450):
    text = text.replace("\n", " ").replace("\r", " ")
    text = " ".join(text.split())

    if len(text) > limit:
        return text[:limit].rsplit(" ", 1)[0] + "..."

    return text


def generate_response(issue, subject, company, product_area, request_type, status, docs):
    if request_type == "invalid":
        return (
            "I am sorry, this request is out of scope and cannot be handled by this support system."
        )

    if status == "Escalated":
        if docs:
            excerpt = clean_doc_excerpt(docs[0]["content"], 300)

            return (
                "Hi,\n\n"
                f"I understand your issue regarding {product_area}.\n\n"
                "I found related support documentation, but this request may require manual review, "
                "account-specific action, or sensitive decision-making.\n\n"
                "Relevant guidance found:\n\n"
                f"{excerpt}\n\n"
                "Please contact official support or the appropriate account administrator for further assistance."
            )

        return (
            "Hi,\n\n"
            f"This request involves {product_area} and requires manual review or sensitive handling. "
            "I cannot safely resolve it using only the provided support documentation. "
            "Please contact support for further assistance."
        )

    if docs:
        excerpt = clean_doc_excerpt(docs[0]["content"], 500)

        return (
            "Hi,\n\n"
            "Based on the provided support documentation, here is the relevant guidance:\n\n"
            f"{excerpt}\n\n"
            "If this does not resolve the issue, please contact support."
        )

    return (
        "Escalate to a human. I could not find enough relevant support documentation "
        "to answer this safely."
    )


def generate_justification(issue, product_area, request_type, status, docs):
    issue_text = issue.lower()

    if any(word in issue_text for word in ["refund", "payment", "charge", "money", "subscription"]):
        reason = "Detected billing or payment-related keywords"
    elif any(word in issue_text for word in ["access", "login", "workspace", "admin", "seat"]):
        reason = "Detected account access or permission-related keywords"
    elif any(word in issue_text for word in ["not working", "error", "failing", "down", "blocker", "connectivity", "submissions"]):
        reason = "Detected technical failure or bug-related keywords"
    elif any(word in issue_text for word in ["fraud", "stolen", "identity", "blocked"]):
        reason = "Detected fraud or security-sensitive keywords"
    elif any(word in issue_text for word in ["vulnerability", "bug bounty", "security"]):
        reason = "Detected security vulnerability-related keywords"
    elif any(word in issue_text for word in ["test", "assessment", "candidate", "certificate", "score"]):
        reason = "Detected assessment or candidate-management keywords"
    elif any(word in issue_text for word in ["data", "privacy", "crawl", "crawling"]):
        reason = "Detected privacy or data-related keywords"
    else:
        reason = "General classification based on ticket keywords"

    doc_path = docs[0]["path"] if docs else "no relevant document found"

    return (
        f"{reason}. Classified as product_area={product_area}, request_type={request_type}. "
        f"Decision={status}. Relevant document used: {doc_path}."
    )


def write_output(results):
    fieldnames = [
        "issue",
        "subject",
        "company",
        "response",
        "product_area",
        "status",
        "request_type",
        "justification"
    ]

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def write_log(results):
    with open(LOG_FILE, "w", encoding="utf-8") as file:
        file.write("Support triage agent run log\n")
        file.write("============================\n\n")

        for index, row in enumerate(results, start=1):
            file.write(f"Ticket {index}\n")
            file.write(f"Subject: {row['subject']}\n")
            file.write(f"Company: {row['company']}\n")
            file.write(f"Product Area: {row['product_area']}\n")
            file.write(f"Request Type: {row['request_type']}\n")
            file.write(f"Status: {row['status']}\n")
            file.write(f"Justification: {row['justification']}\n")
            file.write("-" * 60 + "\n")


def main():
    tickets = load_tickets()
    corpus = load_corpus()

    results = []

    for ticket in tickets:
        issue = ticket["issue"]
        subject = ticket["subject"]
        company = ticket["company"]

        product_area, request_type = classify_request(issue, subject, company)
        docs = retrieve_docs(issue, subject, company, corpus)
        status = should_escalate(issue, subject, company, request_type, docs)

        response = generate_response(
            issue,
            subject,
            company,
            product_area,
            request_type,
            status,
            docs
        )

        justification = generate_justification(
            issue,
            product_area,
            request_type,
            status,
            docs
        )

        results.append({
            "issue": issue,
            "subject": subject,
            "company": company,
            "response": response,
            "product_area": product_area,
            "status": status,
            "request_type": request_type,
            "justification": justification
        })

    write_output(results)
    write_log(results)

    print(f"Processed {len(results)} tickets.")
    print(f"Output written to: {OUTPUT_FILE}")
    print(f"Log written to: {LOG_FILE}")


if __name__ == "__main__":
    main()