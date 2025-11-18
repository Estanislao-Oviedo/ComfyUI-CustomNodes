"""
Custom ComfyUI Nodes
"""

from .nodes.load_image_folder import LoadImageFolder
from .nodes.make_batch_from_single_image import MakeBatchFromSingleImage
from .nodes.region_conditioning_nodes import RegionConditionSpecPct, RegionConditionSpecPx, RegionConditionMerge
from .nodes.attention_couple import AttentionCouple
from .nodes.combine_video_clips import CombineVideoClips
from .nodes.seamless_join_video_clips import WanVideoVaceSeamlessJoin
import os
import nodes

# Combine all node mappings
NODE_CLASS_MAPPINGS = {
    "LoadImageFolder": LoadImageFolder,
    "MakeBatchFromSingleImage": MakeBatchFromSingleImage,
    "RegionConditionSpecPct": RegionConditionSpecPct,
    "RegionConditionSpecPx": RegionConditionSpecPx,
    "RegionConditionMerge": RegionConditionMerge,
    "AttentionCouple": AttentionCouple,
    "CombineVideoClips": CombineVideoClips,
    "WanVideoVaceSeamlessJoin": WanVideoVaceSeamlessJoin,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadImageFolder": "Load Image Folder (Custom)",
    "MakeBatchFromSingleImage": "Make Batch from Single Image (Custom)",
    "RegionConditionSpecPct": "Region Condition Spec (Percentage)",
    "RegionConditionSpecPx": "Region Condition Spec (Pixels)",
    "RegionConditionMerge": "Region Condition Merge",
    "AttentionCouple": "Attention Couple",
    "CombineVideoClips": "Combine Video Clips",
    "WanVideoVaceSeamlessJoin": "Wan Video Vace Seamless Join",
}

# Add JS extension directory for frontend
nodes.EXTENSION_WEB_DIRS["ComfyUI-CustomNodes"] = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'js')

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
