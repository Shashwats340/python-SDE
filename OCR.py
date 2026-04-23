import cv2
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional
import uuid
import os
import numpy as np
import re
import spacy
from PIL import Image
from io import BytesIO
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# load NLP model 
nlp = spacy.load("en_core_web_sm")

app = FastAPI(
    servers=[
        {"url": "http://127.0.0.1:8000"}
    ]
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# image preprocessing
def preprocess_image(image: Image.Image):
    img = np.array(image)

    # convert to grayscale 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #Noise removal
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    #threshold (binarization)
    _, thresh = cv2.threshold(blur, 150, 255, cv2.THRESH_BINARY)

    return thresh

#OCR function
def extract_text(image_array):
    text = pytesseract.image_to_string(image_array)
    return text

#regex extraction
def extract_with_regex(text):
    data = {}

    #ID number (example pattern)
    id_match = re.search(r'\b\d{4, }\b', text)
    if id_match:
        data['id_number'] = id_match.group()

    #Date 
    date_match =  re.search(r'\b\d{2}[/-]\d{2}[/-]\d{4}\b', text)
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

@app.post("/api/v1/scan")
async def scan_document(file: UploadFile = File(...)):
    try:
        request_id = str(uuid.uuid4())

        contents = await file.read()
        image = Image.open(BytesIO(contents))

        #save orignal 
        file_path = os.path.join(UPLOAD_DIR, f"{request_id}.png")
        image.save(file_path)

        processed = preprocess_image(image)  # preprocessing
        text = extract_text(processed)         # OCR extraction
        regex_data = extract_with_regex(text)    #extraction
        ner_data = extract_with_ner(text)        #`extraction
        extracted_fields = {
            "regex": regex_data,
             "ner": ner_data
}       #combine results from 2 dictionaries

        return {
            "request_id": request_id,
            "raw_text": text,
            "fields": extracted_fields,
            "processing_status": "success"

        }
    except Exception as e:
        return JSONResponse(                    #error handling
            status_code=500,
            content={"error": str(e)}
        )
    

    
    

