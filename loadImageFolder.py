import os
import hashlib
import numpy as np
import torch
from PIL import Image, ImageOps, ImageSequence
import folder_paths
import node_helpers

class LoadImageFolder:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "folder_path": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Enter folder path..."
                }),
            },
        }

    CATEGORY = "image"

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "load_images_from_folder"
    
    def load_images_from_folder(self, folder_path):
        # Get all files from the folder
        files = []
        for f in os.listdir(folder_path):
            file_path = os.path.join(folder_path, f)
            if os.path.isfile(file_path):
                files.append(f)
        
        # Filter for image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp']
        image_files = [f for f in files if f.lower().endswith(tuple(image_extensions))]
        
        # Sort files for consistent ordering
        image_files.sort()
        
        all_output_images = []
        all_output_masks = []
        
        for image_file in image_files:
            image_path = os.path.join(folder_path, image_file)
            
            try:
                img = node_helpers.pillow(Image.open, image_path)
                
                output_images = []
                output_masks = []
                w, h = None, None
                
                excluded_formats = ['MPO']
                
                for i in ImageSequence.Iterator(img):
                    i = node_helpers.pillow(ImageOps.exif_transpose, i)
                    
                    if i.mode == 'I':
                        i = i.point(lambda i: i * (1 / 255))
                    image = i.convert("RGB")
                    
                    if len(output_images) == 0:
                        w = image.size[0]
                        h = image.size[1]
                    
                    if image.size[0] != w or image.size[1] != h:
                        continue
                    
                    image = np.array(image).astype(np.float32) / 255.0
                    image = torch.from_numpy(image)[None,]
                    
                    if 'A' in i.getbands():
                        mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                        mask = 1. - torch.from_numpy(mask)
                    elif i.mode == 'P' and 'transparency' in i.info:
                        mask = np.array(i.convert('RGBA').getchannel('A')).astype(np.float32) / 255.0
                        mask = 1. - torch.from_numpy(mask)
                    else:
                        mask = torch.zeros((image.shape[1], image.shape[2]), dtype=torch.float32, device="cpu")
                    
                    output_images.append(image)
                    output_masks.append(mask.unsqueeze(0))
                
                if len(output_images) > 1 and img.format not in excluded_formats:
                    folder_image = torch.cat(output_images, dim=0)
                    folder_mask = torch.cat(output_masks, dim=0)
                else:
                    folder_image = output_images[0]
                    folder_mask = output_masks[0]
                
                all_output_images.append(folder_image)
                all_output_masks.append(folder_mask)
                
            except Exception as e:
                print(f"Error loading image {image_file}: {e}")
                continue
        
        if not all_output_images:
            # Return empty tensors if no images loaded, similar to how LoadImage might handle errors
            empty_image = torch.zeros((1, 64, 64, 3), dtype=torch.float32, device="cpu")
            empty_mask = torch.zeros((1, 64, 64), dtype=torch.float32, device="cpu")
            return (empty_image, empty_mask)
        
        # Concatenate all images from the folder
        if len(all_output_images) > 1:
            final_image = torch.cat(all_output_images, dim=0)
            final_mask = torch.cat(all_output_masks, dim=0)
        else:
            final_image = all_output_images[0]
            final_mask = all_output_masks[0]
        
        return (final_image, final_mask)

    @classmethod
    def IS_CHANGED(s, folder_path):
        if not folder_path or not os.path.exists(folder_path):
            return "invalid_path"
        
        m = hashlib.sha256()
        
        # Hash the folder path
        m.update(folder_path.encode())
        
        # Get all image files and their modification times
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp']
        image_files = []
        
        try:
            for f in os.listdir(folder_path):
                file_path = os.path.join(folder_path, f)
                if os.path.isfile(file_path) and any(f.lower().endswith(ext) for ext in image_extensions):
                    image_files.append(file_path)
        except OSError:
            return "error_reading_folder"
        
        # Sort for consistent hashing
        image_files.sort()
        
        # Hash file paths and modification times
        for file_path in image_files:
            try:
                stat = os.stat(file_path)
                m.update(file_path.encode())
                m.update(str(stat.st_mtime).encode())
                m.update(str(stat.st_size).encode())
            except OSError:
                continue
        
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(s, folder_path):
        if not folder_path:
            return "Folder path cannot be empty"
        
        if not os.path.exists(folder_path):
            return f"Folder path does not exist: {folder_path}"
        
        if not os.path.isdir(folder_path):
            return f"Path is not a directory: {folder_path}"
        
        # Check if folder contains any image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp']
        has_images = False
        
        try:
            for f in os.listdir(folder_path):
                file_path = os.path.join(folder_path, f)
                if os.path.isfile(file_path) and f.lower().endswith(tuple(image_extensions)):
                    has_images = True
                    break
        except OSError:
            return f"Cannot read folder: {folder_path}"
        
        if not has_images:
            return f"No image files found in folder: {folder_path}"
        
        return True

# A dictionary that contains all nodes you want to export with their names
NODE_CLASS_MAPPINGS = {
    "LoadImageFolder": LoadImageFolder
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadImageFolder": "Load Image Folder"
}