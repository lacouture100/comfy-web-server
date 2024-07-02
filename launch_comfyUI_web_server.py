from flask import Flask,send_file, render_template, request, Flask, send_from_directory, abort,jsonify
from PIL import Image
import os
from workflow_api import style_workflow_api, upscale_workflow_api
from utils import image_utils
#from workflow_api import upscale_workflow_api
import logging
from PIL import ImageEnhance, Image
from flask_cors import CORS
import tempfile
import datetime


# Define the paths for the input and output images
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
UPSCALED_IMAGE_PATH = os.path.join(parent_dir,'comfy-web-server/static/output/')


# Setup basic configuration for logging

logging.basicConfig(level=logging.DEBUG,  # Capture all levels of messages
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.FileHandler('app.log'),  # Log to this file
                              logging.StreamHandler()])  # And also logging.info to console
logger = logging.getLogger()

# Initialize the app
app = Flask(__name__, static_folder='static')
CORS(app)

# Home route
@app.route('/')
def index():
    """ Render the frontend defined in 'templates' directory"""
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    """Initial Image Processing Endpoint:
     1. Convert to Oil Painting Style
     2. Add custom color background 
     3. Return the processed image url
     4. Send the processed image to the frontend
     """

    logging.info("Processing api reached...")

    # check for image
    if 'image' not in request.files:
        # Return an error to frontend if no image is uploaded
        return "No image uploaded", 400
    
    image = request.files['image']

    # check for background color
    background_color = request.form['background_color']
    if not background_color:
        return "No background color provided", 400
    
    # Create a temporary file for the input image
    with tempfile.NamedTemporaryFile(delete=False) as temp_input_file:
        image.save(temp_input_file.name)
        input_image_path = temp_input_file.name

    # Create a temporary file for the processed image
    with tempfile.NamedTemporaryFile(delete=False) as temp_output_file:
        processed_image_path = temp_output_file.name

    # Save the image to the input image path
    #image.save(os.path.abspath(INPUT_IMAGE_PATH))
    try:
        logging.info("Processing the image...")
        
        image_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Process the image and save the processed image
        processed_image_result_path  = style_workflow_api.process_image_with_comfy(
            input_image_path, processed_image_path, image_name, background_color
        )
        
        logging.info("Image processed...")

        # Return a JSON response with the Base64-encoded image
        return send_file(processed_image_result_path , mimetype='image/png')
    finally:
        os.remove(input_image_path)
        os.remove(processed_image_path) 

# upscale image endpoint -> upscale the image, crop it using user defined values, and return the upscaled image
@app.route('/upscale', methods=['POST'])
def upscale():
    """Upscale Image Endpoint:
    1. Upscale the image
    3. Adjust brightness and contrast
    4. Resize the image based on the selected format
    5. Return the upscaled image url"""
    
    logging.info("Upscale endpoint reached...")

    # Define a list of form fields
    form_fields = ['brightness', 'contrast', 'format', 'crop_width', 'crop_height', 'crop_x', 'crop_y']
    # Use a dictionary comprehension to get the form data
    form_data = {field: request.form[field] for field in form_fields}

    # check for image
    file = request.files['image']
    if file.filename == '':
        return "No image selected", 400

    logging.info("image received")
    
    # Open the received image file
    input_image = Image.open(file.stream)
    
    # Apply cropping
    crop_x, crop_y = int(form_data['crop_x']), int(form_data['crop_y'])
    crop_width, crop_height = int(form_data['crop_width']), int(form_data['crop_height'])
    cropped_img = image_utils.crop_image(input_image, crop_x, crop_y, crop_width, crop_height)

    # Adjust image brightness and contrast based on form_data
    brightness = float(form_data['brightness'])
    contrast = float(form_data['contrast'])
    adjusted_image = image_utils.adjust_brightness(cropped_img, brightness)
    adjusted_image = image_utils.adjust_contrast(adjusted_image, contrast)

    # Create a temporary file for the adjusted image
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_adjusted_file:
        adjusted_image.save(temp_adjusted_file.name)
        adjusted_image_path = temp_adjusted_file.name

    # Create a temporary file for the upscaled image
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_upscaled_file:
        upscaled_image_path = temp_upscaled_file.name

    try:
        image_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # upscale the image using process_image_with_comfy
        logging.info("Upscaling the image...")

        upscaled_image_result_path = upscale_workflow_api.process_image_with_comfy(
            adjusted_image_path, os.path.abspath(UPSCALED_IMAGE_PATH), image_name, 3300
        )
        logging.info("Upscaling image complete!")

        # Construct the URL for the upscaled image
        image_url = f"output/{os.path.basename(upscaled_image_result_path)}"
        
        # Return a JSON response with the image URL
        return jsonify({"image_url": image_url})
    
    finally:
        os.remove(adjusted_image_path)
        os.remove(upscaled_image_path)

# If debug set to True the image processing will hang up before the image is processed
# host must be set to '0.0.0.0' when hosting on a runpod server/dockerized container
# set threaded to false to avoid issues with the image processing
if __name__ == '__main__':
    app.run(debug=False, threaded=False, host='0.0.0.0', port=5001)
