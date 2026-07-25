# Asset Folder Organizer

A Python tool for organizing chaotic 3D asset folders into a cleaner production-style structure.

This tool scans an input folder, detects different file types, groups related files by asset, suggests clean naming conventions, detects destination conflicts, and can safely apply move/rename operations while routing problematic files to a manual review folder.

## Why this tool exists

3D asset folders often become messy during production:

- meshes mixed with textures
- source files mixed with exports
- inconsistent naming
- duplicate texture maps
- screenshots, invoices, notes or references inside the same folder
- files that should not be overwritten accidentally

This tool is designed as a small Technical Art / pipeline utility to help clean and standardize those folders safely.

## Current version

`v0.1.0`

## Features

- Classifies files into:
  - `meshes`
  - `textures`
  - `misc`

- Supports common 3D and asset production files, such as:
  - `.fbx`
  - `.obj`
  - `.blend`
  - `.max`
  - ZBrush files
  - image texture formats
  - `.spp` Substance Painter files

- Detects texture map types:
  - `basecolor`
  - `normal`
  - `roughness`
  - `metallic`
  - `ao`
  - `opacity`
  - `emissive`

- Groups files by detected asset ID.

- Suggests cleaner naming for final export files:
  - `chair.fbx` → `sm_chair.fbx`
  - `chairbasecolor.png` → `t_chair_basecolor.png`

- Keeps source/project files safer:
  - `.max`, `.blend`, `.spp`, etc. are grouped correctly but not aggressively renamed.

- Detects destination conflicts before applying changes.

- Sends conflict files to:

```text
organized_assets/_needs_review/conflicts/