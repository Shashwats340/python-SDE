from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List
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

from OCR import extract_with_ner

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

nlp = spacy.load("en_core_web_sm")

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def preprocess_image(image: Image.Image):
    img = np.array(image)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)                 #blur / noise removal
    _, thresh = cv2.threshold(blur, 150, 255, cv2.THRESH_BINARY)     #it converts your image into pure B&W (binary image ) as OCR works best when text is black and bg is white
    return thresh

def extract_text(image_array):
    return pytesseract.image_to_string(image_array)

def classify_document(text: str):
    text = text.lower()

    if "passport" in text:
        return "Passport", 0.90
    
    elif "driving" in text or "license" in text:
        return "Driving License", 0.85
    
    elif "vehicle" in text and "registration" in text:
        return "Vehicle Card", 0.85
    
    elif "id" in text and "national" in text and "nationality" in text:
        return "ID Card", 0.80
    else:
        return "Unknown", 0.0

def extract_with_regex(text):
    data = {}

    id_match = re.search(r'\b\d{6,}\b', text)
    if id_match:
        data["id_number"] = id_match.group()

    date_match = re.search(r'\b\d{2}[/-]\d{2}[/-]\d{4}\b', text)
    if date_match:
        data["date"] = date_match.group()

    return data

def extract_with_ner(text):
    doc = nlp(text)
    data ={}

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            data["name"] = ent.text
        elif ent.label_ == "GPE":
            data["location"] = ent.text

    return data

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
            data["registration_card"] = matches[0]
    elif doc_type == "ID Card":
         match = re.search(r'\b\d{6,}\b', text)
         if match:
            data["id_number"] = match.group()

    return data

#multi doc API
