from dotenv import load_dotenv
import os

# Path to the directory one level above the current file
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Determine which environment to load
env = os.getenv('FLASK_ENV', 'development')
print(f"Current Environment: {env}")

# Map the environment to the corresponding .env file
env_files = {
    'development': os.path.join(parent_dir, '.env.development'),
    'production': os.path.join(parent_dir, '.env.production'),
    'testing': os.path.join(parent_dir, '.env.testing')
}

# Load the .env file for the current environment
dotenv_path = env_files.get(env, os.path.join(parent_dir, '.env'))
load_dotenv(dotenv_path)

# Get the environment variable
server_address = os.getenv("SERVER_ADDRESS")
output_image_path = os.getenv("OUTPUT_IMAGE_PATH")
upscale_workflow_api_json = os.getenv("UPSCALE_WORKFLOW_API_JSON")
style_workflow_api_json = os.getenv("STYLE_WORKFLOW_API_JSON")
upscaled_image_path = os.getenv("UPSCALED_IMAGE_PATH")
background_image_path = os.getenv("BACKGROUND_IMAGE_PATH")

print(background_image_path)