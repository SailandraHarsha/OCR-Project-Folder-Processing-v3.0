import os
import time
import fitz  # PyMuPDF
from PIL import Image

# Helper function to log messages
def log_message(message: str):
    # Get the current script's directory
    script_directory = os.path.dirname(os.path.abspath(__file__))
    
    # Create 'daily_logs' directory if it doesn't exist
    log_folder = os.path.join(script_directory, 'daily_logs')
    os.makedirs(log_folder, exist_ok=True)
    
    # Log filename based on the current date
    log_filename = os.path.join(log_folder, f"process_{time.strftime('%d-%m-%Y')}.log")
    
    # Print message to the console
    print(message)
    
    # Write message to the log file
    with open(log_filename, "a") as log_file:
        log_file.write(f"{time.strftime('%H:%M:%S')} - {message}\n")

# Root directory path (e.g., '.' for current directory, or specify a path)
root_directory = '/mnt/OCR'

def convert_pdf_to_images(pdf_path):
    # Get the PDF filename without the extension
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    #log_message(f"Started processing PDF: {pdf_name}")
    
    # Create a folder to save the images in the same location as the PDF
    output_folder = os.path.join(os.path.dirname(pdf_path), pdf_name)
    
    # Check if the output folder already exists
    if os.path.exists(output_folder):
        #log_message(f"Output folder already exists: {output_folder}")
        
        # Check if all pages have already been converted
        existing_images = sorted([f for f in os.listdir(output_folder) if f.endswith('.png')])
        pdf_document = fitz.open(pdf_path)
        total_pages = pdf_document.page_count
        if len(existing_images) == total_pages:
            #log_message(f"Skipping {pdf_name}. All {total_pages} pages are already converted.")
            pdf_document.close()
            return
        pdf_document.close()
    
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    log_message(f"Opened PDF: {pdf_name}, Total pages: {pdf_document.page_count}")
    
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, mode=0o777, exist_ok=True)
    #log_message(f"Created output folder: {output_folder}")
    
    # Convert each page of the PDF to an image
    for page_num in range(pdf_document.page_count):
        image_filename = f"{pdf_name}-{page_num + 1:02d}.png"
        image_path = os.path.join(output_folder, image_filename)
        
        if not os.path.exists(image_path):
            #log_message(f"Converting page {page_num + 1} to image: {image_filename}")
            
            # Get the page
            page = pdf_document.load_page(page_num)
            
            # Convert the page to a pixmap (image)
            pix = page.get_pixmap()
            
            # Convert the pixmap to an image (PIL format)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Save the image as PNG
            img.save(image_path)
            #log_message(f"Saved {image_filename} at {output_folder}")
        else:
            #log_message(f"{image_filename} already exists, skipping.")

    # Close the PDF document
    pdf_document.close()
    log_message(f"Finished processing PDF: {pdf_name}")

def convert_pdfs_in_directory(root_directory):
    log_message(f"Started scanning directory: {root_directory}")
    
    # Walk through all directories and subdirectories
    for dirpath, dirnames, filenames in os.walk(root_directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            
            # Check if the file is a PDF
            if filename.lower().endswith('.pdf'):
                #log_message(f"Found PDF: {file_path}")
                convert_pdf_to_images(file_path)

if __name__ == "__main__":
    log_message("Starting PDF to Image conversion process...")
    convert_pdfs_in_directory(root_directory)

log_message("*" * 50)
log_message("Calling Image OCR Process")
log_message("*" * 50)
    
# Trigger OCR process (replace with actual path for your environment)
os.system('sudo python3 /home/sailocr/02_H_images_to_ocr_lang_allformat_withlogs.py')
log_message("OCR Process completed.")

