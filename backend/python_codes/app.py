# from flask import Flask, request, jsonify, render_template
# import pytesseract
# import cv2
# import fitz
# import os
# import re
# import numpy as np
# from PIL import Image

# app = Flask(__name__)

# UPLOAD_FOLDER = "uploads"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# # ===============================
# # OCR HELPERS
# # ===============================

# def image_to_text(path):
#     img = cv2.imread(path)
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     text = pytesseract.image_to_string(gray)
#     return text


# def pdf_to_text(pdf_path):
#     doc = fitz.open(pdf_path)
#     page = doc.load_page(0)
#     pix = page.get_pixmap(dpi=300)

#     img = np.frombuffer(pix.samples, dtype=np.uint8)
#     img = img.reshape(pix.height, pix.width, pix.n)

#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     text = pytesseract.image_to_string(gray)

#     return text


# # ===============================
# # EXTRACTION FUNCTIONS
# # ===============================

# def extract_aadhaar_number(text):

#     text = text.replace("O","0").replace("I","1").replace("l","1") \
#                .replace("B","8").replace("Z","2").replace("S","5")

#     numbers = re.findall(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', text)

#     if numbers:
#         return numbers[0].replace("-", " ")

#     return ""


# def extract_dob(text):
#     m = re.search(r'\b(\d{2}[/-]\d{2}[/-]\d{4})\b', text)
#     return m.group(1) if m else ""


# def extract_gender(text):
#     if re.search(r'\bMALE\b', text, re.I):
#         return "Male"
#     if re.search(r'\bFEMALE\b', text, re.I):
#         return "Female"
#     return ""


# def extract_student_and_parents(text):

#     lines = [l.strip() for l in text.split("\n") if l.strip()]

#     def clean_line(line):
#         line = re.sub(r'[^A-Za-z ]',' ',line)
#         return re.sub(r'\s+',' ',line).strip()

#     def mostly_caps(line):
#         letters = sum(c.isupper() for c in line)
#         total = sum(c.isalpha() for c in line)
#         return total > 0 and (letters/total) > 0.6

#     student = ""
#     father = ""
#     mother = ""

#     for i,line in enumerate(lines):
#         if line.upper().startswith("NAME"):
#             parts = line.split(" ",1)
#             if len(parts) > 1:
#                 student = clean_line(parts[1]).title()
#             break

#     if not student:
#         for line in lines:
#             if mostly_caps(line):
#                 student = clean_line(line).title()
#                 break

#     parent_candidates = []

#     for line in lines:
#         if mostly_caps(line):
#             parent_candidates.append(clean_line(line).title())

#     if len(parent_candidates) >= 2:
#         father = parent_candidates[0]
#         mother = parent_candidates[1]

#     return student or "NOT FOUND", father or "NOT FOUND", mother or "NOT FOUND"


# # ===============================
# # ROUTES
# # ===============================

# @app.route("/")
# def home():
#     return "OCR Server Running"


# # 🔥 THIS IS THE ROUTE NODE WILL CALL
# @app.route("/ocr", methods=["POST"])
# def ocr_api():

#     if "file" not in request.files:
#         return jsonify({"error": "No file uploaded"}), 400

#     file = request.files["file"]
#     filename = file.filename
#     path = os.path.join(UPLOAD_FOLDER, filename)
#     file.save(path)

#     try:
#         if path.lower().endswith(".pdf"):
#             text = pdf_to_text(path)
#         else:
#             text = image_to_text(path)

#         aadhaar = extract_aadhaar_number(text)
#         dob = extract_dob(text)
#         gender = extract_gender(text)
#         student, father, mother = extract_student_and_parents(text)

#         return jsonify({
#             "raw_text": text,
#             "aadhaar": aadhaar,
#             "dob": dob,
#             "gender": gender,
#             "student_name": student,
#             "father_name": father,
#             "mother_name": mother
#         })

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

#     finally:
#         if os.path.exists(path):
#             os.remove(path)


# # ===============================
# # MAIN SERVER
# # ===============================

# if __name__ == "__main__":
#     app.run(port=5000, debug=True, use_reloader=False)

from flask import Flask, render_template, request, jsonify
import cv2, fitz, os, re, numpy as np
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

from PIL import Image

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def pdf_to_text(pdf_path):

    doc = fitz.open(pdf_path)
    page = doc.load_page(0)     # first page
    pix = page.get_pixmap(dpi=300)

    img = np.frombuffer(pix.samples, dtype=np.uint8)
    img = img.reshape(pix.height, pix.width, pix.n)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    text = pytesseract.image_to_string(gray)
    return text

def image_to_text(path):
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return text

def extract_aadhaar_details(text):

    dob = ""
    gender = ""
    aadhaar = ""

    # ---- DOB ----
    dob_match = re.search(r'\bDOB\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})', text, re.I)
    if dob_match:
        dob = dob_match.group()

    # ---- GENDER ----
    if re.search(r'\bMALE\b', text, re.I):
        gender = "MALE"
    elif re.search(r'\bFEMALE\b', text, re.I):
        gender = "FEMALE"

    # ---- AADHAAR NUMBER ----
    ad_match = re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', text)
    if ad_match:
        aadhaar = ad_match.group()

    return {
        "dob": dob if dob else "NOT FOUND",
        "gender": gender if gender else "NOT FOUND",
        "aadhaar": aadhaar if aadhaar else "NOT FOUND"
    }


import re

def extract_student_and_parents(text):

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    REMOVE_WORDS = [
        "SHRI","SMT",
        "SON OF","DAUGHTER OF","S/O","D/O",
        "FATHER'S NAME","MOTHER S NAME",
        "NAME","WAME","IFIED THAT"
    ]

    # ---------------- HELPERS ----------------

    def clean_line(line):
        line = re.sub(r'[^A-Za-z ]',' ',line)
        line = re.sub(r'\s+',' ',line).strip()
        return line

    def remove_titles(name):
        name = name.upper()
        for w in REMOVE_WORDS:
            name = name.replace(w, "")
        return name.title().strip()

    def mostly_caps(line):
        letters = sum(c.isupper() for c in line)
        total = sum(c.isalpha() for c in line)
        return total > 0 and (letters/total) > 0.6

    # ----------------------------------------

    student = ""
    father = ""
    mother = ""

    student_index = -1   # ⭐ IMPORTANT FIX

    # ========== STUDENT (ICSE) ==========
    for i,line in enumerate(lines):
        if line.upper().startswith("NAME") or line.upper().startswith("WAME"):
            part = line.split(" ",1)[1]
            student = remove_titles(clean_line(part))
            student_index = i
            break

    # ========== STUDENT (SSC) ==========
    if not student:
        for i,line in enumerate(lines):
            if "REGULAR" in line.upper():
                for j in range(i+1, min(i+10,len(lines))):
                    if mostly_caps(lines[j]):
                        student = remove_titles(clean_line(lines[j]))
                        student_index = j
                        break
                break

    # =================================================
    # ========== PARENTS METHOD 1 : ICSE ==========
    # =================================================

    for i,line in enumerate(lines):
        if "DAUGHTER OF" in line.upper() or "SON OF" in line.upper():

            if i+1 < len(lines):
                mother = remove_titles(clean_line(lines[i+1]))

            if i+2 < len(lines):
                father = remove_titles(clean_line(lines[i+2]))

            break

    # =================================================
    # ========== PARENTS METHOD 2 : SSC ==========
    # =================================================

    if (not father or not mother) and student_index != -1:

        parent_candidates = []

        for k in range(student_index+1, min(student_index+10,len(lines))):

            if mostly_caps(lines[k]):
                parent_candidates.append(lines[k])

        if len(parent_candidates) >= 1:
            father = remove_titles(clean_line(parent_candidates[0]))

        if len(parent_candidates) >= 2:
            mother = remove_titles(clean_line(parent_candidates[1]))

    # =================================================

    if not student:
        student = "NOT FOUND"
    if not father:
        father = "NOT FOUND"
    if not mother:
        mother = "NOT FOUND"

    return student, father, mother

# @app.route("/")
# def home():
#     return render_template("index.html")

# @app.route("/upload", methods=["POST"])
# def upload():

#     aadhaar = request.files["aadhaar"]
#     memo = request.files["memo"]

#     a_path = os.path.join(UPLOAD_FOLDER, aadhaar.filename)
#     m_path = os.path.join(UPLOAD_FOLDER, memo.filename)

#     aadhaar.save(a_path)
#     memo.save(m_path)

#     a_text = pdf_to_text(a_path) if a_path.lower().endswith(".pdf") else image_to_text(a_path)
#     m_text = pdf_to_text(m_path)

#     a_data = extract_aadhaar_details(a_text)
#     student, father, mother = extract_student_and_parents(m_text)

#     return jsonify({
#         "Student name": student,
#         "Father name": father,
#         "Mother name": mother,
#         "dob": a_data["dob"],
#         "gender": a_data["gender"],
#         "aadhaar": a_data["aadhaar"]
#     })

@app.route("/ocr", methods=["POST"])
def ocr_api():

    if "aadhaar" not in request.files or "memo" not in request.files:
        return jsonify({"error": "Both files required"}), 400

    aadhaar_file = request.files["aadhaar"]
    memo_file = request.files["memo"]

    a_path = os.path.join(UPLOAD_FOLDER, aadhaar_file.filename)
    m_path = os.path.join(UPLOAD_FOLDER, memo_file.filename)

    aadhaar_file.save(a_path)
    memo_file.save(m_path)

    try:
        a_text = pdf_to_text(a_path) if a_path.lower().endswith(".pdf") else image_to_text(a_path)
        m_text = pdf_to_text(m_path) if m_path.lower().endswith(".pdf") else image_to_text(m_path)

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
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(a_path):
            os.remove(a_path)
        if os.path.exists(m_path):
            os.remove(m_path)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)