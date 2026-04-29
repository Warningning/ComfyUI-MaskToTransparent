from .mask_to_transparent_node import MaskToTransparent

NODE_CLASS_MAPPINGS = {
    "MaskToTransparent": MaskToTransparent
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MaskToTransparent": "Mask to transparent background"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']