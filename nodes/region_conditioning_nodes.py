import torch
import torch.nn.functional as F

class RegionConditionSpecPct:
    """
    Define a region spec using percentages of canvas size.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {"required":{
            'conditioning': ("CONDITIONING",),
            'x': ("FLOAT", {"default": 0.0, "min": 0.0, "max": 100.0, "step": 1.0}),
            'y': ("FLOAT", {"default": 0.0, "min": 0.0, "max": 100.0, "step": 1.0}),
            'width': ("FLOAT", {"default": 100.0, "min": 0.0, "max": 100.0, "step": 1.0}),
            'height': ("FLOAT", {"default": 100.0, "min": 0.0, "max": 100.0, "step": 1.0}),
            'strength': ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01})
        }}
    RETURN_TYPES = ("REGION_SPEC",)
    FUNCTION = "make_spec_pct"
    CATEGORY = "Region Conditioning"

    def make_spec_pct(self, conditioning, x, y, width, height, strength):
        return ({
            'conditioning': conditioning,
            'mode': 'pct',
            'x': x / 100.0, 'y': y / 100.0,
            'w': width / 100.0, 'h': height / 100.0,
            'strength': strength
        },)

class RegionConditionSpecPx:
    """
    Define a region spec using exact pixel coordinates.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {"required":{
            'conditioning': ("CONDITIONING",),
            'x': ("INT", {"default": 0, "min": 0, "max": 8192}),
            'y': ("INT", {"default": 0, "min": 0, "max": 8192}),
            'width': ("INT", {"default": 512, "min": 1, "max": 8192}),
            'height': ("INT", {"default": 512, "min": 1, "max": 8192}),
            'strength': ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01})
        }}
    RETURN_TYPES = ("REGION_SPEC",)
    FUNCTION = "make_spec_px"
    CATEGORY = "Region Conditioning"

    def make_spec_px(self, conditioning, x, y, width, height, strength):
        return ({
            'conditioning': conditioning,
            'mode': 'px',
            'x': x, 'y': y,
            'w': width, 'h': height,
            'strength': strength
        },)

class RegionConditionMerge:
    """
    Merge multiple region specs, apply masks, and combine conditionings.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                'width': ("INT", {"default": 512, "min": 64, "max": 8192}),
                'height': ("INT", {"default": 512, "min": 64, "max": 8192})
            },
            "optional": {},
        }
    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "merge_regions"
    CATEGORY = "Region Conditioning"

    def set_mask(self, conditioning, mask):
        """Apply mask to conditioning using ComfyUI's standard approach"""
        c = []
        for t in conditioning:
            n = [t[0], t[1].copy()]
            n[1]['mask'] = mask
            n[1]['set_area_to_bounds'] = False
            c.append(n)
        return c

    def combine_conditioning(self, conditioning_list):
        """Combine multiple conditionings using ComfyUI's standard approach"""
        if not conditioning_list:
            return []
        
        # Flatten and combine all conditioning sets like ConditioningCombine does
        combined = []
        for cond_set in conditioning_list:
            if isinstance(cond_set, list):
                combined.extend(cond_set)
            else:
                combined.append(cond_set)
        return combined

    def merge_regions(self, width, height, **kwargs):
        # Filter out None values and collect region specs
        specs = [v for v in kwargs.values() if v is not None]
        
        if not specs:
            # Return empty conditioning if no specs provided
            return ([],)
        
        masked = []
        for spec in specs:
            cond = spec['conditioning']
            if spec.get('mode') == 'pct':
                x0 = int(spec['x'] * width)
                y0 = int(spec['y'] * height)
                w0 = int(spec['w'] * width)
                h0 = int(spec['h'] * height)
            else:
                x0, y0, w0, h0 = spec['x'], spec['y'], spec['w'], spec['h']
                w0 = max(0, min(w0, width - x0))
                h0 = max(0, min(h0, height - y0))
            
            # Create mask tensor
            mask = torch.zeros((height, width), dtype=torch.float32)
            if w0 > 0 and h0 > 0:
                mask[y0:y0+h0, x0:x0+w0] = spec['strength']
            
            # Apply mask to conditioning
            masked_cond = self.set_mask(cond, mask)
            masked.append(masked_cond)
        
        # Combine all masked conditionings
        result = self.combine_conditioning(masked)
        return (result,)

NODE_CLASS_MAPPINGS = {
    "RegionConditionSpecPct": RegionConditionSpecPct,
    "RegionConditionSpecPx": RegionConditionSpecPx,
    "RegionConditionMerge": RegionConditionMerge,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RegionConditionSpecPct": "Region Condition Spec (Percentage)",
    "RegionConditionSpecPx": "Region Condition Spec (Pixels)",
    "RegionConditionMerge": "Region Condition Merge",
}
