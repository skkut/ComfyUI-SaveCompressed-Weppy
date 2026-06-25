from .save_compressed_weppy import SaveCompressedWeppy, strip_binary_from_workflow
import os
import json
from server import PromptServer
from aiohttp import web
import folder_paths
from PIL import Image

NODE_CLASS_MAPPINGS = {
    "SaveCompressedWeppy": SaveCompressedWeppy
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveCompressedWeppy": "Save Compressed Weppy"
}

WEB_DIRECTORY = "./web"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']

@PromptServer.instance.routes.post("/save_compressed_weppy")
async def save_compressed_weppy_endpoint(request):
    post_data = await request.json()
    filename = post_data.get("filename")
    subfolder = post_data.get("subfolder", "")
    type = post_data.get("type", "temp")
    prompt = post_data.get("prompt")
    workflow = post_data.get("workflow")
    
    image_dir = folder_paths.get_directory_by_type(type)
    if image_dir is None:
        return web.json_response({"status": "error", "message": f"Unknown type {type}"}, status=400)
    
    image_path = os.path.join(image_dir, subfolder, filename)
    if not os.path.exists(image_path):
        return web.json_response({"status": "error", "message": "Image not found"}, status=404)
        
    try:
        img = Image.open(image_path)
        exif_bytes = b""
        
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
        try:
            import piexif
            if prompt is not None:
                exif_dict["0th"][piexif.ImageIFD.Make] = ("prompt:" + json.dumps(strip_binary_from_workflow(prompt))).encode("utf-8")
            if workflow is not None:
                exif_dict["0th"][piexif.ImageIFD.ImageDescription] = ("workflow:" + json.dumps(strip_binary_from_workflow(workflow))).encode("utf-8")
            exif_bytes = piexif.dump(exif_dict)
        except ImportError:
            exif_bytes = img.getexif()
            if prompt is not None:
                exif_bytes[0x010f] = ("prompt:" + json.dumps(strip_binary_from_workflow(prompt))).encode("utf-8")
            if workflow is not None:
                exif_bytes[0x010e] = ("workflow:" + json.dumps(strip_binary_from_workflow(workflow))).encode("utf-8")

        output_dir = folder_paths.get_output_directory()
        output_prefix = "ComfyUI_Weppy_"
        full_output_folder, out_filename, counter, out_subfolder, out_filename_prefix = folder_paths.get_save_image_path(output_prefix, output_dir, img.width, img.height)
        
        file = f"{out_filename}_{counter:05}_.webp"
        full_path = os.path.join(full_output_folder, file)
        
        img.save(full_path, format="WEBP", exif=exif_bytes, quality=80, lossless=False)
        return web.json_response({"status": "success", "filename": file})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)
