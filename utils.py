import os
import sys
import subprocess
# Ensure ComfyUI is found and its path added to sys.path
def find_path(name: str, path: str = None) -> str:
    """
    Looks at the given path to find the given name.
    Returns the path as a string if found, or None otherwise.
    """
    # If no path is given, use the current working directory's parent directory
    if path is None:
        path = os.path.dirname(os.getcwd())
    
    # Check if the given directory contains the name
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
        return comfyui_path

# Execute the function to add ComfyUI to sys.path
add_comfyui_directory_to_sys_path()

# def run_comfyui_batch_file() -> None:
#     """
#     Run the 'run_nvidia_gpu.bat' file inside the ComfyUI directory.
#     """
#     comfyui_path = add_comfyui_directory_to_sys_path()
#     if comfyui_path is not None:
#         batch_file_path = os.path.join(comfyui_path, "run_nvidia_gpu.bat")
#         if os.path.isfile(batch_file_path):
#             subprocess.run(batch_file_path, shell=True)
#             print(f"'{batch_file_path}' executed.")
#         else:
#             print(f"Batch file not found: {batch_file_path}")
#     else:
#         print("ComfyUI directory not found. Could not execute the batch file.")

# run_comfyui_batch_file()