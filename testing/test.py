import unittest
from PIL import Image
import os
import sys
import requests
import datetime
import json
from flask import Flask
from flask_cors import CORS
import importlib.util
from io import BytesIO
 

OS_TYPE = "Windows" if os.name == 'nt' else "Linux"

# Define the path separator based on the operating system
PATH_SEPARATOR = '\\' if OS_TYPE == 'Windows' else '/'
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the parent directory to sys.path
sys.path.append(parent_dir)

from workflow_api import style_workflow_api
from workflow_api import upscale_workflow_api
from utils import image_utils


flask_app_path = os.path.join(parent_dir, 'launch_comfyui_web_server.py')

# Dynamically load the Flask app from the script as its own module
spec = importlib.util.spec_from_file_location("launch_comfyui_web_server", flask_app_path)
launch_comfyui_web_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launch_comfyui_web_server)
app = launch_comfyui_web_server.app


class TestImageProcessing(unittest.TestCase):
    """
    Test the image processing functions
    """
    def setUp(self):
        self.input_image = os.path.abspath('test_input_image.png')
        self.output_directory = os.path.join(parent_dir, "static", "output")
        self.bg_color = 'blue'
        self.brightness = 20
        self.contrast = 100
        self.output_image_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    def tearDown(self):
        # Clean up created files
        for f in os.listdir(self.output_directory):
            os.remove(os.path.join(self.output_directory, f))
            return
        
    def test_process_image(self):
        image_path = style_workflow_api.process_image_with_comfy(self.input_image, self.output_directory, self.output_image_name, self.bg_color)
        self.assertTrue(os.path.exists(image_path))

    def test_upscale_image(self):
        image_path = upscale_workflow_api.process_image_with_comfy(self.input_image, self.output_directory, self.output_image_name, 3000)
        self.assertTrue(os.path.exists(image_path))

    def test_adjust_image(self):
        img = Image.open(self.input_image)
        img_brightness = image_utils.adjust_brightness(img, self.brightness)
        img_contrast = image_utils.adjust_contrast(img, self.contrast)
        
        # Save the adjusted image to verify it works
        adjusted_image_path = os.path.join(self.output_directory, 'adjusted_image.png')
        img_contrast.save(adjusted_image_path)

        # Check if the adjusted image exists and is an instance of Image
        self.assertTrue(os.path.exists(adjusted_image_path))
        self.assertIsInstance(img_contrast, Image.Image)


class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        self.input_image = os.path.abspath('test_input_image.png')
        self.output_directory = os.path.join(parent_dir, "static", "output")

    @classmethod
    def setUpClass(cls):
        # Set up the test client before any tests run
        cls.client = app.test_client()
        cls.client.testing = True

    def tearDown(self):
        # Clean up created files
        for f in os.listdir(self.output_directory):
            os.remove(os.path.join(self.output_directory, f))
            return
        
    def test_process(self):
        # Test the /process route with a POST request using test_input_image.png
        with open(self.input_image, 'rb') as image_file:
            test_image = BytesIO(image_file.read())

        response = self.client.post('/process', content_type='multipart/form-data', data={
            'image': (test_image, 'test_input_image.png'),
            'background_color': 'blue'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'image/png')

    def test_upscale(self):
            # Test the /upscale route with a POST request using test_input_image.png
            with open(self.input_image, 'rb') as image_file:
                test_image = BytesIO(image_file.read())

            response = self.client.post('/upscale', content_type='multipart/form-data', data={
                'image': (test_image, 'test_input_image.png'),
                'brightness': '1.0',
                'contrast': '1.0',
                'format': '1000',
                'crop_width': '240',
                'crop_height': '330',
                'crop_x': '10',
                'crop_y': '10'
            })

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.mimetype, 'application/json')

            # Parse the JSON response
            data = response.get_json()
            self.assertIn('image_url', data)
            self.assertTrue(data['image_url'].startswith('output/'))

if __name__ == '__main__':
    unittest.main()
