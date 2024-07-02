import json
from urllib import request, parse
import random
import os 
import io
from sys import stdout
import uuid
import websocket
import urllib
import base64
from flask import send_file


# Get the absolute path of the parent directory
parent_dir = os.path.dirname(os.getcwd())

seed = random.randint(1, 184409551614)
workflow_api_json = "{}{}".format(os.path.abspath(os.path.dirname(__file__)), "/style_workflow_api.json")
output_image_path = os.path.join(parent_dir, "static", "output")
bg_images_path = os.path.join(parent_dir, "static", "bg_colors")

server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

def process_prompt(
        workflow_api_json: str, 
        seed: str, 
        input_image_path: str, 
        background_image_path: str, 
        output_image_path: str,
        output_image_name:str
        ) -> dict:
    """
    Process the given prompt path and replace the variables in the JSON file.
    
    Args:
        prompt_path(str): The path of the prompt to be processed.
    
    Returns:
        prompt_text: The prompt to be processed in string format
    """

    # Load the JSON file
    with open(workflow_api_json, encoding="utf8") as file:
        data = json.load(file)  # data is now a Python dictionary

    # Change the seed in each generation for the server to process a new prompt
    for key, value in data.items():
        if "inputs" in value:
            if "_meta" in value and value["_meta"].get("title") == "KSampler":
                value["inputs"]["seed"] = seed
            elif "_meta" in value and value["_meta"].get("title") == "Load Input Image":
                input_image_node = value
            elif "_meta" in value and value["_meta"].get("title") == "Load Background Image":
                background_image_node = value
            elif "_meta" in value and value["_meta"].get("title") == "Save Output Image":
                output_image_node = value

    # Modify the desired properties
    # Assuming you want to change the image file name

    input_image_node["inputs"]["image"] = input_image_path
    output_image_node["inputs"]["output_path"] = output_image_path
    output_image_node["inputs"]["filename_prefix"] = output_image_name
    background_image_node["inputs"]["image"] = background_image_path
    

    # Convert the modified JSON object (dictionary) to a JSON-formatted string
    json_string = json.dumps(data, indent=2)
    prompt_text = json_string
    return prompt_text

def queue_prompt(prompt) :
    """
    Send a prompt to the server to be processed.
    
    Args:
        prompt: The prompt to be sent to the server.
    
    Returns:
        dict: A dictionary containing the prompt_id, number, and node_errors
        
    """
    # Create a dictionary with the provided prompt and client_id (global).
    p = {"prompt": prompt, "client_id": client_id}
    
    # Convert the dictionary to a JSON string and then encode it to bytes.
    # This encoding is necessary as the data needs to be sent in a byte format over HTTP.
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    response = urllib.request.urlopen(req).read()
    print(response)
    return json.loads(response)

def get_image(filename, subfolder, folder_type) :
    """
    Retrieve an image from the server.
    
    Args:
        filename: The name of the image file.
        subfolder: The subfolder where the image is located.
        folder_type: The type of the folder.
        
    Returns:
        str: The URL of the image.
    """
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    print(data)
    url_values = urllib.parse.urlencode(data)
    image_url = "{}\\{}".format(output_image_path, filename)
    print(image_url)
    return image_url

def get_history(prompt_id):
    """
    Retrieve the history of a prompt from the server.
    
    Args:
        prompt_id: The unique identifier of the prompt.
    
    Returns:  
        dict: A dictionary containing every the execution of the prompt
    """
    # Send a GET request to the server to retrieve the history of the prompt.
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())

def get_images(websocket, prompt):
    """
    This function sends the prompt to the server and waits for the execution to complete.
    It then retrieves the output images from the server and returns them as a dictionary.
    
    Args:
        websocket: The websocket object used to communicate with the server.
        prompt: The prompt to be sent to the server.
        
    Returns: 
        dict: A dictionary with the output_node_id as the key and a list of images
    
    """
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    
    # While websocket is open
    while True:
        # Receive the message from the websocket
        out = websocket.recv()
        # If the message is a string, parse it as JSON
        if isinstance(out, str):
            message = json.loads(out)
            # If message is of type 'executing', then indicates ongoing execution.
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break #Execution is done
            # If message is of type 'progress', then indicates progress of execution.
            elif message['type'] == 'progress':
                data = message['data']
                print_progress(data['value'], data['max'])

                print(f"Progress: Step {data['value']} of {data['max']})")
                # When progress is complete
                if data['value'] == data['max']:
                    print("\nPrompt complete!")
        else:
            # If the message is not text (e.g., binary), ignore & continue
            continue 
    
    # Retrieve the execution history for the given prompt ID.
    history = get_history(prompt_id)[prompt_id]
    
    for o in history['outputs']:
        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            # Check if the node output contains images.
            if 'images' in node_output:
                images_output = []
                for image in node_output['images']:
                    # Retrieve each image data from the server.
                    image_data = get_image(image['filename'], image['subfolder'], image['type'])
                    images_output.append(image_data)
            # Store the list of images for the current node (queue task) in the output_images dictionary.
            output_images[node_id] = images_output
    # If there is only one prompt request for one image, return the image data directly.
    return output_images

def print_progress(value, max_value):
    """
    Renders a progress bar in the console.
    
    Args:
        value: The current value of the progress.
        max_value: The maximum value of the progress
        
    Returns: 
        None
    """
    bar_length = 50  # Length of the progress bar
    percent = float(value) / max_value
    arrow = '-' * int(round(percent * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    # Update the progress bar in place
    stdout.write("\rProgress: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
    stdout.flush()

# create new websocket object
ws = websocket.WebSocket()  


def process_image_with_comfy(input_image_path: str, output_directory: str, output_image_name:str, bg_color: str ) -> str:
    """
    Process the input image using the Comfy style workflow API.
    
    Args:
        input_image_path (str): The path to the input image.
        output_directory (str): The directory to save the processed image.
        bg_color (str): The background color for the processed image.
    
    Returns:
        str: The path to the processed image.
    """
    
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    background_image_path = "{}\{}.png".format(bg_images_path, bg_color)
    prompt_text = process_prompt(
        workflow_api_json, 
        seed, 
        input_image_path, 
        background_image_path, 
        output_image_path,
        output_image_name)
    prompt = json.loads(prompt_text)
    image_data = get_images(ws, prompt)
    
    
    processed_image_path = image_data[list(image_data.keys())[0]][0]
    print("style_workflow_web_socket : " + processed_image_path)
    ws.close()
    return processed_image_path


#process_image_with_comfy(input_image_path, output_image_path, "blue")

