from nodes import NODE_CLASS_MAPPINGS, LoadImage
import os
import random
import sys
from typing import Sequence, Mapping, Any, Union
import torch

def get_value_at_index(obj: Union[Sequence, Mapping], index: int) -> Any:
    """Returns the value at the given index of a sequence or mapping.

    If the object is a sequence (like list or string), returns the value at the given index.
    If the object is a mapping (like a dictionary), returns the value at the index-th key.

    Some return a dictionary, in these cases, we look for the "results" key

    Args:
        obj (Union[Sequence, Mapping]): The object to retrieve the value from.
        index (int): The index of the value to retrieve.

    Returns:
        Any: The value at the given index.

    Raises:
        IndexError: If the index is out of bounds for the object and the object is not a mapping.
    """
    try:
        return obj[index]
    except KeyError:
        return obj["result"][index]

# Ensure ComfyUI is found and its path added to sys.path
def find_path(name: str, path: str = None) -> str:
    """
    Looks at the given path to find the given name.
    Returns the path as a string if found, or None otherwise.
    """
    # If no path is given, use the current working directory
    if path is None:
        path = os.getcwd()
    
    # Check if the current directory contains the name
    for root, dirs, files in os.walk(path):
        if name in dirs or name in files:
            path_name = os.path.join(root, name)
            print(f"{name} found: {path_name}")
            return path_name
    return None


def add_comfyui_directory_to_sys_path() -> None:
    """
    Add 'ComfyUI' to the sys.path
    """
    comfyui_path = find_path("ComfyUI")
    if comfyui_path is not None and os.path.isdir(comfyui_path):
        sys.path.append(comfyui_path)
        print(f"'{comfyui_path}' added to sys.path")


def add_extra_model_paths() -> None:
    """
    Parse the optional extra_model_paths.yaml file and add the parsed paths to the sys.path.
    """
    from main import load_extra_path_config

    extra_model_paths = find_path("extra_model_paths.yaml")

    if extra_model_paths is not None:
        load_extra_path_config(extra_model_paths)
    else:
        print("Could not find the extra_model_paths config file.")


add_comfyui_directory_to_sys_path()
add_extra_model_paths()


def import_custom_nodes() -> None:
    """Find all custom nodes in the custom_nodes folder and add those node objects to NODE_CLASS_MAPPINGS

    This function sets up a new asyncio event loop, initializes the PromptServer,
    creates a PromptQueue, and initializes the custom nodes.
    """
    import asyncio
    import execution
    from nodes import init_custom_nodes
    import server

    # Creating a new event loop and setting it as the default loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Creating an instance of PromptServer with the loop
    server_instance = server.PromptServer(loop)
    execution.PromptQueue(server_instance)

    # Initializing custom nodes
    init_custom_nodes()


def upscale_image_with_comfy(input_image_path, output_image_path):
    """Upscale the input image using the Comfy upscale workflow API.
    """
    import_custom_nodes()
    with torch.inference_mode():
        upscalemodelloader = NODE_CLASS_MAPPINGS["UpscaleModelLoader"]()
        upscalemodelloader_12 = upscalemodelloader.load_model(
            model_name="4xUltrasharp_4xUltrasharpV10.pth"
        )

        loadimage = LoadImage()
        loadimage_13 = loadimage.load_image(image=input_image_path)

        constant_number = NODE_CLASS_MAPPINGS["Constant Number"]()
        constant_number_34 = constant_number.return_constant_number(
            number_type="integer", number=3300
        )

        constant_number_35 = constant_number.return_constant_number(
            number_type="integer", number=2400
        )

        imageupscalewithmodel = NODE_CLASS_MAPPINGS["ImageUpscaleWithModel"]()
        #resizeimagemixlab = NODE_CLASS_MAPPINGS["ResizeImageMixlab"]()
        image_save = NODE_CLASS_MAPPINGS["Image Save"]()

        for q in range(1):
            imageupscalewithmodel_29 = imageupscalewithmodel.upscale(
                upscale_model=get_value_at_index(upscalemodelloader_12, 0),
                image=get_value_at_index(loadimage_13, 0),
            )

            # resizeimagemixlab_31 = resizeimagemixlab.run(
            #     width=[3300],
            #     height=[2400],
            #     scale_option="width",
            #     average_color="on",
            #     fill_color="#FFFFFF",
            #     image=get_value_at_index(imageupscalewithmodel_29, 0),
            # )

            image_save_37 = image_save.was_save_images(
                output_path=output_image_path,
                filename_prefix="UPSCALE",
                filename_delimiter="_",
                filename_number_padding=4,
                filename_number_start="false",
                extension="png",
                quality=100,
                lossless_webp="false",
                overwrite_mode="false",
                show_history="false",
                show_history_by_prefix="true",
                embed_workflow="true",
                show_previews="true",
                images=get_value_at_index(imageupscalewithmodel_29, 0),
            )

        print("Image saved successfully!" +
            output_image_path + str(image_save_37['ui']['images'][0]['filename']))
        return output_image_path + f"/{str(image_save_37['ui']['images'][0]['filename'])}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Image Processing Workflow")
    parser.add_argument("-i", "--input_image_path", type=str,
                        help="Path to the input image file")
    parser.add_argument("-o", "--output_image_path", type=str,
                        help="Path to save the output image file")
    args = parser.parse_args()

    upscale_image_with_comfy(args.input_image_path, args.output_image_path)
