from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional
import uuid
import os
from PIL import Image
import base64
from io import BytesIO

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def health_check():
    return {"status": "API is running"}

@app.post("/api/v1/scan")
async def upload_image(
    file: Optional[UploadFile] = File(None),
    base64_image: Optional[str] = Form(None),
    doc_type: Optional[str] = Form("auto"),
    language: Optional[str] = Form("auto"),
    confidence_threshold: Optional[float] = Form(0.75),

):
    try:
        request_id = str(uuid.uuid4())

        #case 1: file upload
        if file:
            contents = await file.read()
            image = Image.open(BytesIO(contents))

        #case 2: base64 image
        elif base64_image:
            image_data = base64.b64decode(base64_image)
            image = Image.open(BytesIO(image_data))

        else:
            return JSONResponse(status_code=400, content={"error": "No image provided"},
            )

  # Save image
        file_path = os.path.join(UPLOAD_DIR, f"{request_id}.png")
        image.save(file_path)
        
 #  Placeholder for OCR / AI pipeline
        extracted_fields = {
            "name": {"value": "John Doe", "confidence": 0.92, "flagged": False},
            "id_number": {"value": "123456789", "confidence": 0.85, "flagged": False},
        }

        return {
            "request_id": request_id,
            "doc_type": doc_type,
            "classification_confidence": 0.88,
            "fields": extracted_fields,
            "processing_time_ms": 1200,
            "file_saved_at": file_path,
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )
