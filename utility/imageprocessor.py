import logging
import os
import cv2

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
