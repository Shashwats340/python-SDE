from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List
from typing_extensions import Annotated
import uuid
import os
import cv2
import numpy as np
import pytesseract
import re
import spacy
from PIL import Image
from io import BytesIO
from pdf2image import convert_from_bytes

# 👉 Set Tesseract path (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load NLP model
nlp = spacy.load("en_core_web_sm")

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Multi-document scanning API is working!"}


# Create upload folder
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# =========================
# 🔹 PREPROCESSING
# =========================
def preprocess_image(image: Image.Image):
    img = np.array(image)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 150, 255, cv2.THRESH_BINARY)

    return thresh


# =========================
# 🔹 OCR
# =========================
def extract_text(image_array):
    return pytesseract.image_to_string(image_array)


# =========================
# 🔹 CLASSIFICATION
# =========================
def classify_document(text: str):
    text = text.lower()

    if "passport" in text:
        return "Passport", 0.90
    elif "driving" in text or "license" in text:
        return "Driving License", 0.85
    elif "vehicle" in text and "registration" in text:
        return "Vehicle Card", 0.85
    elif "id" in text and "national" in text:
        return "ID Card", 0.80
    else:
        return "Unknown", 0.0


# =========================
# 🔹 REGEX EXTRACTION
# =========================
def extract_with_regex(text):
    data = {}

    id_match = re.search(r'\b\d{6,}\b', text)
    if id_match:
        data["id_number"] = id_match.group()

    date_match = re.search(r'\b\d{2}[/-]\d{2}[/-]\d{4}\b', text)
    if date_match:
        data["date"] = date_match.group()

    return data


# =========================
# 🔹 NER EXTRACTION
# =========================
def extract_with_ner(text):
    doc = nlp(text)
    data = {}

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            data["name"] = ent.text
        elif ent.label_ == "GPE":
            data["location"] = ent.text

    return data


# =========================
# 🔹 DOC-SPECIFIC EXTRACTION
# =========================
def extract_fields_by_doc_type(text, doc_type):
    data = {}

    if doc_type == "Passport":
        matches = re.findall(r'[A-Z0-9]{6,9}', text)
        if matches:
            data["passport_number"] = matches[0]

    elif doc_type == "Driving License":
        matches = re.findall(r'[A-Z0-9]{5,}', text)
        if matches:
            data["license_number"] = matches[0]

    elif doc_type == "Vehicle Card":
        matches = re.findall(r'\b[A-Z]{2}\d{1,2}[A-Z]{1,3}\d{3,4}\b', text)
        if matches:
            data["registration_number"] = matches[0]

    elif doc_type == "ID Card":
        match = re.search(r'\b\d{6,}\b', text)
        if match:
            data["id_number"] = match.group()

    return data


@app.post("/api/v1/scan-multiple")
async def scan_multiple(
    file1: UploadFile = File(...),
    file2: UploadFile = File(None),
    file3: UploadFile = File(None)
):
    files = [f for f in [file1, file2, file3] if f is not None]
    try:
        all_results = []

        for file in files:
            contents = await file.read()

            # Handle PDF or Image
            if file.filename.lower().endswith(".pdf"):
                images = convert_from_bytes(contents)
            else:
                images = [Image.open(BytesIO(contents))]

            doc_pages = []

            for page_num, image in enumerate(images):
                request_id = str(uuid.uuid4())

                # Save image
                file_path = os.path.join(UPLOAD_DIR, f"{request_id}.png")
                image.save(file_path)

                # Preprocess
                processed = preprocess_image(image)

                # OCR
                text = extract_text(processed)

                # Classification
                doc_type, confidence = classify_document(text)

                # Extraction
                regex_data = extract_with_regex(text)
                ner_data = extract_with_ner(text)
                doc_specific = extract_fields_by_doc_type(text, doc_type)

                final_data = {**regex_data, **ner_data, **doc_specific}

                doc_pages.append({
                    "page": page_num + 1,
                    "doc_type": doc_type,
                    "classification_confidence": confidence,
                    "raw_text": text,
                    "fields": final_data
                })

            all_results.append({
                "file_name": file.filename,
                "pages": doc_pages
            })

        return {
            "status": "success",
            "documents": all_results
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        
        )
    
    # in the next doc we will upgrade to paddle OCR 