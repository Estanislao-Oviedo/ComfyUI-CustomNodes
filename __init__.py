"""
Custom ComfyUI Nodes
"""

from .nodes.LoadImageFolder import LoadImageFolder
from .nodes.MakeBatchFromSingleImage import MakeBatchFromSingleImage
from .nodes.region_conditioning_nodes import RegionConditionSpecPct, RegionConditionSpecPx, RegionConditionMerge
import os
import nodes

# Combine all node mappings
NODE_CLASS_MAPPINGS = {
    "LoadImageFolder": LoadImageFolder,
    "MakeBatchFromSingleImage": MakeBatchFromSingleImage,
    "RegionConditionSpecPct": RegionConditionSpecPct,
    "RegionConditionSpecPx": RegionConditionSpecPx,
    "RegionConditionMerge": RegionConditionMerge,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadImageFolder": "Load Image Folder (Custom)",
    "MakeBatchFromSingleImage": "Make Batch from Single Image (Custom)",
    "RegionConditionSpecPct": "Region Condition Spec (Percentage)",
    "RegionConditionSpecPx": "Region Condition Spec (Pixels)",
    "RegionConditionMerge": "Region Condition Merge",
}

# Add JS extension directory for frontend
nodes.EXTENSION_WEB_DIRS["ComfyUI-CustomNodes"] = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'js')

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
