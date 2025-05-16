# Monitors a folder for new image files and processes them. 

import threading
import logging
import os
import time


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