import uuid

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import cv2
import os
import numpy as np
import pytesseract
import re
import spacy 
from PIL import Image
from io import BytesIO
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

#load NLP model
nlp = spacy.load("en_core_web_sm")

app = FastAPI()
@app.get("/")
def test():
    return {"message": "working"}

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def preprocess_image(image: Image.Image):
    img = np.array(image)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 150, 255, cv2.THRESH_BINARY)
    return thresh

#ocr
def extract_text(image_array):
    text = pytesseract.image_to_string(image_array)
    return text

#doc detection
def classify_document(text: str):
    text_lower = text.lower()

    if "passport" in text_lower:
        return "Passport", 0.90
    
  
    elif "driving" in text_lower or "licence" in text_lower or "license" in text_lower:
        return "driving_licence", 0.85

    elif "vehicle" in text_lower or "registration" in text_lower:
        return "vehicle_card", 0.85

    elif "id" in text_lower or "national" in text_lower:
        return "id_card", 0.80

    else:
        return "unknown", 0.50
    
# regex extraction
def extract_with_regex(text):
    data = {}

    # ID number
    id_match = re.search(r'\b\d{6,}\b', text)
    if id_match:
        data["id_number"] = id_match.group()

    # Date
    date_match = re.search(r'\b\d{2}[/-]\d{2}[/-]\d{4}\b', text)
    if date_match:
        data["date"] = date_match.group()

    return data

#NER extraction
def extract_with_ner(text):
    doc = nlp(text)
    data = {}

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            data["name"] = ent.text
        elif ent.label_ == "GPE":
            data["location"] = ent.text

    return data

#doc type extraction
def extract_fields_by_doc_type(text, doc_type):
    data = {}

    if doc_type == "passport":
        matches = re.findall(r'[A-Z0-9]{6,9}', text)
        if matches:
            data["passport_number"] = matches[0]

    elif doc_type == "driving_licence":
        matches = re.findall(r'[A-Z0-9]{5,}', text)
        if matches:
            data["licence_number"] = matches[0]

    elif doc_type == "vehicle_card":
        matches = re.findall(r'[A-Z]{2}\d{4}', text)
        if matches:
            data["vehicle_number"] = matches[0]

    elif doc_type == "id_card":
        match = re.search(r'\b\d{6,}\b', text)
        if match:
            data["id_number"] = match.group()

    return data

@app.post("/api/v1/scan")
async def scan_document(file: UploadFile = File(...)):
    try:
        request_id = str(uuid.uuid4())

        contents = await file.read()
        image = Image.open(BytesIO(contents))

        # Save original file
        file_path = os.path.join(UPLOAD_DIR, f"{request_id}.png")
        image.save(file_path)

        # 🔸 Preprocess
        processed = preprocess_image(image)

        # 🔸 OCR
        text = extract_text(processed)

        # 🔸 Doc Type Detection
        doc_type, confidence = classify_document(text)

        # 🔸 Extraction
        regex_data = extract_with_regex(text)
        ner_data = extract_with_ner(text)
        doc_specific_data = extract_fields_by_doc_type(text, doc_type)

        # Merge all extracted data
        final_fields = {**regex_data, **ner_data, **doc_specific_data}

        return {
            "request_id": request_id,
            "doc_type": doc_type,
            "classification_confidence": confidence,
            "raw_text": text,
            "fields": final_fields,
            "processing_status": "success"
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )