# Blender to Unreal Export Prep Tool

Small Technical Art prototype to speed up asset iteration between Blender and Unreal Engine.

The idea is to export assets from Blender and import/reimport them in Unreal with fewer manual steps.

## Why I made this

When working between Blender and Unreal, I noticed that even simple asset iteration can become repetitive: fixing names, applying transforms, checking pivots, exporting FBX files and importing them again in Unreal.

I wanted to build a small tool that helps with that process and also lets me practice a more Technical Artist-style workflow: validating assets, generating reports, using JSON files, and connecting a DCC tool with a game engine.

This is still a prototype, but the goal is to make the Blender → Unreal iteration faster and less manual.


## What it does

### Blender

- validates selected mesh objects
- checks naming, transforms, UVs, materials and pivot
- can apply simple fixes
- exports FBX
- creates a validation report
- creates a JSON manifest
- adds the asset to a pending import queue

### Unreal

- reads the pending import queue
- imports new assets
- reimports existing assets
- uses a small Editor Utility Widget
- can auto-check the queue every 5 seconds

## Workflow

```text
Blender
    Validate / Fix / Export
        ↓
Export folder
    FBX
    manifest.json
    validation_report.json
    _pending_imports.json
        ↓
Unreal
    Import Pending
    or Auto Import
```

## Structure

```text
03_blender_unreal_export_prep/
    blender/
        ta_unreal_export_prep.py

    unreal/
        import_pending_blender_exports.py
        where_blender_exports_are.example.json

    docs/
        blender_export_panel.png
        unreal_import_bridge_widget.png
        
```

## Unreal setup

The Unreal script is placed inside the project, outside the `Content` folder:

```text
MyUnrealProject/
    Content/
    Config/
    Scripts/
        BlenderImportBridge/
            import_pending_blender_exports.py
            where_blender_exports_are.json
```

Example settings file:

```json
{
    "export_root_folder": "C:/Path/To/Your/Blender/Export/Folder"
}
```

## Notes

This is still a prototype, not a finished plugin.

The goal was to practice a real Technical Artist workflow using Blender Python, Unreal Python, JSON files and Editor Utility Widgets.

Next improvements could be a cleaner UI, better status messages, a Clear Queue button and an easier Unreal installation.