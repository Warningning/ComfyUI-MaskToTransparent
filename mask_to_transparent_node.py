import torch
import numpy as np
from typing import Tuple


class MaskToTransparent:
    """
    Use mask to only retain pixels in the white area and remove those in the black area (by setting pixel values to zero and making them transparent). 
    Support edge feathering to retain some transparent transition pixels. 
    Output: An RGBA image with the same size as the original image, where the white area retains the original image, the black area is completely transparent, and the edges have a gradient transition
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",), 
                "mask": ("MASK",), 
                "threshold": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "feather_radius": ("INT", {"default": 5, "min": 0, "max": 50, "step": 1}),
                "preserve_original_alpha": ("BOOLEAN", {"default": False}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "apply_mask_to_transparent"
    CATEGORY = "image/mask"
    
    def apply_mask_to_transparent(self, image: torch.Tensor, mask: torch.Tensor, 
                                  threshold: float = 0.5, feather_radius: int = 5,
                                  preserve_original_alpha: bool = False) -> Tuple[torch.Tensor]:
        device = image.device
        mask = mask.to(device)

        if len(mask.shape) == 2:
            mask = mask.unsqueeze(0)
        batch_size = image.shape[0]
        if mask.shape[0] == 1 and batch_size > 1:
            mask = mask.expand(batch_size, -1, -1)
        elif mask.shape[0] != batch_size:
            min_batch = min(mask.shape[0], batch_size)
            image = image[:min_batch]
            mask = mask[:min_batch]
            batch_size = min_batch
        
        if feather_radius > 0:
            feathered_mask = self._apply_feather(mask, feather_radius, threshold)
        else:
            feathered_mask = (mask > threshold).float()
        mask_expanded = feathered_mask.unsqueeze(-1)  # (B, H, W, 1)
        
        if image.shape[-1] == 3:
            rgb_result = image * mask_expanded
            alpha = mask_expanded
            rgba = torch.cat([rgb_result, alpha], dim=-1)
            
        elif image.shape[-1] == 4:
            rgba_result = image.clone()
            if preserve_original_alpha:
                rgba_result[..., :3] = image[..., :3] * mask_expanded
                rgba_result[..., 3:4] = image[..., 3:4] * mask_expanded
            else:
                rgba_result[..., :3] = image[..., :3] * mask_expanded
                rgba_result[..., 3:4] = mask_expanded
            rgba = rgba_result
            
        else:
            raise ValueError(f"Number of unsupported image channels: {image.shape[-1]},Expected 3 (RGB) or 4 (RGBA)")
        
        rgba = rgba.contiguous()
        return (rgba,)
    
    def _apply_feather(self, mask: torch.Tensor, radius: int, threshold: float) -> torch.Tensor:
        batch_size, height, width = mask.shape
        device = mask.device
    
        core_mask = (mask > threshold).float()

        outer_mask = (mask <= threshold).float()
        
        kernel_size = radius * 2 + 1
        sigma = radius / 3
        
        x = torch.arange(kernel_size, device=device) - radius
        gaussian_1d = torch.exp(-0.5 * (x / sigma) ** 2)
        gaussian_1d = gaussian_1d / gaussian_1d.sum()
        
        gaussian_2d = torch.outer(gaussian_1d, gaussian_1d)
        
        feathered_results = []
        
        for i in range(batch_size):
            current_mask = mask[i].unsqueeze(0).unsqueeze(0)
            padding = radius
            blurred = torch.nn.functional.conv2d(
                current_mask, 
                gaussian_2d.view(1, 1, kernel_size, kernel_size),
                padding=padding
            ).squeeze(0).squeeze(0)
            feathered = torch.where(core_mask[i] > 0.5, 
                                   torch.ones_like(blurred),
                                   blurred * outer_mask[i])
            # feathered = torch.clamp(feathered, 0, 1)
            feathered_results.append(feathered)
        
        return torch.stack(feathered_results, dim=0)