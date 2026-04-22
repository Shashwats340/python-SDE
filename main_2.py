from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional
import uuid
import os
from PIL import Image
import base64
from io import BytesIO

# FastAPI → creates your API server
# UploadFile → handles file uploads efficiently
# File, Form → define request inputs
# Image (PIL) → opens and processes images
# uuid → generates unique request IDs
# BytesIO → converts raw bytes into file-like object
app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
# Creates a folder named uploads/
# exist_ok=True prevents crash if folder already exists

@app.get("/")
def health_check():
    return {"status": "API is running"}
# Simple test route Used in:
# deployment (Docker / Render)
# uptime monitoring

@app.post("/api/v1/scan")       #This is your core endpoint Matches your document: POST /api/v1/scan
async def upload_image(
    file: Optional[UploadFile] = File(None),
    base64_image: Optional[str] = Form(None),
    doc_type: Optional[str] = Form("auto"),
    language: Optional[str] = Form("auto"),
    confidence_threshold: Optional[float] = Form(0.75),

):
# These are the input parameters for the endpoint:
# Parameter	   Purpose
# file	       Upload image file
# base64_image	Alternative input (API integration)
# doc_type	    Force document type (or auto detect later)
# language	    OCR language
# confidence_threshold	filter low-confidence results
# Supports both:
# frontend uploads
# backend-to-backend API calls
    try:
        request_id = str(uuid.uuid4())  #generates something like -"f47ac10b-58cc-4372-a567-0e02b2c3d479"

        #case 1: file upload reads the uploaded file , convert bytes to image ; load using PIL 
        if file:
            contents = await file.read()
            image = Image.open(BytesIO(contents))

        #case 2: base64 image , Decode base64 to bytes ; converts to image 
        elif base64_image:
            image_data = base64.b64decode(base64_image)
            image = Image.open(BytesIO(image_data))
        # case 3: no image provided; prevents empty requests 
        else:
            return JSONResponse(status_code=400, content={"error": "No image provided"},
            )

  # Save image - as uploads/<request_id>.png & we main disable storage for privacy 
        file_path = os.path.join(UPLOAD_DIR, f"{request_id}.png")
        image.save(file_path)
        
 #  Placeholder for OCR / AI pipeline - This simulates your - OCR, NER and field extraction 
 # later we will replace this with Tesseract , paddleOCR or Regex/ML 
        extracted_fields = {
            "name": {"value": "John Doe", "confidence": 0.92, "flagged": False},
            "id_number": {"value": "123456789", "confidence": 0.85, "flagged": False},
        }

# API response structure 
        return {
            "request_id": request_id,
            "doc_type": doc_type,
            "classification_confidence": 0.88,
            "fields": extracted_fields,
            "processing_time_ms": 1200,
            "file_saved_at": file_path,
        }
# error handling - catches any unexpected issues and returns a 500 error with the message
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )

# move to the next api related to the agent - Now its -Image → Save → Dummy JSON
# next it will be Image → OpenCV → OCR → NLP → JSON

