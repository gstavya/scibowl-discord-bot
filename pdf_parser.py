import pdfplumber
import requests
import re
from collections import defaultdict

# ==========================
# CONFIG
# ==========================

PDF_URL_TEMPLATE = (
    "https://science.osti.gov/-/media/wdts/nsb/pdf/"
    "HS-Sample-Questions/Sample-Set-10/{}A_HS_Reg_2016.pdf"
)

SUBJECT_MAP = {
    "Physics": "phy",
    "Math": "math",
    "Biology": "bio",
    "Chemistry": "chem",
    "Earth and Space": "ess",
    "Energy": "energy",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://science.osti.gov/"
}

# ==========================
# DOWNLOAD
# ==========================

def download_pdf(url, path):
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    with open(path, "wb") as f:
        f.write(r.content)
    return path

# ==========================
# EXTRACT
# ==========================

def extract_text(path):
    pages = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            txt = page.extract_text()
            if txt:
                pages.append(txt)
    return "\n".join(pages)

# ==========================
# NORMALIZE
# ==========================

def normalize_text(text):
    # Remove page headers
    text = re.sub(
        r"2016 NSB® Regional High School Questions Page \d+",
        "",
        text
    )

    # Fix broken chemical formulas
    text = re.sub(r"C\s*5\s*12", "C5H12", text)

    # Join broken lines mid-sentence
    text = re.sub(r"\n(?=[a-z])", " ", text)
    text = re.sub(r"\n+", "\n", text)

    return text.strip()

# ==========================
# SPLIT QUESTIONS
# ==========================

def split_questions(text):
    pattern = re.compile(
        r"(TOSS-UP|BONUS)\s*\n?\s*\d+\)\s*"
        r"(Physics|Math|Biology|Chemistry|Earth and Space|Energy)\s*–",
        re.IGNORECASE
    )
    return pattern.split(text)

# ==========================
# PARSE QUESTIONS
# ==========================

def parse_questions(text):
    questions = defaultdict(list)
    parts = split_questions(text)

    for i in range(1, len(parts), 3):
        qa_type = parts[i]
        subject = parts[i + 1]
        body = parts[i + 2]

        if subject not in SUBJECT_MAP:
            continue

        key = SUBJECT_MAP[subject]

        qtype = "Multiple Choice" if "Multiple Choice" in body else "Short Answer"

        ans_match = re.search(r"Answer:\s*(.+)", body, re.IGNORECASE)
        if not ans_match:
            continue

        answer_text = ans_match.group(1).strip()
        question_text = body[:ans_match.start()].strip()

        # Remove duplicated question-type labels from PDF
        question_text = re.sub(
            r"^(Short Answer|Multiple Choice)\s*",
            "",
            question_text,
            flags=re.IGNORECASE
        )

        if qtype == "Multiple Choice":
            choices = re.findall(r"([WXYZ])\)\s*(.+)", question_text)
            stem = re.split(r"[WXYZ]\)", question_text)[0].strip()
            choice_block = "\n".join(
                f"{k}) {v.strip()}" for k, v in choices
            )

            q = f"{subject.upper()} Multiple Choice: {stem}\n{choice_block}"
            answer = re.search(r"([WXYZ])", answer_text).group(1)

        else:
            q = f"{subject.upper()} Short Answer: {question_text}"
            answer = answer_text.split("(")[0].strip()

        questions[key].append({
            "q": q,
            "a": answer
        })

    return dict(questions)

# ==========================
# MERGE
# ==========================

def merge_questions(dest, src):
    for subject, qlist in src.items():
        dest[subject].extend(qlist)

# ==========================
# MAIN
# ==========================

if __name__ == "__main__":
    all_questions = defaultdict(list)

    for round_num in range(1, 18):
        print(f"Parsing round {round_num}...")

        url = PDF_URL_TEMPLATE.format(round_num)

        try:
            pdf_path = download_pdf(url, f"round_{round_num}.pdf")
            raw_text = extract_text(pdf_path)
            clean_text = normalize_text(raw_text)

            round_questions = parse_questions(clean_text)
            merge_questions(all_questions, round_questions)

        except Exception as e:
            print(f"⚠️ Failed round {round_num}: {e}")

    all_questions = dict(all_questions)

    import pprint

    print("\nquestions = ")
    pprint.pprint(all_questions, width=120, sort_dicts=False)
