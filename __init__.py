"""
Custom ComfyUI Nodes
"""

from .nodes.loadImageFolder import LoadImageFolder
from .nodes.MakeBatchFromSingleImage import MakeBatchFromSingleImage

# Combine all node mappings
NODE_CLASS_MAPPINGS = {
    "LoadImageFolder": LoadImageFolder,
    "MakeBatchFromSingleImage": MakeBatchFromSingleImage,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadImageFolder": "Load Image Folder (Custom)",
    "MakeBatchFromSingleImage": "Make Batch from Single Image (Custom)",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
