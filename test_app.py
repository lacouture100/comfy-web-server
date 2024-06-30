import unittest
from launch_comfyUI_web_server import process_image, upscale_image, adjust_image
from PIL import Image
import os


OS_TYPE = "Windows" if os.name == 'nt' else "Linux"

# Define the path separator based on the operating system
PATH_SEPARATOR = '\\' if OS_TYPE == 'Windows' else '/'


class TestImageProcessing(unittest.TestCase):

    def setUp(self):
        self.input_image = os.path.abspath(f'static{PATH_SEPARATOR}test_input_image.png')
        self.output_directory = os.path.abspath(f'static{PATH_SEPARATOR}output{PATH_SEPARATOR}')
        self.bg_color = 'blue'
        self.brightness = 100
        self.contrast = 100
        
        # Create a test image
        img = Image.new('RGB', (100, 100), color = 'red')
        img.save(self.input_image)

    def tearDown(self):
        # Clean up created files
        if os.path.exists(self.input_image):
            os.remove(self.input_image)
        for f in os.listdir(self.output_directory):
            os.remove(os.path.join(self.output_directory, f))

    def test_process_image(self):
        processed_image_path = process_image(self.input_image, self.output_directory, self.bg_color)
        self.assertTrue(os.path.exists(processed_image_path))

    def test_upscale_image(self):
        upscaled_image_path = upscale_image(self.input_image, self.output_directory)
        self.assertTrue(os.path.exists(upscaled_image_path))

    def test_adjust_image(self):
        img = Image.open(self.input_image)
        adjusted_image = adjust_image(img, self.brightness, self.contrast)
        self.assertIsInstance(adjusted_image, Image.Image)

if __name__ == '__main__':
    unittest.main()
