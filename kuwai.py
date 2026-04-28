
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from paddleocr import PaddleOCR
from PIL import Image
from io import BytesIO
from pdf2image import convert_from_bytes
import numpy as np
import cv2
import uuid
import os
import re



app = FastAPI(
    title="Kuwait OCR API",
    version="1.0"
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)



ocr = PaddleOCR(
    use_angle_cls=True,
    lang='ar',
    det_db_thresh=0.2,
    det_db_box_thresh=0.3,
    det_db_unclip_ratio=1.8
)



@app.get("/")
def home():
    return {
        "status": "success",
        "message": "Kuwait OCR API Running"
    }


def preprocess_image(image):
    img = np.array(image)

    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # upscale
    img = cv2.resize(img, None, fx=2, fy=2)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # denoise
    gray = cv2.fastNlMeansDenoising(gray)

    # sharpen
    kernel = np.array([
        [0,-1,0],
        [-1,5,-1],
        [0,-1,0]
    ])

    sharp = cv2.filter2D(gray, -1, kernel)

    return sharp


def extract_text(image_array):
    try:
        result = ocr.ocr(image_array)

        texts = []
        confs = []

        # New PaddleOCR format
        if isinstance(result, list):

            for block in result:

                # Old format support
                if isinstance(block, list):
                    for line in block:
                        if len(line) >= 2:
                            txt = line[1][0]
                            conf = line[1][1]

                            texts.append(txt)
                            confs.append(conf)

                # New format support
                elif isinstance(block, dict):

                    if "rec_texts" in block:
                        texts.extend(block["rec_texts"])

                    if "rec_scores" in block:
                        confs.extend(block["rec_scores"])

        final_text = " ".join(texts).strip()

        avg_conf = round(
            sum(confs) / len(confs), 2
        ) if confs else 0

        return final_text, avg_conf

    except Exception as e:
        return "", 0


def classify_document(text):
    t = text.lower()

    if "الكويت" in t or "kuwait" in t:

        if "مرور" in t or "مركبة" in t:
            return "Kuwait Vehicle Card", 0.96

        if "مدنية" in t or "civil" in t:
            return "Kuwait Civil ID", 0.95

        if "passport" in t or "جواز" in t:
            return "Kuwait Passport", 0.94

    return "Unknown", 0


def extract_fields(text, doc_type):
    data = {}

    # dates
    dates = re.findall(r'\d{4}-\d{2}-\d{2}', text)
    if dates:
        data["dates_found"] = dates

    # long numbers
    nums = re.findall(r'\d{6,}', text)
    if nums:
        data["numbers_found"] = nums


    if doc_type == "Kuwait Vehicle Card":

        year = re.search(r'20\d{2}', text)
        if year:
            data["vehicle_year"] = year.group()

        expiry = re.search(r'20\d{2}-\d{2}-\d{2}', text)
        if expiry:
            data["expiry_date"] = expiry.group()

        eng_name = re.search(r'NAME[: ]+([A-Z ]+)', text)
        if eng_name:
            data["owner_name"] = eng_name.group(1).strip()


    elif doc_type == "Kuwait Civil ID":

        civil = re.search(r'\d{12}', text)
        if civil:
            data["civil_id_number"] = civil.group()

 
    elif doc_type == "Kuwait Passport":

        pass_num = re.search(r'[A-Z0-9]{6,9}', text)
        if pass_num:
            data["passport_number"] = pass_num.group()

    return data



@app.post("/api/v1/scan")
async def scan_document(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        # PDF
        if file.filename.lower().endswith(".pdf"):
            pages = convert_from_bytes(contents)
            image = pages[0]
        else:
            image = Image.open(BytesIO(contents)).convert("RGB")

        # save original
        request_id = str(uuid.uuid4())
        save_path = os.path.join(UPLOAD_DIR, f"{request_id}.jpg")
        image.save(save_path)

        # preprocess
        processed = preprocess_image(image)

        # OCR
        text, conf = extract_text(processed)

        # classify
        doc_type, cls_conf = classify_document(text)

        # fields
        fields = extract_fields(text, doc_type)

        return {
            "status": "success",
            "file_name": file.filename,
            "doc_type": doc_type,
            "classification_confidence": cls_conf,
            "ocr_confidence": conf,
            "raw_text": text,
            "fields": fields
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e)
            }
        )


# @app.post("/api/v1/scan-multiple")
# async def scan_multiple(files: list[UploadFile] = File(...)):
#     try:
#         all_docs = []

#         for file in files:
#             contents = await file.read()

#             if file.filename.lower().endswith(".pdf"):
#                 pages = convert_from_bytes(contents)
#                 image = pages[0]
#             else:
#                 image = Image.open(BytesIO(contents)).convert("RGB")

#             processed = preprocess_image(image)

#             text, conf = extract_text(processed)

#             doc_type, cls_conf = classify_document(text)

#             fields = extract_fields(text, doc_type)

#             all_docs.append({
#                 "file_name": file.filename,
#                 "doc_type": doc_type,
#                 "classification_confidence": cls_conf,
#                 "ocr_confidence": conf,
#                 "raw_text": text,
#                 "fields": fields
#             })

#         return {
#             "status": "success",
#             "documents": all_docs
#         }

#     except Exception as e:
#         return JSONResponse(
#             status_code=500,
#             content={
#                 "status": "error",
#                 "message": str(e)
#             }
#         )