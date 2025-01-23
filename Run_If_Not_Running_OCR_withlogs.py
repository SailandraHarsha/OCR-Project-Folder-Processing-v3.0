import subprocess
import os
import time

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


# Check if the first script (00_H_pdf_to_images.py) is running
p1 = subprocess.Popen(['pgrep', '-f', '00_H_pdf_to_images_withlogs.py'], stdout=subprocess.PIPE)
out01, err1 = p1.communicate()
p1.kill()

# Check if the second script (02_H_images_to_ocr_lang_allformat.py) is running
p2 = subprocess.Popen(['pgrep', '-f', '02_H_images_to_ocr_lang_allformat_withlogs.py'], stdout=subprocess.PIPE)
out02, err2 = p2.communicate()
p2.kill()

# Log the output of the pgrep command
log_message(f"Output from pgrep for 00_H_pdf_to_images_withlogs.py: {out01.decode().strip()}")
log_message(f"Output from pgrep for 02_H_images_to_ocr_lang_allformat_withlogs.py: {out02.decode().strip()}")

# Print outputs for reference
print(out01)
print(out02)

# If neither script is running, start the first script
if len(out01.strip()) == 0 and len(out02.strip()) == 0:
    log_message("Neither script is running. Starting 00_H_pdf_to_images_withlogs.py...")
    os.system('sudo python3 /home/sailocr/Sudarshan/00_H_pdf_to_images_withlogs.py')
    log_message("Started 00_H_pdf_to_images_withlogs.py.")
else:
    # If the first script is running, log it
    if len(out01.strip()) > 0:
        log_message("01 script (00_H_pdf_to_images_withlogs.py) is already running.")
        print("01 script already running")
    
    # If the second script is running, log it
    if len(out02.strip()) > 0:
        log_message("02 script (02_H_images_to_ocr_lang_allformat_withlogs.py) is already running.")
        print("02 script already running")

