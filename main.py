#gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:5006 --timeout 120 main:app --reload
#sudo lsof -t -i tcp:5006 | xargs kill -9

from fastapi import FastAPI, File, UploadFile
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import time, os
import easyocr
from pdf2image import convert_from_path
from typing import Optional
from pydantic import BaseModel
from fastapi.responses import FileResponse

app = FastAPI()
readerEN = easyocr.Reader(['en'], gpu=False, model_storage_directory="SailModels")
readerHI = easyocr.Reader(['hi'], gpu=False, model_storage_directory="SailModels")
readerENHI = easyocr.Reader(['en', 'hi'], gpu=False, model_storage_directory="SailModels")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root folder for storing OCR files
ROOT_FOLDER = './ForOCR/'

# Helper function to generate file names
def generate_filename(uid: str, lang: str, file_ext: str) -> str:
    timestamp = time.strftime('%d-%m-%Y_%H-%M-%S')
    return f"{uid}_{lang}_{timestamp}{file_ext}"

# Helper function to log messages
def log_message(message: str):
    # Get the current script's directory
    script_directory = os.path.dirname(os.path.abspath(__file__))
    
    # Create 'daily_logs' directory if it doesn't exist
    log_folder = os.path.join(script_directory, 'daily_live_logs')
    os.makedirs(log_folder, exist_ok=True)
    
    # Log filename based on the current date
    log_filename = os.path.join(log_folder, f"process_{time.strftime('%d-%m-%Y')}.log")
    
    # Print message to the console
    print(message)
    
    # Write message to the log file
    with open(log_filename, "a") as log_file:
        log_file.write(f"{time.strftime('%H:%M:%S')} - {message}\n")

# Helper function to process OCR for images
def process_ocr_for_image(image_path: str, lang: str) -> list:
    if lang == 'en':
        result = readerEN.readtext(image_path, detail=0, paragraph=True, min_size=2, height_ths=1)
    elif lang == 'hi':
        result = readerHI.readtext(image_path, detail=0, paragraph=True, min_size=2, height_ths=1)
    elif lang == 'en,hi' or lang == 'hi,en':
        result = readerENHI.readtext(image_path, detail=0, paragraph=True, min_size=2, height_ths=1)
    else:
        result = readerEN.readtext(image_path, detail=0, paragraph=True, min_size=2, height_ths=1)
    return result

# Helper function to process OCR for PDF
def process_ocr_for_pdf(pdf_path: str, lang: str, output_dir: str) -> list:
    log_message(f"Converting PDF to images: {pdf_path}")
    images = convert_from_path(pdf_path, 300)
    first_page_ocr = []
    for i, image in enumerate(images):
        img_filename = os.path.join(output_dir, f"{os.path.basename(pdf_path).split('.')[0]}_{i+1}.png")
        image.save(img_filename)
        log_message(f"Processing page {i+1} for OCR: {img_filename}")
        ocr_result = process_ocr_for_image(img_filename, lang)
        
        text_filename = img_filename.replace(".png", ".txt")
        with open(text_filename, "w") as text_file:
            text_file.write("\n".join(ocr_result))  # Writing OCR text as is with each line separated by newline
        log_message(f"OCR text saved to: {text_filename}")

        if i == 0:  # Returning first page OCR
            first_page_ocr = ocr_result
    
    return first_page_ocr

@app.post("/GetOCR/")
async def get_ocr(file: UploadFile = File(...), Lang: str = File(...), UID: str = File(...)):
    log_message(f"Received request for OCR: UID={UID}, Lang={Lang}, File={file.filename}")

    file_ext = os.path.splitext(file.filename)[-1].lower()
    filename = generate_filename(UID, Lang, file_ext)
    file_path = os.path.join(ROOT_FOLDER, filename)

    # Ensure ROOT_FOLDER exists
    if not os.path.exists(ROOT_FOLDER):
        os.makedirs(ROOT_FOLDER)

    # Save the uploaded image file
    with open(file_path, "wb+") as file_object:
        file_object.write(file.file.read())
    log_message(f"File saved as: {file_path}")

    text_filename = file_path.replace(file_ext, ".txt")
    
    # If text file already exists, skip OCR process and return the content
    if os.path.exists(text_filename):
        log_message(f"OCR text file already exists: {text_filename}")
        with open(text_filename, "r") as text_file:
            ocr_text = text_file.read()
        return {"OCR_Content": ocr_text, "FileName":filename}

    if file_ext in ['.png', '.jpg', '.jpeg']:
        # If it's an image
        ocr_text = process_ocr_for_image(file_path, Lang)
        with open(text_filename, "w") as text_file:
            text_file.write("\n".join(ocr_text))  # Writing OCR text in array format (each string on a new line)
        log_message(f"OCR text saved to: {text_filename}")

        return {"OCR_Content": ocr_text, "FileName":filename}
    
    elif file_ext == '.pdf':
        # If it's a PDF
        output_dir = os.path.join(ROOT_FOLDER, filename.replace(".pdf", ""))
        os.makedirs(output_dir, exist_ok=True)
        log_message(f"PDF images saved in folder: {output_dir}")
        first_page_ocr = process_ocr_for_pdf(file_path, Lang, output_dir)
        
        return {"OCR_Content": first_page_ocr, "FileName":filename}

    else:
        return {"error": "Unsupported file type"}

@app.post("/GetOCRMP/")
async def get_ocr_mp(file: UploadFile = File(...), Lang: str = File(...), UID: str = File(...)):
    log_message(f"Received request for OCR: UID={UID}, Lang={Lang}, File={file.filename}")

    file_ext = os.path.splitext(file.filename)[-1].lower()
    filename = generate_filename(UID, Lang, file_ext)
    file_path = os.path.join(ROOT_FOLDER, filename)

    # Ensure ROOT_FOLDER exists
    if not os.path.exists(ROOT_FOLDER):
        os.makedirs(ROOT_FOLDER)

    # Save the uploaded image file
    with open(file_path, "wb+") as file_object:
        file_object.write(file.file.read())
    log_message(f"File saved as: {file_path}")

    text_filename = file_path.replace(file_ext, ".txt")
    
    # If text file already exists, skip OCR process and return the content
    if os.path.exists(text_filename):
        log_message(f"OCR text file already exists: {text_filename}")
        with open(text_filename, "r") as text_file:
            ocr_text = text_file.read()
        return {"OCR_Content": ocr_text, "FileName":filename}

    if file_ext in ['.png', '.jpg', '.jpeg']:
        # If it's an image
        ocr_text = process_ocr_for_image(file_path, Lang)
        with open(text_filename, "w") as text_file:
            text_file.write("\n".join(ocr_text))  # Writing OCR text in array format (each string on a new line)
        log_message(f"OCR text saved to: {text_filename}")

        return {"OCR_Content": ocr_text, "FileName":filename}
    
    elif file_ext == '.pdf':
        # If it's a PDF
        output_dir = os.path.join(ROOT_FOLDER, filename.replace(".pdf", ""))
        os.makedirs(output_dir, exist_ok=True)
        log_message(f"PDF images saved in folder: {output_dir}")
        first_page_ocr = process_ocr_for_pdf(file_path, Lang, output_dir)
        
        return {"OCR_Content": first_page_ocr, "FileName":filename}

    else:
        return {"error": "Unsupported file type"}


#Receive request and read text file and return to call

# Helper function to check if file exists
def file_exists(file_path: str) -> bool:
    return os.path.exists(file_path)

class SailData(BaseModel):
    filename: str
    count: int

# Single function to handle OCR text retrieval
@app.post("/getNPOCRText/")
async def getNPOCRText(data: SailData):
    filename = data.filename
    count = data.count
    log_message(f"Received Request for get ocr text for {filename}")
    print(f"Received Request for get ocr text for {filename}")

    # Check file extension to determine if it's an image or PDF
    file_ext = os.path.splitext(filename)[-1].lower()

    # Logic for Image files
    if file_ext in ['.png', '.jpg', '.jpeg', '.gif']:
        text_filename = os.path.join(ROOT_FOLDER, f"{os.path.splitext(filename)[0]}.txt")
        if file_exists(text_filename):
            with open(text_filename, "r") as text_file:
                ocr_text = text_file.read()
            log_message(f"Retured text for {os.path.splitext(filename)[0]}.txt")
            return {"OCR_Content": ocr_text, "FileName":filename}
        else:
            raise HTTPException(status_code=404, detail="OCR text file not found for the image.")

    # Logic for PDF files
    elif file_ext == '.pdf':
        folder_path = os.path.join(ROOT_FOLDER, os.path.splitext(filename)[0])  # Folder named after the PDF file
        text_filename = os.path.join(folder_path, f"{os.path.splitext(filename)[0]}_{count}.txt")
        if file_exists(text_filename):
            with open(text_filename, "r") as text_file:
                ocr_text = text_file.read()
            log_message(f"Retured text for {text_filename}")
            return {"OCR_Content": ocr_text, "FileName":filename}
        else:
            raise HTTPException(status_code=404, detail=f"OCR text file not found for PDF page {count}.")
    
    # Invalid file type (not an image or PDF)
    else:
        raise HTTPException(status_code=400, detail="Invalid file type. Only images and PDFs are supported.")


class SailDataDown(BaseModel):
    filename: str
    count: int
    downfor: int  # 0 for current page, 1 for all pages

def file_exists(file_path: str) -> bool:
    return os.path.isfile(file_path)


@app.post("/downloadOCRText/")
async def download_ocr_text(data: SailDataDown):
    filename = data.filename
    count = data.count
    downfor = data.downfor
    file_ext = os.path.splitext(filename)[-1].lower()

    if file_ext in ['.png', '.jpg', '.jpeg', '.gif']:  # Image files
        text_filename = os.path.join(ROOT_FOLDER, f"{os.path.splitext(filename)[0]}.txt")
        if file_exists(text_filename):
            with open(text_filename, "r") as text_file:
                ocr_text = text_file.read()
            return {"OCR_Content": ocr_text, "FileName": text_filename}
        else:
            raise HTTPException(status_code=404, detail="OCR text file not found for the image.")
    
    elif file_ext == '.pdf':  # PDF files
        folder_path = os.path.join(ROOT_FOLDER, os.path.splitext(filename)[0])
        all_ocr_text = ""

        if downfor == 1:  # Return OCR text for all pages
            page_num = 1
            while True:
                text_filename = os.path.join(folder_path, f"{os.path.splitext(filename)[0]}_{page_num}.txt")
                if not file_exists(text_filename):
                    break
                with open(text_filename, "r") as text_file:
                    all_ocr_text += text_file.read() + "\n"
                page_num += 1

            if all_ocr_text:
                return {"OCR_Content": all_ocr_text, "FileName": f"{os.path.splitext(filename)[0]}_All.txt"}
            else:
                raise HTTPException(status_code=404, detail="No OCR text found for the PDF.")
        
        else:  # Return OCR text for a specific page
            text_filename = os.path.join(folder_path, f"{os.path.splitext(filename)[0]}_{count}.txt")
            if file_exists(text_filename):
                with open(text_filename, "r") as text_file:
                    ocr_text = text_file.read()
                return {"OCR_Content": ocr_text, "FileName": f"{os.path.splitext(filename)[0]}_{count}.txt"}
            else:
                raise HTTPException(status_code=404, detail=f"OCR text file not found for PDF page {count}.")
    
    else:
        raise HTTPException(status_code=400, detail="Invalid file type. Only images and PDFs are supported.")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5006, log_level="debug")

