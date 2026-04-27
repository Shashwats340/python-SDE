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

