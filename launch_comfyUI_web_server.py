from flask import Flask,send_file, render_template, request, Flask, send_from_directory, abort,jsonify
from PIL import Image
import os
from workflow_api import style_workflow_websockets_api
#from workflow_api import upscale_workflow_api
import logging
from PIL import ImageEnhance, Image
from flask_cors import CORS


# Define the paths for the input and output images
INPUT_IMAGE_PATH = 'static/input_image.png'
PROCESSED_IMAGE_PATH = 'static/output'
ADJUSTED_IMAGE_PATH = 'static/output/adjusted_image.png'
DOWNLOAD_IMAGE_PATH = 'static/output/download_image.png'
UPSCALED_IMAGE_PATH = 'static/output/'


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
    
    input_image_path = os.path.abspath(INPUT_IMAGE_PATH)
    processed_image_path = os.path.abspath(PROCESSED_IMAGE_PATH)

    # Save the image to the input image path
    image.save(os.path.abspath(INPUT_IMAGE_PATH))

    logging.info("Processing the image...")

    # Process the image and save the processed image
    processed_image_result_path  = style_workflow_websockets_api.process_image_with_comfy(
        input_image_path, processed_image_path, background_color
    )
    
    # Return a JSON response with the Base64-encoded image
    return send_file(processed_image_result_path , mimetype='image/png')

# # upscale image endpoint -> upscale the image, crop it using user defined values, and return the upscaled image
# @app.route('/upscale', methods=['POST'])
# def upscale():
#     """Upscale Image Endpoint:
#     1. Upscale the image
#     3. Adjust brightness and contrast
#     4. Resize the image based on the selected format
#     5. Return the upscaled image url"""
    
#     logging.info("Upscale endpoint reached...")

#     # Define a list of form fields
#     form_fields = [
#         'brightness', 'contrast'
#     ]
#     # Use a dictionary comprehension to get the form data
#     form_data = {field: request.form[field] for field in form_fields}

    
#     # Iterate over the keys and log their values from the request form
#     for key in form_fields:
#         logging.info("%s value: %s", key, request.form[key])

#     logging.info("FormData processed")

#     # check for image
#     file = request.files['image']
#     if file.filename == '':
#         return "No image selected", 400

#     logging.info("image received")
    
#     # Open the received image file
#     input_image = Image.open(file.stream)

#     # Adjust image brightness and contrast based on form_data
#     adjusted_image = adjust_image(input_image, float(form_data['brightness']), float(form_data['contrast']))
#     adjusted_image.save(ADJUSTED_IMAGE_PATH)

#     # upscale the image
#     logging.info("Upscaling the image...")
#     upscaled_image = upscale_workflow_api.upscale_image_with_comfy(os.path.abspath(
#         ADJUSTED_IMAGE_PATH), os.path.abspath(UPSCALED_IMAGE_PATH))
#     logging.info("Upscaling image complete!")

#     logging.info("upscaled Image: %s", upscaled_image)
#     logging.info("Type of upscaled_image: %s", type(upscaled_image))

#     # # Open the image to resize it
#     # upscaled_image = Image.open(upscaled_image)

#     # # Save the resized image to the download image path
#     # upscaled_image.save(os.path.abspath(DOWNLOAD_IMAGE_PATH))
#     # logging.info("download Image AFTER RESIZE: %s", DOWNLOAD_IMAGE_PATH)
#     # logging.info("download Image AFTER RESIZE: %s", DOWNLOAD_IMAGE_PATH.split(f'static{PATH_SEPARATOR}')[1])

#     # Return a JSON response with the download image path
#     #return jsonify({"image_url": upscaled_image})
#     return jsonify({"image_url": upscaled_image.split(f'static{PATH_SEPARATOR}')[1]})

def adjust_image(image, brightness, contrast):
    """Adjust image brightness and contrast."""
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(brightness / 200.0)

    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(contrast / 200.0)

    return image

# If debug set to True the image processing will hang up before the image is processed
# host must be set to '0.0.0.0' when hosting on a runpod server/dockerized container
# set threaded to false to avoid issues with the image processing
if __name__ == '__main__':
    app.run(debug=False, threaded=False, host='0.0.0.0', port=5001)
