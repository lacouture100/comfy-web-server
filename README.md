

# ComfyUI Image Processing Server

## Project Description

This repository contains a Flask-based server that processes images by connecting to the ComfyUI API. The server allows for image processing with Comfy UI, such as converting an image to an oil painting style, adding a custom background color, and upscaling the image, among others. It is designed to be easily extensible for additional image processing workflows.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Usage](#usage)
4. [System Architecture](#system-architecture)
5. [Directory Structure](#directory-structure)
5. [Testing](#testing)
6. [Contributing](#contributing)
7. [License](#license)



![Image to Painting Example](readme_content/readme_example_image.png)

---

 
## Getting Started

### 1. Prerequisites

- Python 3.11+
- Pip (Python package installer)
- ComfyUI directory in the same parent directory of this downloaded repository. You can download the latest version with

    ```bash
    git clone https://github.com/comfyanonymous/ComfyUI.git
    ```

- Refer to the "Models.text" file to find a list of used models and their respective download. Download the models and include them in the `ComfyUI/models` folder.

### 2. Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/lacouture100/comfy-web-server.git
    cd comfyui-image-processing-server
    ```

2. Start a new python terminal and create an environment.
    ```bash
      conda create -n comfyui-server 
    ```
3. Activate your conda environment
    ```bash
    conda activate comfyui-server
    ```

4. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

### 3. Running the Server

1. Ensure the ComfyUI server is running and accessible. If you are using the ComfyUI windows portable version, double click the `run_nvidia_gpu.bat` file. This should start the ComfyUI server on `http://localhost:8188`.


2. Start the Flask server:

    ```bash
    python launch_comfyUI_web_server.py
    ```

   The server will be running on `http://localhost:5001`.

### 4. System Architecture


![Directory Structure](readme_content/system_architecture.svg)

#### Explanation
- **THINGMADE Client (Browser)**: Handles incoming requests and interacts with ComfyUI and Image Storage.
- **Shopify THINGMADE Store**: Displays the full catalog of merchandise.
- **Shopify Store Backend**: Handles product inventory and media.
- **Shopify THINGMADE Frontend**: Uses Liquid and Javascript to render the store frontend and interacts with the Shopify Store Product. **NOTE:** The frontend is not included in this repository.
- **NGINX**: Securely forwards requests to the Flask Server, converting to HTTPS for secure transfer. It is not necessary to run this server.[More information about NGINX and how to set it up](https://nginx.org/en/docs/beginners_guide.html)
- **Flask Server**: Handles incoming requests, interacts with ComfyUI and Image Storage.
- **ComfyUI**: Processes and upscale the image.
- **Image Storage**: Stores processed images.

#### API Endpoints

#### Home Route

- **GET `/`**
  - Renders the frontend defined in the `templates` directory.

#### Process Image

- **POST `/process`**
  - Processes an image by converting it to an oil painting style and adding a custom background color.
  - **Request Parameters**:
    - `image`: The image file to be processed.
    - `background_color`: The background color to be added to the image.
  - **Response**:
    - Returns the processed image file in binary format.

##### Upscale Image

- **POST `/upscale`**
  - This endpoint does the following:
    1. Crops the image given certain dimensions.
    2. Apply image filters such as brightness and contrast.
    3. Upscales the image.
  - **Request Parameters**:
    - `image`: The image file to be processed.
    - `brightness`: The brightness adjustment value.
    - `contrast`: The contrast adjustment value.
    - `crop_width`: The width of the crop area.
    - `crop_height`: The height of the crop area.
    - `crop_x`: The X coordinate for the crop area.
    - `crop_y`: The Y coordinate for the crop area.
  - **Response**:
    - Returns the saved image URL with the largest height/width dimension being "3300px"

### 5. Directory Structure

The following is an overview of the project's directory structure:

```plaintext
comfy-web-server/
├── readme_content/
│   └── readme_example_image.png
├── static/
│   └── bg_colors/
|   └── output/
├── templates/
│   └── index.html
├── testing/
│   └── test.py
├── utils/
│   ├── __init__.py
│   └── image_utils.py
├── workflow_api/
│   ├── __init__.py
│   └── style_workflow_api.py
│   └── upscale_workflow_api.py
├── .gitignore
├── app.log
├── launch_comfyUI_web_server.py
├── LICENSE
├── README.md
├── required_models.txt
└── requirements.txt
```

- **`readme_content/`**: Contains images and other assets for the README documentation.
- **`static/`**: Contains static files served by the Flask application.
    - `bg_colors/` : Directory containing several background images for color selection.
    - `output/`: Directory where processed images are stored.
- **`templates/`**: Contains HTML templates for rendering web pages.
    - `index.html`: Main HTML template for the web application.
- **`testing/`**: Contains test scripts for the project.
    - `test.py`: Script for testing the Flask application and image processing functions.
- **`utils/`**: Contains utility modules and functions.
    - `__init__.py`: Initialization file for the `utils` package.
    - `image_utils.py`: Utility functions for image processing.
- **`workflow_api/`**: Contains modules for handling image processing workflows.
    - `__init__.py`: Initialization file for the `workflow_api` package.
    - `config.py`: Configuration settings for the API.
    - `style_workflow_api.py`: Module for handling style transfer workflows.
    - `upscale_workflow_api.py`: Module for handling image upscaling workflows.
- **`.env.development`**: Environment variables for development.
- **`.env.testing`**: Environment variables for testing.
- **`app.log`**: Log file for the application.
- **`launch_comfyUI_web_server.py`**: Main script to launch the Flask web server.
- **`README.md`**: This README file.
- **`required_models.txt`**: List of required models and their download instructions.
- **`requirements.txt`**: List of required Python packages.

## 6. Testing

To ensure the functionality of the image processing server, a `test.py` script is included in the `testing` folder. The script uses the `unittest` framework to test various components and endpoints of the server. Change the development environment in the `comfy-web-server/workflow_api/config.py` file to `testing`, or `development`

### Prerequisites

- Ensure that your environment is set up as described in the [Prerequisites](#prerequisites) section.
- Place a test image named `test_image.png` in the `comfy-web-server/testing` directory of your repository.

### Running the Tests

1. Navigate to the directory containing your `test.py` script:
    ```bash
    cd comfy-web-server/testing
    ```

2. Run the tests using the `unittest` module:
    ```bash
    python test.py
    ```

### Explanation of the `test.py` Script

The `test.py` script includes two main test classes:

1. **TestImageProcessing**:
    - Tests individual image processing functions.
    - Methods:
        - `test_process_image`: Tests the image processing functionality.
        - `test_upscale_image`: Tests the image upscaling functionality.
        - `test_adjust_image`: Tests the image adjustment functions (brightness and contrast).

2. **TestFlaskApp**:
    - Tests the Flask app routes (`/process` and `/upscale`).
    - Methods:
        - `test_process`: Tests the `/process` route with a sample image and background color.
        - `test_upscale`: Tests the `/upscale` route with a sample image and various parameters.

Running these tests will ensure that your image processing server and its endpoints are functioning correctly.
## Configuration

- **Paths**:

  - `UPSCALED_IMAGE_PATH`: Path for saving the downloadable image.

## Contributing

Contact the developers of this repository to contribute to this project.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

