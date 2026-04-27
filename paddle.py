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

