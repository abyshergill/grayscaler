# GrayScaler Image Converter & Watcher

## Introduction

This program is designed to automatically convert images to grayscale, effectively compressing them, and can continuously monitor a specified folder for new images to process. It also maintains detailed logs for each processing session.

### Why This Program Was Created

During my work, I encountered a situation where our machinery captures images every sec. Each color picture is around 2.5 MB. The critical issue is that while these images are captured in color (with 4 color channels according to metadata), their essential content is black and white in nature. This means only a single color channel is truly useful for our purposes.

To address this, I developed this program leveraging my Python knowledge and learnings from OpenCV. The goal is to convert these images to their essential grayscale form, significantly reducing file size without losing important visual information.

### Who Should Use This Program?

This program is beneficial for anyone who:

1.  Wants to convert batches of color images into grayscale (black & white).
2.  Needs to compress images by converting them to grayscale, which is particularly useful when the color information is redundant.
3.  Requires a tool to automatically process images as they appear in a specific folder.

## Key Features

* **Automatic Grayscale Conversion:** Converts images to 8-bit grayscale.
* **Folder Monitoring:** Continuously watches a designated folder for new image files.
* **Custom Output Location:** Allows users to specify where converted images are saved.
* **Original File Deletion:** Automatically deletes original color images after successful conversion to save space (use with caution).
* **Real-time GUI Log:** Displays ongoing activities and messages within the application window.
* **Session-Based File Logging:** Creates a unique, timestamped log file for each program run, stored in a dedicated `app_run_logs` folder.
* **User-Friendly Interface:** Built with CustomTkinter for a modern and easy-to-use experience.
* **Supported Image Formats:** Processes common image types like PNG, JPG, JPEG, GIF, and BMP.

## Without Python
Those people who want to use this program in `production with real time without installing the python can get binary/exe. can contact me`
  ```
  Email : shergillkuldeep@outlook.com
  ```


## With Python Requirements

* Python 3.7 or newer
* Libraries:
    * OpenCV (`opencv-python`)
    * CustomTkinter (`customtkinter`)

## Installation

1.  Ensure you have Python 3 installed on your system.
2.  Install the required libraries using pip:
    ```bash
    pip install opencv-python customtkinter
    ```

## How to Run

1.  Save the program code as a Python file (e.g., `image_processor_app.py`).
2.  Open a terminal or command prompt.
3.  Navigate to the directory where you saved the file.
4.  Run the script using:
    ```bash
    python main.py
    ```
    This will launch the graphical user interface.

## User Manual

The application provides a straightforward interface for image processing:

### 1. Monitor Folder

* **Purpose:** This is the input folder. The application will look for images here.
* **How to use:** Click the **Browse** button next to "Monitor Folder:" to navigate and select the directory containing the original color images you want to convert.

### 2. Save Grayscale To

* **Purpose:** This is the output folder where the converted grayscale images will be stored.
* **How to use:** Click the **Browse** button next to "Save Grayscale To:" to choose a destination folder.
* **Default Behavior:** If you leave this field empty, the program will automatically create and use a subfolder named `grayscale_output_default` inside the selected "Monitor Folder".

### 3. Start Watching

* **Purpose:** Initiates the image monitoring and conversion process.
* **Action:** Once clicked, the program will:
    1.  Begin scanning the "Monitor Folder" for new image files (checks approximately every 1 second).
    2.  Convert any detected images to grayscale.
    3.  Save the processed images to the "Save Grayscale To" folder.
    4.  **Important:** Delete the original color image from the "Monitor Folder" after successful conversion.

### 4. Stop Watching

* **Purpose:** Halts the active monitoring and conversion process.
* **Action:** Click this button to safely stop the application from looking for and processing new images.

### 5. Activity Log (In-App)

* **Location:** The text box at the bottom of the application window.
* **Purpose:** Displays real-time status messages, including detected images, conversion progress, successful operations, and any errors encountered. The GUI log display updates frequently (around every 0.5 seconds) with the latest messages.

### 6. Status Bar

* **Location:** At the very bottom of the window.
* **Purpose:** Shows the current overall status of the application, such as "Status: Idle", "Status: Watching 'folder_name'...", or "Status: Not Watching".

## Log Files

For detailed tracking and troubleshooting, the application generates comprehensive log files:

* **Location:** A folder named `app_run_logs` will be automatically created in the same directory where the application script is located. All log files are stored here.
* **Naming Convention:** Each time you run the application, a new log file is created with a unique timestamp in its name, following the format: `app_session_YYYY-MM-DD_HH-MM-SS.log` (e.g., `app_session_2025-05-16_23-50-12.log`). This ensures that logs from previous sessions are preserved.
* **Content:** These files record important events, including application start and stop times, folders being watched, images processed, and any errors, all with precise timestamps.

## Important Notes

* **⚠️ Original File Deletion:** This program is designed to **delete the original color images** from the "Monitor Folder" after they are successfully converted and saved. Please ensure you have backups of your original images if they are important, or test the program with copies of images first.
* **Monitoring Interval:** The application actively scans the "Monitor Folder" for new images approximately every **1 second** when the "Start Watching" mode is active.
