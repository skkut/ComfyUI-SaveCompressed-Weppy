# ComfyUI Save Compressed Weppy

A custom node and context menu extension for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) to save images as compressed WebP files (`.webp`) while maintaining metadata (prompt and workflow) without reaching EXIF size limits.

## Features

- **WebP Compression**: Save your generated images in WebP format with configurable quality and lossy/lossless options to save disk space.
- **Auto Metadata Extraction**: Embeds ComfyUI workflow and prompt metadata into the WebP EXIF tags (`Make` and `ImageDescription`), enabling easy drag-and-drop loading of workflows back into ComfyUI.
- **EXIF Size Limit Protection**: Automatically strips large base64-encoded binary files (such as embedded images) from the saved workflow JSON, avoiding "EXIF data too long" errors and keeping file sizes optimized.
- **UI Context Menu Integration**: Right-click on any image in the ComfyUI frontend to instantly save it using the "Save Compressed Weppy" callback via a custom HTTP backend route.

## Installation

1. Navigate to your ComfyUI custom nodes directory:
   ```bash
   cd ComfyUI/custom_nodes/
   ```
2. Clone this repository:
   ```bash
   git clone https://github.com/skkut/ComfyUI-SaveCompressed-Weppy.git
   ```
3. Restart ComfyUI.

## Node Configuration

### Save Compressed Weppy

Find this node under the `image` category.

- **`images`**: The image sequence/batch output to save.
- **`filename_prefix`**: The prefix for the saved files. Defaults to `ComfyUI_Weppy_`.
- **`quality`**: The quality parameter for WebP encoding. Range: `1` to `100` (Default: `80`). Higher means better quality and larger file size.
- **`lossless`**: If `True`, saves the image using lossless WebP encoding (Default: `False`). Note that quality controls compression level in lossless mode.
- **`prompt` / `extra_pnginfo`**: Hidden fields that automatically capture the current execution prompt and node workflow layout.

## How it Works

1. **Saving WebP images**: The node converts standard ComfyUI images (Tensors) to PIL Images and saves them with a `.webp` extension inside the ComfyUI `output` directory.
2. **Metadata handling**:
   - If `piexif` is installed, it uses it to write EXIF metadata into the WebP file headers.
   - If `piexif` is not available, it gracefully falls back to Pillow's native EXIF writer.
3. **Preventing bloated metadata**: Before serializing the workflow JSON to write into EXIF:
   - Any base64 data URIs (e.g. `data:image/png;base64,...`) are stripped.
   - Any string longer than 10KB without spaces is stripped (typically raw base64 data from embedded files).
