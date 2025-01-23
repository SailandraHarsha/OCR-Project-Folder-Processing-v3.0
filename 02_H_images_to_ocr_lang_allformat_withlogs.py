import os
import easyocr
import time
import re  # For regex pattern matching

# Root directory path (e.g., '/mnt/OCR')
root_directory = '/mnt/OCR'

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

def extract_languages_from_filename(image_name):
    """
    Extract language codes from the image filename.
    Handles cases like 'en_name.png', 'en-hi_name.png', 'hi_name.png', and 'en_name_name.png'.
    """
    log_message(f"Extracting language codes from filename: {image_name}")
    
    base_name = os.path.splitext(image_name)[0]  # Remove extension (.png, .jpg, etc.)
    
    # Regex to match language codes before the first underscore
    match = re.match(r"([a-zA-Z]{2})(?:-([a-zA-Z]{2}))?", base_name)
    
    if match:
        # If two language codes are found separated by a hyphen (e.g., en-hi)
        if match.group(2):
            languages = [match.group(1), match.group(2)]
            #log_message(f"Languages extracted: {languages}")
        else:
            # If only one language code is found (e.g., en, hi)
            languages = [match.group(1)]
            #log_message(f"Single language extracted: {languages}")
    else:
        # Default to English ('en') if no language code is found
        languages = ['en']
        log_message(f"No language code found, defaulting to: {languages}")
    
    return languages

def perform_ocr_on_image(image_path):
    """
    Perform OCR on an image and save the extracted text to a file.
    """
    image_name = os.path.basename(image_path)
    
    log_message(f"Processing image: {image_name}")
    
    # Extract language codes from the image filename
    languages = extract_languages_from_filename(image_name)
    
    # Check if OCR text file already exists for the image
    text_filename = os.path.splitext(image_path)[0] + '.txt'
    
    if os.path.exists(text_filename):
        log_message(f"OCR text file already exists for {image_name}. Skipping...")
        return  # Skip OCR if text file already exists
    
    log_message(f"Performing OCR on image: {image_path}")
    
    try:
        # Initialize the easyocr Reader object with the appropriate language codes
        reader = easyocr.Reader(languages)  # Pass languages list dynamically
        #log_message(f"Initialized easyocr.Reader with languages: {languages}")
        
        # Perform OCR on the image
        result = reader.readtext(image_path)
        #log_message(f"OCR result obtained for {image_name}: {result}")
        
        # Extract text from OCR result
        ocr_text = "\n".join([text[1] for text in result])
        
        # Save the OCR result to a text file in the same location as the image
        with open(text_filename, 'w', encoding='utf-8') as f:
            f.write(ocr_text)
        
        log_message(f"OCR text successfully saved to: {text_filename}")
    
    except Exception as e:
        # If there's an error (e.g., corrupted image), create an error text file
        error_filename = os.path.splitext(image_path)[0] + '_error.txt'
        with open(error_filename, 'w', encoding='utf-8') as f:
            f.write(f"Error processing image: {image_name}\n")
            f.write(f"Error details: {str(e)}\n")
        
        log_message(f"Error processing image: {image_name}. Error details saved to: {error_filename}")

def ocr_images_in_directory(root_directory):
    """
    Traverse the given directory and apply OCR to all supported image files.
    """
    # Supported image formats for OCR
    supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif')
    
    #log_message(f"Scanning directory for images: {root_directory}")
    
    # Traverse all directories and subdirectories
    for dirpath, dirnames, filenames in os.walk(root_directory):
        #log_message(f"Scanning directory: {dirpath}")
        
        for filename in filenames:
            # Check if the file is a supported image format
            if filename.lower().endswith(supported_formats):
                image_path = os.path.join(dirpath, filename)
                log_message(f"Found supported image file: {image_path}")
                perform_ocr_on_image(image_path)
            else:
                log_message(f"Skipping unsupported file: {filename}")

def main():
    """
    Main function to start the OCR process.
    """
    log_message(f"Starting OCR process in directory: {root_directory}")
    
    ocr_images_in_directory(root_directory)
    
    log_message("OCR process completed.")

if __name__ == "__main__":
    main()

print("")
print('*' * 50)
print("Image OCR Process completed")
print('*' * 50)

