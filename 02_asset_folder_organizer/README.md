# Asset Folder Organizer

A Python Technical Art tool that organizes chaotic asset folders into a cleaner production-style structure.

The tool scans an input folder, classifies files, groups them by asset, suggests a folder structure, detects conflicts, generates JSON reports, and can optionally apply the suggested organization.

---

## Version

`organizer-v0.3.0`

---

## Features

- Classifies files as `mesh`, `texture`, or `other`
- Groups meshes and textures by asset name
- Suggests cleaner naming conventions
- Generates a dry-run JSON report
- Detects destination conflicts
- Moves files safely in apply mode
- Keeps conflicting files in a review folder
- Supports interactive mode and command line arguments

---

## Supported File Types

### Meshes / Source Files

```text
.fbx
.obj
.blend
.max
.ma
.mb
.ztl
.zpr
```

### Textures / Material Sources

```text
.png
.jpg
.jpeg
.tga
.exr
.tif
.tiff
.psd
.spp
```

Images containing keywords such as `preview`, `render`, `reference`, `capture`, or `screenshot` are treated as `other`.

---

## Example Input

```text
sample_input/
    chair.fbx
    chair_basecolor.png
    chair_normal.png
    chair.max
    rock_roughness.tga
    preview_render.jpg
    invoice.pdf
```

---

## Example Output

```text
organized_assets/
    chair/
        meshes/
            sm_chair.fbx
            chair.max
        textures/
            t_chair_basecolor.png
            t_chair_normal.png

    rock/
        textures/
            t_rock_roughness.tga

    misc/
        preview_render.jpg
        invoice.pdf
```

---

## Usage

The tool can be used in two ways:

1. Interactive mode
2. Command line arguments

---

## Interactive Mode

Run:

```bash
python main.py
```

The tool will ask:

```text
Input folder [sample_input]:
Apply changes? y/N:
```

If no input folder is provided, it uses `sample_input`.

If the user does not type `y`, the tool runs in dry-run mode.

---

## Command Line Arguments

### Dry-run mode

```bash
python main.py --input sample_input
```

This generates the report but does not move files.

### Apply mode

```bash
python main.py --input sample_input --apply
```

This generates the report and applies the suggested actions.

### Help

```bash
python main.py --help
```

Shows the available command line options.

---

## Reports

### Organizer Report

```text
output/organizer_report.json
```

Includes:

- Classified files
- Detected assets
- Suggested structure
- Suggested actions
- Conflicts
- Summary

### Apply Report

```text
output/apply_report.json
```

Includes:

- Applied actions
- Skipped actions
- Total applied
- Total skipped

---

## Safety Behavior

The tool is safe by default.

- Dry-run mode does not move files
- Apply mode only runs when explicitly requested
- Existing destination files are not overwritten
- Missing source files are skipped and reported
- Conflicting files are moved to:

```text
organized_assets/_needs_review/conflicts/
```

---

## Current Limitations

- Input folders must currently exist inside the organizer project folder
- Absolute paths are not fully supported yet
- Naming rules are hardcoded
- Texture type detection is based on filename keywords
- There is no graphical interface yet

---

## Roadmap

Possible future improvements:

- Support absolute paths
- Add configurable output folder
- Add JSON configuration for naming rules
- Validate missing texture maps
- Improve report summaries
- Add a PySide interface

---

## Version History

### `organizer-v0.1.0`

Initial functional version.

Added:

- File classification
- Asset grouping
- Suggested structure
- Suggested actions
- JSON report generation
- Conflict detection
- Apply mode

### `organizer-v0.2.0`

Added interactive console settings.

Added:

- Runtime input folder selection
- Runtime apply/dry-run selection
- Input folder validation

### `organizer-v0.3.0`

Added command line argument support.

Added:

- `--input` argument
- `--apply` flag
- `--help` documentation
- Interactive mode kept as fallback

---

## Technical Focus

This tool was built as part of a Technical Art Python portfolio.

Main concepts used:

```text
os
json
shutil
argparse
sys.argv
dictionaries
lists
loops
conditionals
functions
dry-run/apply workflow
```