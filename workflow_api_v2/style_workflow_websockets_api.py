import json
from urllib import request, parse
import random
import os 
import io
from sys import stdout
import uuid
import websocket
import urllib

seed = random.randint(1, 184409551614)
workflow_api_json = "workflow_api.json"
image_output_path = os.path.abspath(os.path.dirname(__file__))
input_image_path = os.path.abspath("input_image_2.png")
background_image_path = os.path.abspath("bg_blue.png")
is_single_image = False

def process_prompt(workflow_api_json: str, seed: str, input_image_path: str, background_image_path: str, output_image_path: str) -> dict:
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

    # # Change the seed in each generation for the server to process a new prompt
    # if "3" in data and "inputs" in data["3"]:
    #   data["3"]["inputs"]["seed"] = seed

    # if "10" in data and "inputs" in data["10"]:
    #   input_image_node = data["10"]

    # if "59" in data and "inputs" in data["59"]:
    #   background_image_node = data["59"]

    # if "36" in data and "inputs" in data["36"]:
    #   output_image_node = data["36"]
      
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
    background_image_node["inputs"]["image"] = background_image_path
    

    # Convert the modified JSON object (dictionary) to a JSON-formatted string
    json_string = json.dumps(data, indent=2)
    prompt_text = json_string
    return prompt_text


server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

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
    image_url = "{}\\{}".format(image_output_path, filename)
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
    # includes the 'server_address' and 'prompt_id' as part of the URL path.
    print("http://{}/history/{}".format(server_address, prompt_id))
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

def retrieve_processed_image_url(images_dict: dict) -> str:
    """
    Retrieve the URL of the processed image from the dictionary of images.
    
    Args:
        images_dict: A dictionary containing the output_node_id and list of images.
        
    Returns:
        str: The URL of the processed image.
    """
    # Retrieve the first image from the dictionary

    image_url = images_dict[list(images_dict.keys())[0]][0]
    return image_url


# create new websocket object
ws = websocket.WebSocket()  

# connect to the websocket server
ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
print(f"client ID = {client_id}")


prompt_text = process_prompt(workflow_api_json, seed, input_image_path, background_image_path, image_output_path)
prompt = json.loads(prompt_text)

# get images, passing the ws and prompt_workflow
# returns a dictionary of output_node_id (key) and list of images (value)
image_data = get_images(ws, prompt)
processed_image_url = retrieve_processed_image_url(image_data)
print(processed_image_url )

