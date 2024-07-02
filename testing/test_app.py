import unittest
from PIL import Image
import os
import sys
import requests
from io import BytesIO
import datetime


OS_TYPE = "Windows" if os.name == 'nt' else "Linux"

# Define the path separator based on the operating system
PATH_SEPARATOR = '\\' if OS_TYPE == 'Windows' else '/'
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the parent directory to sys.path
sys.path.append(parent_dir)

from workflow_api import style_workflow_websockets_api
from workflow_api import upscale_workflow_websockets_api
from workflow_api import apply_image_adjustments

class TestImageProcessing(unittest.TestCase):

    def setUp(self):
        self.input_image_path = os.path.abspath('test_input_image.png')
        self.output_directory = os.path.join(parent_dir, "static", "output")
        self.bg_color = 'blue'
        self.brightness = 20
        self.contrast = 100
        self.input_image = self.input_image_path  # Directly assign the path to the input image
        self.output_image_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        #img = Image.new('RGB', (100, 100), color = 'red')
        #img.save(self.input_image)

    def tearDown(self):
        # Clean up created files
        for f in os.listdir(self.output_directory):
            os.remove(os.path.join(self.output_directory, f))
            return
        
    def test_process_image(self):
        image_path = style_workflow_websockets_api.process_image_with_comfy(self.input_image, self.output_directory, self.output_image_name, self.bg_color)
        self.assertTrue(os.path.exists(image_path))

    def test_upscale_image(self):
        image_path = upscale_workflow_websockets_api.process_image_with_comfy(self.input_image, self.output_directory, self.output_image_name, 3000)
        self.assertTrue(os.path.exists(image_path))

    def test_adjust_image(self):
        img = Image.open(self.input_image)
        img_brightness = apply_image_adjustments.adjust_brightness(img, self.brightness)
        img_contrast = apply_image_adjustments.adjust_contrast(img, self.contrast)
        
        # Save the adjusted image to verify it works
        adjusted_image_path = os.path.join(self.output_directory, 'adjusted_image.png')
        img_contrast.save(adjusted_image_path)

        # Check if the adjusted image exists and is an instance of Image
        self.assertTrue(os.path.exists(adjusted_image_path))
        self.assertIsInstance(img_contrast, Image.Image)

if __name__ == '__main__':
    unittest.main()
