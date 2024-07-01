import json
from urllib import request, parse
import random
import os 

abs_path = os.path.abspath(os.path.dirname(__file__))
seed = random.randint(1, 184409551614)

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

def queue_prompt(prompt):
    p = {"prompt": prompt}
    data = json.dumps(p).encode('utf-8')
    req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
    request.urlopen(req)


prompt = json.loads(prompt_text)

queue_prompt(prompt)

