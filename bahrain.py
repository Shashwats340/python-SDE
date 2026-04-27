from email.mime import text

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List
from typing_extensions import Annotated

import uuid
import os
import cv2
import numpy as np
import re
import spacy

from PIL import Image
from io import BytesIO
from pdf2image import convert_from_bytes

from paddleocr import PaddleOCR

#load models 
ocr = PaddleOCR(
    use_angle_cls=True,  # angle classification / detects rotated text
    lang='ar'  # language arabic + mixed docs

)

nlp = spacy.load("en_core_web_sm")    #nlp model - english NER only 

app = FastAPI(
    title="Bahrain OCR doc scanner API",
    version = "1.0",
)

@app.get("/")
def home():
    return {"message": "Bahrain OCR API is working!"}

#creating upload folder

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def preprocess_image(image: Image.Image):
    img = np.array(image)

    # RGB → Gray
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Blur removes noise
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Convert to Black/White
    _, thresh = cv2.threshold(
        blur, 150, 255, cv2.THRESH_BINARY
    )

    return thresh

#extraction 
def extract_text(image_array):
    result = ocr.ocr(image_array, cls=True)
    texts = []
    confs = []

    if result and result[0]:

        for line in result[0]:
            text = line[1][0]
            conf = line[1][1]
            texts.append(text)
            confs.append(conf)
    
    final_text = " ".join(texts)
    avg_conf =(
        sum(confs) / len(confs) if confs else 0
    )
    return final_text, avg_conf

#classifier (bahrain)

def classify_document(text):
    t = text.lower()
    if "passport" in t or "جواز" in text:
        return "Passport", 0.95
    
    elif (
         "driving" in t or
        "licence" in t or
        "license" in t or
        "رخصة" in text
    ):
        return "Driving License", 0.93
    
    elif (
        "vehicle" in t or
        "registration" in t or
        "traffic" in t or
        "مركبة" in text or
        "مرور" in text or
        "ترخيص" in text
    ):
        return "Vehicle Card", 0.92
    
    elif (
        "identity" in t or
        "national" in t or
        "cpr" in t or
        "بطاقة" in text or
        "هوية" in text
    ):
        return "National ID", 0.90

    else:
        return "Unknown", 0.50
    
#regex extraction

def extract_with_regex(text):

    data = {}

    date_match = re.search(
        r'\b\d{4}[/-]\d{2}[/-]\d{2}\b',
        text
    )
    if date_match:
        data["date"] = date_match.group()

    # long numbers
    num_match = re.search(
        r'\b\d{8,15}\b',
        text
    )
    if num_match:
        data["document_number"] = num_match.group()

    return data

#NER extraction

def extract_with_ner(text):

    data = {}

    doc = nlp(text)

    for ent in doc.ents:

        if ent.label_ == "PERSON":
            data["name"] = ent.text

        elif ent.label_ == "GPE":
            data["location"] = ent.text

    return data

# doc specific extraction

def extract_fields_by_doc_type(text, doc_type):
    data = {}

    if doc_type == "Passport":
        m = re.findall(r'[A-Z0-9]{6,9}', text)
        if m:
            data["passport_number"] = m[0]

    elif doc_type == "Driving License":
        m = re.findall(r'\b\d{6,12}\b', text)
        if m:
            data["license_number"] = m[0]

    elif doc_type == "Vehicle Card":
        m = re.findall(r'[A-Z0-9]{8,20}', text)
        if m:
            data["vehicle_number"] = m[0]
        
        year = re.search(r'\b20\d{2}\b', text)
        if year:
            data["model_year"] = year.group()
    
    elif doc_type == "National ID":
        m = re.search(r'\b\d{9}\b', text)

        if m:
            data["cpr_number"] = m.group()

    return data

@app.post("/api/v1/scan-multiple")
async def scan_multiple(
    files: Annotated[List[UploadFile], File(...)]

):
    try:
        all_results = []

        for file in files:
            contents = await file.read()

            if file.filename.lower().endswith(".pdf"):
                images = convert_from_bytes(contents)
            else:
                images = [
                    Image.open(BytesIO(contents))
                ]
            pages = []

            for page_num, image in enumerate(images):

                request_id = str(uuid.uuid4())

                file_path = os.path.join(
                    UPLOAD_DIR,
                    f"{request_id}.png"
                )

                image.save(file_path)

                processed = preprocess_image(image)
                text, ocr_conf = extract_text(processed)
                doc_type, cls_conf = classify_document(text)

                regex_data = extract_with_regex(text)
                ner_data = extract_with_ner(text)
                doc_data = extract_fields_by_doc_type(
                    text,
                    doc_type
                )
            #combine all extracted data into one dictionary
                final_data = {
                    **regex_data,
                    **ner_data,
                    **doc_data
                }

                pages.append({
                    "page": page_num + 1,
                    "doc_type": doc_type,
                    "classification_confidence": round(cls_conf, 3),
                    "ocr_confidence": round(ocr_conf, 3),
                    "raw_text": text,
                    "fields": final_data

                })
            
            all_results.append({
                "file_name": file.filename,
                "pages": pages
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
    