from flask import Flask, request, jsonify
from io import BytesIO
import pytesseract
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import cv2
import re

# --- Set your tesseract executable path ---
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = Flask(__name__)

# ---------- OCR Helpers ----------

def get_text(file_storage):
    """
    Read text from a file-like object (PDF or image)
    """
    file_storage.seek(0)  # Reset pointer
    file_bytes = BytesIO(file_storage.read())

    # --- Try PDF first ---
    try:
        doc = fitz.open(stream=file_bytes.read(), filetype="pdf")
        page = doc.load_page(0)  # first page only
        pix = page.get_pixmap(dpi=300)

        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n == 4:  # RGBA
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        if pix.n != 1:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img

        text = pytesseract.image_to_string(gray)
        return text
    except Exception as e_pdf:
        print("Not a PDF, trying image:", e_pdf)

    # --- Fallback to image ---
    try:
        file_bytes.seek(0)
        img = Image.open(file_bytes)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e_img:
        print("Cannot read file:", e_img)
        raise ValueError("Cannot read file as PDF or image")


def extract_aadhaar_details(text):
    dob_match = re.search(r'\bDOB\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})', text, re.I)
    dob = dob_match.group() if dob_match else "NOT FOUND"
    gender = (
        "MALE" if re.search(r'\bMALE\b', text, re.I)
        else "FEMALE" if re.search(r'\bFEMALE\b', text, re.I)
        else "NOT FOUND"
    )
    aadhaar_match = re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', text)
    aadhaar = aadhaar_match.group() if aadhaar_match else "NOT FOUND"
    return {"dob": dob, "gender": gender, "aadhaar": aadhaar}


def extract_student_and_parents(text):
    text_upper = text.upper()

    # CBSE Pattern Detection
    if "CENTRAL BOARD OF SECONDARY EDUCATION" in text_upper:

        student_match = re.search(
            r"THIS IS TO CERTIFY THAT\s+([A-Z ]+)",
            text_upper
        )
        student = student_match.group(1).strip().title() if student_match else "NOT FOUND"

        mother_match = re.search(
            r"MOTHER'?S NAME\s+([A-Z ]+)",
            text_upper
        )
        mother = mother_match.group(1).strip().title() if mother_match else "NOT FOUND"

        father_match = re.search(
            r"FATHER'?S.*?NAME\s+([A-Z ]+)",
            text_upper
        )
        father = father_match.group(1).strip().title() if father_match else "NOT FOUND"

        return student, father, mother

    lines = [l.strip() for l in text.split("\n") if l.strip()]
    REMOVE_WORDS = [
        "CERT","SHRI","SMT","SON OF","DAUGHTER OF",
        "S/O","D/O","FATHER'S NAME","MOTHER S NAME",
        "NAME","WAME","LFIED THAT","IFIED THAT",
        "CERTIFIED THAT","FATHER S"
    ]

    def clean_line(line):
        line = re.sub(r'[^A-Za-z ]', ' ', line)
        return re.sub(r'\s+', ' ', line).strip()

    def remove_titles(name):
        name = name.upper()
        for w in REMOVE_WORDS:
            name = name.replace(w, "")
        return name.title().strip()

    def mostly_caps(line):
        letters = sum(c.isupper() for c in line)
        total = sum(c.isalpha() for c in line)
        return total > 0 and (letters / total) > 0.6

    student, father, mother = "NOT FOUND", "NOT FOUND", "NOT FOUND"
    student_index = -1

    for i, line in enumerate(lines):
        if line.upper().startswith("NAME") or line.upper().startswith("WAME"):
            part = line.split(" ", 1)[1] if " " in line else line
            student = remove_titles(clean_line(part))
            student_index = i
            break

    if student == "NOT FOUND":
        for i, line in enumerate(lines):
            if "REGULAR" in line.upper():
                for j in range(i + 1, min(i + 10, len(lines))):
                    if mostly_caps(lines[j]):
                        student = remove_titles(clean_line(lines[j]))
                        student_index = j
                        break
                break

    for i, line in enumerate(lines):
        if "DAUGHTER OF" in line.upper() or "SON OF" in line.upper():
            if i + 1 < len(lines):
                mother = remove_titles(clean_line(lines[i + 1]))
            if i + 2 < len(lines):
                father = remove_titles(clean_line(lines[i + 2]))
            break

    if (father == "NOT FOUND" or mother == "NOT FOUND") and student_index != -1:
        candidates = [
            lines[k] for k in range(student_index + 1, min(student_index + 10, len(lines)))
            if mostly_caps(lines[k])
        ]
        if len(candidates) >= 1:
            father = remove_titles(clean_line(candidates[0]))
        if len(candidates) >= 2:
            mother = remove_titles(clean_line(candidates[1]))

    return student, father, mother

# ---------- Flask OCR Route ----------

@app.route("/ocr", methods=["POST"])
def ocr_api():
    try:
        if "aadhaar" not in request.files or "memo" not in request.files:
            return jsonify({"error": "Both files required"}), 400

        aadhaar_file = request.files["aadhaar"]
        memo_file = request.files["memo"]

        print("Received files:", aadhaar_file.filename, memo_file.filename)

        a_text = get_text(aadhaar_file)
        m_text = get_text(memo_file)

        aadhaar_data = extract_aadhaar_details(a_text)
        student, father, mother = extract_student_and_parents(m_text)

        return jsonify({
            "student_name": student,
            "father_name": father,
            "mother_name": mother,
            "dob": aadhaar_data["dob"],
            "gender": aadhaar_data["gender"],
            "aadhaar": aadhaar_data["aadhaar"]
        })

    except Exception as e:
        print("OCR error:", e)
        return jsonify({"error": str(e)}), 500

# ---------- Run Flask ----------

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)