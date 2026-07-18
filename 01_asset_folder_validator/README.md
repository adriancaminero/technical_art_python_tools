# Asset Folder Validator

A small Python tool for validating the structure of a game art asset folder.

This project was created from a common Technical Art problem: keeping asset folders clean, consistent and easy to review. When working with 3D assets, meshes, textures and support files can easily become mixed together, making the project harder to maintain and review.

The goal of this tool is to scan a sample asset project, validate files based on folder rules, and generate a JSON report with the results.

## What it does

- Reads the folders inside a sample asset project.
- Detects files inside each folder.
- Validates files based on allowed extensions.
- Separates valid files from files that need review.
- Tracks folders that do not have validation rules.
- Exports the result as a JSON report.
- Prints a readable summary in the console.

## Current validation rules

```python
rules = {
    "Meshes": (".fbx",),
    "Textures": (".png", ".jpg", ".jpeg", ".tga")
}
```

## Expected folder structure

```text
sample_project/
    Meshes/
        sm_crate_01.fbx
        wrong_texture.png

    Textures/
        t_crate_01_basecolor.png
        notes.txt

    Other/
        reference_image.psd
```

## Example output

```json
{
    "validated_folders": {
        "Meshes": {
            "valid": [
                "sm_crate_01.fbx"
            ],
            "review": [
                "wrong_texture.png"
            ],
            "total": 2,
            "total_valid": 1,
            "total_review": 1
        },
        "Textures": {
            "valid": [
                "t_crate_01_basecolor.png"
            ],
            "review": [
                "notes.txt"
            ],
            "total": 2,
            "total_valid": 1,
            "total_review": 1
        }
    },
    "ignored_folders": [
        "Other"
    ]
}
```

## How to run

From the `01_asset_folder_validator` folder, run:

```bash
python main.py
```

The tool will generate a report in:

```text
output/report.json
```

## Why this is useful

In game art and Technical Art workflows, clean folder structure and consistent asset organization are important for collaboration, debugging and pipeline automation.

This tool is a first step toward building simple pipeline tools that help artists and technical artists keep projects organized.

## Roadmap

Future improvements may include:

- Naming convention validation.
- Required texture checks.
- Mesh-to-texture matching.
- Automatic asset classification.
- Dry-run mode for safe file organization.
- Optional file moving and renaming.
- External JSON configuration for folder rules.