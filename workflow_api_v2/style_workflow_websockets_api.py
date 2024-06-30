import json
from urllib import request, parse
import random
import os 
import io
from sys import stdout
import uuid
import websocket
import urllib

abs_path = os.path.abspath(os.path.dirname(__file__))
seed = random.randint(1, 184409551614)

image_output_path = os.path.abspath(os.path.dirname(__file__))

# Load the JSON file
with open('workflow_api.json', encoding="utf8") as file:
    data = json.load(file)  # data is now a Python dictionary

# Chagne the seed in each generation
if "3" in data and "inputs" in data["3"]:
  data["3"]["inputs"]["seed"] = seed

if "10" in data and "inputs" in data["10"]:
  input_image_node = data["10"]

if "59" in data and "inputs" in data["59"]:
  background_image_node = data["59"]

if "36" in data and "inputs" in data["36"]:
  output_image_node = data["36"]
  

# Modify the desired properties
# Assuming you want to change the image file name
if "10" in data  and "inputs" in data["10"]:
    input_image_node["inputs"]["image"] = os.path.abspath("input_image_2.png")
    output_image_node["inputs"]["output_path"] = os.path.abspath(os.path.dirname(__file__))


# Convert the modified JSON object (dictionary) to a JSON-formatted string
json_string = json.dumps(data, indent=2)

prompt_text = json_string


server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

def queue_prompt(prompt):
    # Create a dictionary with the provided prompt and client_id (global).
    p = {"prompt": prompt, "client_id": client_id}
    
    # Convert the dictionary to a JSON string and then encode it to bytes.
    # This encoding is necessary as the data needs to be sent in a byte format over HTTP.
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    print(data)
    url_values = urllib.parse.urlencode(data)
    image_url = image_output_path + "\\" + filename
    print(image_url)
    return image_url
    # with urllib.request.urlopen("http://{}/view?{}".format(image_output_path, url_values)) as response:
    #     return response.read()

def get_history(prompt_id):
      # Construct the URL for the request.
    # This URL is formatted to access the 'history' endpoint on the server,
    # includes the 'server_address' and 'prompt_id' as part of the URL path.
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())

def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break #Execution is done
            elif message['type'] == 'progress':
                data = message['data']
                print_progress(data['value'], data['max'])

                print(f"Progress: Step {data['value']} of {data['max']})")
                # When progress is complete
                if data['value'] == data['max']:
                    print("\nPrompt complete!")
        else:
            continue #previews are binary data

    history = get_history(prompt_id)[prompt_id]
    for o in history['outputs']:
        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            if 'images' in node_output:
                images_output = []
                for image in node_output['images']:
                    print("image" + str(image))
                    image_data = get_image(image['filename'], image['subfolder'], image['type'])
                    images_output.append(image_data)
            output_images[node_id] = images_output

    return output_images

def print_progress(value, max_value):
    bar_length = 50  # Length of the progress bar
    percent = float(value) / max_value
    arrow = '-' * int(round(percent * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    # Update the progress bar in place
    stdout.write("\rProgress: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
    stdout.flush()

# create new websocket object
ws = websocket.WebSocket()  
# connect to the websocket server
ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
print(f"client ID = {client_id}")

prompt = json.loads(prompt_text)

# get images, passing the ws and prompt_workflow
# returns a dictionary of output_node_id (key) and list of images (value)
images = get_images(ws, prompt)

