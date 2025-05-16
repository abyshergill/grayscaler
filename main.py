import cv2
import os
import time
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox # Added messagebox
from collections import deque
import logging
import datetime

class ImageProcessor:
    """
    Handles image processing tasks using OpenCV.
    """
    def __init__(self, output_folder="grayscale"):
        """
        Initializes the ImageProcessor with an output folder for grayscale images.

        Args:
            output_folder (str): The path to the folder to save grayscale images.
        """
        self.output_folder = output_folder
        # No need to check for os.path.exists here, will be done before processing
        # if not os.path.exists(self.output_folder):
        #     try:
        #         os.makedirs(self.output_folder)
        #         logging.info(f"Created output folder: {self.output_folder}")
        #     except OSError as e:
        #         logging.error(f"Could not create output folder {self.output_folder}: {e}")
        #         # Propagate the error or handle it, e.g., by setting a flag
        #         raise # Or handle differently
        logging.info(f"ImageProcessor initialized. Output folder set to: {self.output_folder}")

    def _ensure_output_folder_exists(self):
        """Ensures the output folder exists, creating it if necessary."""
        if not os.path.exists(self.output_folder):
            try:
                os.makedirs(self.output_folder)
                logging.info(f"Created output folder: {self.output_folder}")
                return True
            except OSError as e:
                logging.error(f"Could not create output folder {self.output_folder}: {e}")
                # Potentially show a message to the user via the main app's log
                return False
        return True


    def convert_to_grayscale(self, image_path, filename):
        """
        Converts an image to grayscale and saves it to the output folder.

        Args:
            image_path (str): Path to the input image.
            filename (str): Name of the image file.

        Returns:
            str: Path to the saved grayscale image, or None on failure.
        """
        if not self._ensure_output_folder_exists():
            # Log this specific failure within the app's UI log if possible
            # For now, relying on standard logging
            return None
        try:
            img = cv2.imread(image_path)
            if img is None:
                logging.error(f"Could not read image: {image_path}")
                return None

            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Ensure filename doesn't have path components if it's just a name
            base_filename = os.path.basename(filename)
            output_path = os.path.join(self.output_folder, base_filename)

            cv2.imwrite(output_path, gray_img)
            logging.info(f"Converted to grayscale: {base_filename}, saved to {output_path}")
            return output_path
        except Exception as e:
            logging.error(f"Error converting {image_path} to grayscale: {e}")
            return None

    def delete_original(self, image_path):
        """
        Deletes the original image file.

        Args:
            image_path (str): Path to the image to delete.
        """
        try:
            os.remove(image_path)
            logging.info(f"Deleted original image: {image_path}")
        except Exception as e:
            logging.error(f"Error deleting {image_path}: {e}")

class FileWatcher:
    """
    Monitors a folder for new image files and processes them.
    """
    def __init__(self, folder_path, image_processor, log_queue_callback, update_interval=1):
        """
        Initializes the FileWatcher.

        Args:
            folder_path (str): Path to the folder to monitor.
            image_processor (ImageProcessor): Instance of ImageProcessor to handle image processing.
            log_queue_callback (function): Callback function to add messages to the app's log queue.
            update_interval (int): How often to check for new files, in seconds.  Defaults to 1.
        """
        self.folder_path = folder_path
        self.image_processor = image_processor
        self.log_queue_callback = log_queue_callback # Use callback for logging to app
        self.update_interval = update_interval
        self.stop_flag = threading.Event()
        self.processed_files = set()

    def watch(self):
        """
        Starts monitoring the folder for new image files.
        """
        self.log_message_to_app(f"Watching folder: {self.folder_path}")
        while not self.stop_flag.is_set():
            try:
                # Check if folder still exists
                if not os.path.exists(self.folder_path):
                    self.log_message_to_app(f"Error: Monitored folder {self.folder_path} no longer exists. Stopping watch.")
                    logging.error(f"Monitored folder {self.folder_path} no longer exists.")
                    break # Exit the loop

                files = [f for f in os.listdir(self.folder_path)
                           if os.path.isfile(os.path.join(self.folder_path, f)) and
                              f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
                for filename in files:
                    if self.stop_flag.is_set(): break # Check stop flag frequently
                    image_path = os.path.join(self.folder_path, filename)
                    # Check if file still exists before processing (it might be moved/deleted quickly)
                    if not os.path.exists(image_path):
                        self.processed_files.discard(filename) # Remove if it was somehow added then disappeared
                        continue

                    if filename not in self.processed_files:
                        self.log_message_to_app(f"New image detected: {filename}")
                        gray_path = self.image_processor.convert_to_grayscale(image_path, filename)
                        if gray_path:
                            self.image_processor.delete_original(image_path)
                            self.log_message_to_app(f"Processed and original deleted: {filename}")
                        else:
                            self.log_message_to_app(f"Failed to process: {filename}")
                        self.processed_files.add(filename)
                if self.stop_flag.is_set(): break
                time.sleep(self.update_interval)
            except FileNotFoundError:
                 self.log_message_to_app(f"Error: Monitored folder {self.folder_path} not found. Stopping watch.")
                 logging.error(f"Monitored folder {self.folder_path} not found during watch.")
                 break # Exit the loop
            except Exception as e:
                logging.error(f"Error watching folder {self.folder_path}: {e}")
                self.log_message_to_app(f"Error in watcher: {e}")
                time.sleep(self.update_interval * 2) # Sleep longer on generic error

        self.log_message_to_app("File watcher stopped.")


    def log_message_to_app(self, message):
        """
        Uses the callback to add a message to the main application's log queue.
        """
        self.log_queue_callback(message) # The callback will handle timestamping

    def stop(self):
        """
        Sets the stop flag, signaling the watching thread to exit.
        """
        self.stop_flag.set()
        logging.info("Stopping file watcher signaled.")


class ImageProcessingApp(object):
    """
    Main application class for the image processing and file watching GUI.
    """
    def __init__(self, root_window):
        """
        Initializes the main application window.
        """
        self.root = root_window
        self.root.title("Pro Image Watcher & Converter")
        self.root.geometry("750x550")
        self.root.minsize(700, 500)

        logging.basicConfig(filename="image_processor_app.log", level=logging.INFO,
                            format="%(asctime)s - %(levelname)s - %(message)s")
        self.log_queue = deque(maxlen=200)

        self.watcher_thread = None
        self.is_watching = False
        self.image_processor = None
        self.watcher = None

        # --- Button Styling ---
        self.button_corner_radius = 8
        self.button_fg_color = ("#5DADE2", "#2E86C1")  # (light_mode, dark_mode)
        self.button_hover_color = ("#85C1E9", "#3498DB")
        self.button_text_color = ("#FFFFFF", "#FFFFFF")
        self.button_border_width = 0
        self.button_border_spacing = 5

        self.create_widgets()
        self.update_log_display_periodically() # Start log display updates

    def create_widgets(self):
        """
        Creates the UI elements.
        """
        self.root.grid_columnconfigure(1, weight=1) # Allow entry fields to expand

        # --- Input Folder Selection ---
        self.input_folder_label = ctk.CTkLabel(self.root, text="Monitor Folder:")
        self.input_folder_label.grid(row=0, column=0, padx=(20, 5), pady=10, sticky="w")

        self.input_folder_entry = ctk.CTkEntry(self.root, placeholder_text="Path to folder with original images")
        self.input_folder_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        self.browse_input_button = ctk.CTkButton(
            self.root, text="Browse", command=self.select_input_folder,
            corner_radius=self.button_corner_radius, fg_color=self.button_fg_color,
            hover_color=self.button_hover_color, text_color=self.button_text_color,
            border_width=self.button_border_width, width=100
        )
        self.browse_input_button.grid(row=0, column=2, padx=(5, 20), pady=10, sticky="e")

        # --- Output Folder Selection ---
        self.output_folder_label = ctk.CTkLabel(self.root, text="Save Grayscale To:")
        self.output_folder_label.grid(row=1, column=0, padx=(20, 5), pady=10, sticky="w")

        self.output_folder_entry = ctk.CTkEntry(self.root, placeholder_text="Path for processed images (optional, defaults to subfolder)")
        self.output_folder_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

        self.browse_output_button = ctk.CTkButton(
            self.root, text="Browse", command=self.select_output_folder,
            corner_radius=self.button_corner_radius, fg_color=self.button_fg_color,
            hover_color=self.button_hover_color, text_color=self.button_text_color,
             border_width=self.button_border_width, width=100
        )
        self.browse_output_button.grid(row=1, column=2, padx=(5, 20), pady=10, sticky="e")


        # --- Control Buttons ---
        controls_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        controls_frame.grid(row=2, column=0, columnspan=3, pady=10, padx=20, sticky="ew")
        controls_frame.grid_columnconfigure((0,1), weight=1) # Distribute space

        self.start_button = ctk.CTkButton(
            controls_frame, text="Start Watching", command=self.start_watching,
            corner_radius=self.button_corner_radius, fg_color=("green", "darkgreen"), # Specific color for start
            hover_color=("#A9DFBF", "#58D68D"), text_color=self.button_text_color,
            height=35, font=("Arial", 13, "bold")
        )
        self.start_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.stop_button = ctk.CTkButton(
            controls_frame, text="Stop Watching", command=self.stop_watching, state="disabled",
            corner_radius=self.button_corner_radius, fg_color=("red", "darkred"), # Specific color for stop
            hover_color=("#F5B7B1", "#EC7063"), text_color=self.button_text_color,
            height=35, font=("Arial", 13, "bold")
        )
        self.stop_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")


        # --- Log Display ---
        self.log_label = ctk.CTkLabel(self.root, text="Activity Log:")
        self.log_label.grid(row=3, column=0, padx=20, pady=(10,0), sticky="w")

        self.log_text = ctk.CTkTextbox(self.root, state="disabled", height=150, wrap="word")
        self.log_text.grid(row=4, column=0, columnspan=3, padx=20, pady=(0,10), sticky="nsew")
        self.root.grid_rowconfigure(4, weight=1) # Make log expandable

        # --- Status Label ---
        self.status_label = ctk.CTkLabel(self.root, text="Status: Idle", text_color="gray", font=("Arial", 12, "italic"))
        self.status_label.grid(row=5, column=0, columnspan=3, padx=20, pady=(5,10), sticky="w")

        # --- Status Label ---
        self.Creator_label = ctk.CTkLabel(self.root, text="Creator : Aby | Contact information kuldeepsinah@calcomp.co.th", text_color="gray", font=("Arial", 12, "bold"))
        self.Creator_label.grid(row=6, column=0, columnspan=3, padx=20, pady=(5,10), sticky="w")


    def select_input_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder to Monitor")
        if folder_path:
            self.input_folder_entry.delete(0, ctk.END)
            self.input_folder_entry.insert(0, folder_path)
            self.add_log_message(f"Input folder selected: {folder_path}")

    def select_output_folder(self):
        folder_path = filedialog.askdirectory(title="Select Output Folder for Grayscale Images")
        if folder_path:
            self.output_folder_entry.delete(0, ctk.END)
            self.output_folder_entry.insert(0, folder_path)
            self.add_log_message(f"Output folder selected: {folder_path}")


    def start_watching(self):
        input_folder_path = self.input_folder_entry.get().strip()
        output_folder_path = self.output_folder_entry.get().strip()

        if not input_folder_path:
            messagebox.showerror("Input Error", "Please select or enter an input folder path to monitor.")
            self.add_log_message("Error: Input folder path is empty.")
            return
        if not os.path.exists(input_folder_path) or not os.path.isdir(input_folder_path):
            messagebox.showerror("Input Error", f"The input folder path does not exist or is not a directory:\n{input_folder_path}")
            self.add_log_message(f"Error: Invalid input folder path: {input_folder_path}")
            return

        if not output_folder_path:
            output_folder_path = os.path.join(input_folder_path, "grayscale_output_default")
            self.add_log_message(f"Output folder not specified. Defaulting to: {output_folder_path}")
            self.output_folder_entry.delete(0, ctk.END) # Show default in entry
            self.output_folder_entry.insert(0, output_folder_path)

        # Try to create output folder if it doesn't exist to catch issues early
        if not os.path.exists(output_folder_path):
            try:
                os.makedirs(output_folder_path)
                self.add_log_message(f"Created output folder: {output_folder_path}")
            except OSError as e:
                messagebox.showerror("Output Error", f"Could not create output folder:\n{output_folder_path}\nError: {e}")
                self.add_log_message(f"Error: Failed to create output folder {output_folder_path}: {e}")
                return
        elif not os.path.isdir(output_folder_path):
             messagebox.showerror("Output Error", f"The specified output path exists but is not a directory:\n{output_folder_path}")
             self.add_log_message(f"Error: Output path is not a directory: {output_folder_path}")
             return


        if self.is_watching:
            self.add_log_message("Already watching. Please stop the current session first.")
            return

        self.image_processor = ImageProcessor(output_folder=output_folder_path)
        self.watcher = FileWatcher(input_folder_path, self.image_processor, self.add_log_message) # Pass callback

        self.watcher_thread = threading.Thread(target=self.watcher.watch, daemon=True)
        self.watcher_thread.start()

        self.is_watching = True
        self.update_ui_for_watch_state(True, input_folder_path)
        self.add_log_message(f"Started watching '{os.path.basename(input_folder_path)}'. Output to '{os.path.basename(output_folder_path)}'.")


    def stop_watching(self):
        if self.is_watching and self.watcher:
            self.add_log_message("Stopping file watcher...")
            self.watcher.stop()
            if self.watcher_thread and self.watcher_thread.is_alive():
                self.watcher_thread.join(timeout=5)
                if self.watcher_thread.is_alive():
                    self.add_log_message("Warning: Watcher thread did not terminate gracefully.")
                    logging.warning("Watcher thread did not terminate in time.")

            self.is_watching = False
            self.update_ui_for_watch_state(False)
            self.add_log_message("Stopped watching folder.")
        else:
            self.add_log_message("Not currently watching or watcher not initialized.")


    def update_ui_for_watch_state(self, watching, folder_name=""):
        if watching:
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.browse_input_button.configure(state="disabled")
            self.input_folder_entry.configure(state="disabled")
            self.browse_output_button.configure(state="disabled")
            self.output_folder_entry.configure(state="disabled")
            self.status_label.configure(text=f"Status: Watching '{os.path.basename(folder_name)}'...", text_color="green")
        else:
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.browse_input_button.configure(state="normal")
            self.input_folder_entry.configure(state="normal")
            self.browse_output_button.configure(state="normal")
            self.output_folder_entry.configure(state="normal")
            self.status_label.configure(text="Status: Idle", text_color="gray")

    def add_log_message(self, message):
        """
        Adds a message to the log queue for display and logs it to file.
        This method is thread-safe for appending to deque and logging.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {message}"
        self.log_queue.append(log_entry)
        logging.info(message)
        # UI update for log_text is handled by update_log_display_periodically

    def update_log_display_periodically(self):
        """
        Periodically updates the log display with new entries.
        Runs in the main Tkinter thread.
        """
        self.log_text.configure(state="normal")
        # Efficiently add new messages instead of clearing and re-adding all
        # For simplicity, this version still clears and re-adds.
        # For very high log volume, consider only adding new lines.
        current_log_content = self.log_text.get("1.0", ctk.END).strip()
        new_log_entries = "\n".join(list(self.log_queue))

        if current_log_content != new_log_entries: # Update only if changed
            self.log_text.delete("1.0", ctk.END)
            for log_entry in self.log_queue: # Iterate over a copy
                self.log_text.insert(ctk.END, log_entry + "\n")
            self.log_text.see(ctk.END) # Scroll to the end
        self.log_text.configure(state="disabled")

        self.root.after(500, self.update_log_display_periodically) # Update every 0.5 seconds


    def on_closing(self):
        """
        Handles the window closing event.
        """
        if self.is_watching:
            # Give a chance to confirm or stop gracefully
            if messagebox.askyesno("Confirm Exit", "The file watcher is active. Are you sure you want to exit? This will stop the watcher."):
                self.stop_watching()
                self.root.destroy()
            else:
                return # Don't close
        else:
            self.root.destroy()

if __name__ == "__main__":
    ctk.set_appearance_mode("Light") # System, Dark, Light
    ctk.set_default_color_theme("blue") # blue, dark-blue, green

    app_root = ctk.CTk()
    app = ImageProcessingApp(app_root)
    app_root.protocol("WM_DELETE_WINDOW", app.on_closing)
    app_root.mainloop()