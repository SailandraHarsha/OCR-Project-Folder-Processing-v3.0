# Setup Instructions

Follow these steps to set up and run the OCR process and enable automatic execution via cron, along with UI interaction:

# 1. Download All Models
   - First, use the script `001_GetAllModels.py` to download all the required models. This script will automatically fetch and store the necessary model files.

   Command:
   ```bash
   python 001_GetAllModels.py
   ```

# 2. Mount the OCR Folder
   - On your server or local machine, you need to mount the OCR folder from a remote server or PC. This will allow access to the OCR data needed by the scripts.
   - Mount the OCR folder under the path `/mnt/OCR`.

   Example (if you're using Linux and SSHFS):
   ```bash
   sshfs user@remote-server:/path/to/OCR /mnt/OCR
   ```

   Ensure the folder is mounted correctly by verifying that you can access the OCR files in the `/mnt/OCR` directory.

# 3. Update IP Addresses in Configuration Files
   - Update the IP addresses and/or server paths in the following files to match your environment and network configuration:
   
   - Files to update:
     - `Run_If_Not_Running_OCR_withlogs.py`
     - `02_H_images_to_ocr_lang_allformat_withlogs.py`
     - `00_H_pdf_to_images_withlogs.py`
     - `main.py`
     - `UI/index.html`
     
   - In each of these files, look for the sections where the server's IP address or path to OCR resources is defined, and replace it with the correct values for your setup.

   Example:
   - Open `Run_If_Not_Running_OCR_withlogs.py` and update the IP address:
     ```python
     SERVER_IP = '192.168.1.100'  # Change this to your server's IP address
     ```

# 4. Configure Cron Jobs for Automatic OCR
   - To have the OCR process run automatically at specified intervals, follow the instructions in `setup_cron.txt` to update the `crontab` and `visudo` files.

   - Steps:
     1. Open `setup_cron.txt` for detailed instructions.
     2. Add the appropriate cron jobs to your `crontab` file to schedule the OCR scripts.
     3. Make any necessary adjustments to the `visudo` file to grant the required permissions.

   Example Cron Job (to run every hour):
   ```bash
   0 * * * * python /path/to/your/script/02_H_images_to_ocr_lang_allformat_withlogs.py >> /path/to/logs/ocr_log.txt 2>&1
   ```

   After these changes, the OCR will run automatically as per the scheduled cron jobs.

# 5. Expose UI for User Interaction
   - You can interact with the OCR UI through an exposed server. To run a simple HTTP server and access the UI, follow these steps:

   - Navigate to the `UI` folder:
     ```bash
     cd /path/to/your/project/UI
     ```

   - Start a Python HTTP server to expose the UI on port 8000:
     ```bash
     python3 -m http.server 8000
     ```

   - You can now access the UI through your browser by going to `http://<your-server-ip>:8000`.

# 6. Make Changes in `main.py` and `index.html`
   - Ensure the following updates are made for the UI to work correctly and for the main Python script to communicate with it:

   - In `main.py`:
     - Update the `SERVER_IP` variable and any paths that need to point to the correct locations for your environment.

     Example:
     ```python
     SERVER_IP = 'http://localhost:8000'  # Update to the server's IP if running remotely
     ```

   - In `index.html`:
     - Update the URL or IP addresses where needed, so the UI interacts properly with the backend services.

     Example:
     ```html
     <script>
       var apiEndpoint = 'http://localhost:5000/api/ocr';  // Update this as needed
     </script>
     ```

# 7. Run the OCR Process
   - After completing the previous steps, you can manually trigger the OCR process by running the script:

   Example:
   ```bash
   python 02_H_images_to_ocr_lang_allformat_withlogs.py
   ```

   Or, if the cron jobs are set, it will run automatically according to the schedule you defined.

---

# Notes:
- Ensure that you have all necessary dependencies installed. If not, you may need to install them via `pip` or another package manager.
- The OCR folder from the remote server must remain accessible throughout the process to ensure that the scripts can read the data.
- The cron jobs will execute automatically, but you can also manually trigger the scripts as needed.
- Be sure to check the log files after running the scripts (either manually or via cron) to confirm that the OCR process completed successfully.

Let me know if you need further clarifications or additions to the guide!

---

This version should provide all the necessary steps for setting up the OCR process, making changes to `main.py` and `index.html`, configuring cron jobs, and using the UI. Let me know if anything else is needed!
