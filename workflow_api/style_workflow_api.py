import os
import random
import sys
from typing import Sequence, Mapping, Any, Union
import torch
import argparse

# Add the ComfyUI directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir,os.pardir))
comfyui_path = os.path.abspath(os.path.join(current_dir, parent_dir, 'ComfyUI'))
if comfyui_path not in sys.path:
    sys.path.append(comfyui_path)


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
    """
    initializes the PromptServer,
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




def process_image_with_comfy(input_image_path, output_image_path, selected_color):
    import_custom_nodes()
    from nodes import (
    CLIPTextEncode,
    VAEDecode,
    CheckpointLoaderSimple,
    NODE_CLASS_MAPPINGS,
    LoadImage,
    VAEEncode,
    LoraLoader,
    KSampler
    )
    
    print("Starting the image proccesing workflow...")

    with torch.inference_mode():
        checkpointloadersimple = CheckpointLoaderSimple()
        checkpointloadersimple_4 = checkpointloadersimple.load_checkpoint(
            ckpt_name="oilPainting_oilPaintingV10.safetensors"
        )

        loraloader = LoraLoader()
        loraloader_17 = loraloader.load_lora(
            lora_name="oil_painting.safetensors",
            strength_model=0.1,
            strength_clip=1,
            model=get_value_at_index(checkpointloadersimple_4, 0),
            clip=get_value_at_index(checkpointloadersimple_4, 1),
        )

        cliptextencode = CLIPTextEncode()
        cliptextencode_6 = cliptextencode.encode(
            text="impressionist oil painting",
            clip=get_value_at_index(loraloader_17, 1),
        )

        cliptextencode_7 = cliptextencode.encode(
            text="text, watermark, signatures",
            clip=get_value_at_index(loraloader_17, 1),
        )

        loadimage = LoadImage()
        loadimage_10 = loadimage.load_image(image=input_image_path)

        getimagesize = NODE_CLASS_MAPPINGS["GetImageSize+"]()
        getimagesize_60 = getimagesize.execute(
            image=get_value_at_index(loadimage_10, 0)
        )

        
        propostvignette = NODE_CLASS_MAPPINGS["ProPostVignette"]()
        propostvignette_56 = None
        
        if(selected_color != "none"):
            bg_color_image_path = 'static/bg_colors'

            # Get the background color image path
            bg_color = os.path.abspath(
                bg_color_image_path + "/" + selected_color + '.png')

            
            loadimage_59 = loadimage.load_image(image=bg_color)
            print("Background Image loaded successfully!" + bg_color)
            imageresize = NODE_CLASS_MAPPINGS["ImageResize+"]()
            imageresize_65 = imageresize.execute(
                width=get_value_at_index(getimagesize_60, 0),
                height=get_value_at_index(getimagesize_60, 1),
                interpolation="nearest",
                keep_proportion=False,
                condition="always",
                multiple_of=0,
                image=get_value_at_index(loadimage_59, 0),
            )

            midas_depthmappreprocessor = NODE_CLASS_MAPPINGS["MiDaS-DepthMapPreprocessor"]()
            midas_depthmappreprocessor_44 = midas_depthmappreprocessor.execute(
                a=6.28,
                bg_threshold=0.1,
                resolution=512,
                image=get_value_at_index(loadimage_10, 0),
            )

            previewbridge = NODE_CLASS_MAPPINGS["PreviewBridge"]()
            previewbridge_43 = previewbridge.doit(
                image="$43-0",
                images=get_value_at_index(midas_depthmappreprocessor_44, 0),
                unique_id=14896410112531593664,
            )

            imagetomask = NODE_CLASS_MAPPINGS["ImageToMask"]()
            imagetomask_37 = imagetomask.image_to_mask(
                channel="red", image=get_value_at_index(previewbridge_43, 0)
            )

            imagecompositemasked = NODE_CLASS_MAPPINGS["ImageCompositeMasked"]()
            imagecompositemasked_48 = imagecompositemasked.composite(
                x=0,
                y=0,
                resize_source=False,
                destination=get_value_at_index(imageresize_65, 0),
                source=get_value_at_index(loadimage_10, 0),
                mask=get_value_at_index(imagetomask_37, 0),
            )

            propostvignette_56 = propostvignette.vignette_image(
                intensity=0.2,
                center_x=0.5,
                center_y=0.5,
                image=get_value_at_index(imagecompositemasked_48, 0),
            )
            
        else:
                propostvignette_56 = propostvignette.vignette_image(
                intensity=0.2,
                center_x=0.5,
                center_y=0.5,
                image=get_value_at_index(loadimage_10, 0),
            )

        vaeencode = VAEEncode()
        vaeencode_11 = vaeencode.encode(
            pixels=get_value_at_index(propostvignette_56, 0),
            vae=get_value_at_index(checkpointloadersimple_4, 2),
        )

        ksampler = KSampler()
        vaedecode = VAEDecode()
        image_save = NODE_CLASS_MAPPINGS["Image Save"]()

        for q in range(1):
            ksampler_3 = ksampler.sample(
                seed=random.randint(1, 2**64),
                steps=20,
                cfg=8,
                sampler_name="euler",
                scheduler="simple",
                denoise=0.18,
                model=get_value_at_index(loraloader_17, 0),
                positive=get_value_at_index(cliptextencode_6, 0),
                negative=get_value_at_index(cliptextencode_7, 0),
                latent_image=get_value_at_index(vaeencode_11, 0),
            )

            vaedecode_8 = vaedecode.decode(
                samples=get_value_at_index(ksampler_3, 0),
                vae=get_value_at_index(checkpointloadersimple_4, 2),
            )
            
            print("Saving image...")


            image_save_36 = image_save.was_save_images(
                output_path=output_image_path,
                filename_prefix="SERVER",
                filename_delimiter="_",
                filename_number_padding=4,
                filename_number_start="false",
                extension="png",
                quality=100,
                lossless_webp="false",
                overwrite_mode="true",
                show_history="false",
                show_history_by_prefix="true",
                embed_workflow="true",
                show_previews="true",
                images=get_value_at_index(vaedecode_8, 0),
            )
            print("Image saved successfully! %s" + (output_image_path +str(image_save_36['ui']['images'][0]['filename'])))
    return output_image_path + f"/{str(image_save_36['ui']['images'][0]['filename'])}"


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Image Processing Workflow")
    parser.add_argument("-i", "--input_image_path", type=str, help="Path to the input image file")
    parser.add_argument("-o", "--output_image_path", type=str, help="Path to save the output image file")
    args = parser.parse_args()

    process_image_with_comfy(args.input_image_path, args.output_image_path)