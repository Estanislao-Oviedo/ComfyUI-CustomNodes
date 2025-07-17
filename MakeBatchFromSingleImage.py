import os
import hashlib
import numpy as np
import torch
from PIL import Image, ImageOps, ImageSequence
import folder_paths
import node_helpers

class MakeBatchFromSingleImage:
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        files = folder_paths.filter_files_content_types(files, ["image"])
        return {"required":
                    {"batch_count": ("INT", {
                        "default": 1, 
                        "min": 1,
                        "max": 1000,
                        "step": 1,
                        "display": "number"
                    }),
                     "image": (sorted(files), {"image_upload": True})},
                }

    CATEGORY = "image"

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "make_batch_from_single_image"
    
    def make_batch_from_single_image(self, batch_count, image):
        image_path = folder_paths.get_annotated_filepath(image)

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
                mask = torch.zeros((64,64), dtype=torch.float32, device="cpu")
            output_images.append(image)
            output_masks.append(mask.unsqueeze(0))

        if len(output_images) > 1 and img.format not in excluded_formats:
            output_image = torch.cat(output_images, dim=0)
            output_mask = torch.cat(output_masks, dim=0)
        else:
            output_image = output_images[0]
            output_mask = output_masks[0]

        # Create batch by repeating the image batch_count times
        batch_images = []
        batch_masks = []
        
        for _ in range(batch_count):
            batch_images.append(output_image)
            batch_masks.append(output_mask)
        
        # Concatenate to create the final batch
        if batch_count > 1:
            batched_image = torch.cat(batch_images, dim=0)
            batched_mask = torch.cat(batch_masks, dim=0)
        else:
            batched_image = output_image
            batched_mask = output_mask

        return (batched_image, batched_mask)

    @classmethod
    def IS_CHANGED(s, batch_count, image):
        image_path = folder_paths.get_annotated_filepath(image)
        m = hashlib.sha256()
        with open(image_path, 'rb') as f:
            m.update(f.read())
        # Include batch_count in the hash so the node re-executes when batch count changes
        m.update(str(batch_count).encode())
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(s, batch_count, image):
        if not folder_paths.exists_annotated_filepath(image):
            return "Invalid image file: {}".format(image)
        
        if batch_count < 1:
            return "Batch count must be at least 1"
        
        if batch_count > 1000:
            return "Batch count cannot exceed 1000"

        return True

# A dictionary that contains all nodes you want to export with their names
NODE_CLASS_MAPPINGS = {
    "MakeBatchFromSingleImage": MakeBatchFromSingleImage
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "MakeBatchFromSingleImage": "Make Batch from Single Image"
}