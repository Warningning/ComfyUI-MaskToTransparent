# ComfyUI-MaskToTransparent

A simple mask-based transparency tool for ComfyUI. Turns black mask areas into fully transparent pixels while preserving white areas, with edge feathering support. Perfect for object extraction after semantic segmentation with SAM 3.1 models.

✨ Features
✅ Automatically makes black mask areas transparent, preserves original image in white areas
✅ Customizable Gaussian edge feathering to remove jagged edges
✅ Supports preserving or overwriting original alpha channel
✅ Fully compatible with RGB & RGBA images
✅ Ideal for extracting segmented objects after using SAM 3.1 models, removing unwanted background pixels

📥 Installation
Go to the custom_nodes folder in your ComfyUI directory
Run the command:git clone https://github.com/Warningning/ComfyUI-MaskToTransparent.git