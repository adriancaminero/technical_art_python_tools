import bpy
import os
import json
from datetime import datetime
from mathutils import Vector


PENDING_IMPORTS_FILE_NAME = "_pending_imports.json"

EXPORT_ROOT_FOLDER = r"C:\Users\adric\OneDrive\Escritorio\Python\blender_ta_tools\Test_export"

UNREAL_DESTINATION_ROOT = "/Game/BlenderExports"

EXPORT_FROM_WORLD_ORIGIN = True

def get_mesh_objects(objects):
    
    mesh = []
    
    for obj in objects:
        if obj.type == "MESH":
            mesh.append(obj)
            
    return mesh

def is_close(value, target, tolerance=0.001):
    return abs(value - target) <= tolerance


def is_vector_close(vector, target, tolerance=0.001):
    return (
        is_close(vector[0], target[0], tolerance) and
        is_close(vector[1], target[1], tolerance) and
        is_close(vector[2], target[2], tolerance)
    )


def create_issue(code, message, fixable=False, severity="warning"):
    return {
        "code": code,
        "message": message,
        "fixable": fixable,
        "severity": severity
    }


def is_pivot_bottom_center(obj, tolerance=0.01):
    if obj.type != "MESH":
        return False

    x_values = []
    y_values = []
    z_values = []

    for corner in obj.bound_box:
        x_values.append(corner[0])
        y_values.append(corner[1])
        z_values.append(corner[2])

    min_x = min(x_values)
    max_x = max(x_values)

    min_y = min(y_values)
    max_y = max(y_values)

    min_z = min(z_values)

    bottom_center_x = (min_x + max_x) / 2
    bottom_center_y = (min_y + max_y) / 2
    bottom_center_z = min_z

    return (
        is_close(bottom_center_x, 0.0, tolerance) and
        is_close(bottom_center_y, 0.0, tolerance) and
        is_close(bottom_center_z, 0.0, tolerance)
    )

def get_bottom_center_world(obj):
    world_corners = []

    for corner in obj.bound_box:
        world_corner = obj.matrix_world @ Vector(corner)
        world_corners.append(world_corner)

    min_x = min(corner.x for corner in world_corners)
    max_x = max(corner.x for corner in world_corners)

    min_y = min(corner.y for corner in world_corners)
    max_y = max(corner.y for corner in world_corners)

    min_z = min(corner.z for corner in world_corners)

    bottom_center = Vector((
        (min_x + max_x) / 2,
        (min_y + max_y) / 2,
        min_z
    ))

    return bottom_center

def set_pivot_to_bottom_center(obj):
    if obj.type != "MESH":
        return False

    bottom_center = get_bottom_center_world(obj)

    old_cursor_location = bpy.context.scene.cursor.location.copy()

    bpy.ops.object.select_all(action="DESELECT")

    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.context.scene.cursor.location = bottom_center

    bpy.ops.object.origin_set(
        type="ORIGIN_CURSOR",
        center="MEDIAN"
    )

    bpy.context.scene.cursor.location = old_cursor_location

    print(f"Set pivot to bottom center: {obj.name}")

    return True

def validate_object(obj):
    issues = []
    scene = bpy.context.scene
    
    if not obj.name.startswith("SM_"):
        issues.append(create_issue(
            "invalid_name",
            "Name should start with SM_",
            True,
            "warning"
        ))

    if not is_vector_close(obj.scale, (1.0, 1.0, 1.0)):
        issues.append(create_issue(
            "scale_not_applied",
            "Scale is not applied",
            True,
            "warning"
        ))

    if not is_vector_close(obj.rotation_euler, (0.0, 0.0, 0.0)):
        issues.append(create_issue(
            "rotation_not_applied",
            "Rotation is not applied",
            True,
            "warning"
        ))

    if obj.type != "MESH":
        issues.append(create_issue(
            "not_mesh",
            "Object is not a mesh",
            False,
            "error"
        ))

    else:
        if len(obj.material_slots) == 0:
            issues.append(create_issue(
                "missing_materials",
                "Object has no materials",
                False,
                "warning"
            ))

        if len(obj.data.uv_layers) == 0:
            issues.append(create_issue(
                "missing_uvs",
                "Object has no UV maps",
                False,
                "warning"
            ))

        if scene.ta_validate_pivot_bottom_center:
            if not is_pivot_bottom_center(obj):
                issues.append(create_issue(
                    "pivot_not_bottom_center",
                    "Pivot is not at bottom center",
                    False,
                    "warning"
                ))

    if len(issues) == 0:
        status = "OK"
    else:
        status = "NEEDS_REVIEW"

    return {
        "object_name": obj.name,
        "object_type": obj.type,
        "scale": list(obj.scale),
        "rotation": list(obj.rotation_euler),
        "dimensions": list(obj.dimensions),
        "status": status,
        "issues": issues
    }


def apply_scale_rotation(obj):
    bpy.ops.object.select_all(action="DESELECT")

    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.transform_apply(
        location=False,
        rotation=True,
        scale=True
    )


def fix_mesh_name(obj):
    if obj.type != "MESH":
        return False

    if obj.name.startswith("SM_"):
        return False

    old_name = obj.name
    new_name = "SM_" + old_name

    obj.name = new_name
    obj.data.name = new_name

    print(f"Renamed {old_name} to {new_name}")

    return True

def apply_normal_mode(obj, normal_mode):
    if obj.type != "MESH":
        return False

    if normal_mode == "KEEP":
        return False

    if normal_mode == "FLAT":
        for polygon in obj.data.polygons:
            polygon.use_smooth = False

        obj.data.update()
        print(f"Applied shade flat normals: {obj.name}")
        return True

    if normal_mode == "SMOOTH":
        for polygon in obj.data.polygons:
            polygon.use_smooth = True

        obj.data.update()
        print(f"Applied shade smooth normals: {obj.name}")
        return True

    if normal_mode == "WEIGHTED":
        for polygon in obj.data.polygons:
            polygon.use_smooth = True

        modifier = obj.modifiers.get("TA_Weighted_Normals")

        if modifier is None:
            modifier = obj.modifiers.new(
                name="TA_Weighted_Normals",
                type="WEIGHTED_NORMAL"
            )

        modifier.keep_sharp = True
        modifier.weight = 50

        obj.data.update()
        print(f"Applied weighted normals: {obj.name}")
        return True

    return False

def store_object_location(objects):
    
    saved_locations = []
    
    for obj in objects:
        saved_locations.append((obj, obj.location.copy()))
    
    return saved_locations

def restore_location(saved_locations):
    
    for obj,location in saved_locations:
        
        obj.location = location
        
def move_export_group_to_world_origin(objects, anchor_obj):
    mesh_objects = get_mesh_objects(objects)
    
    if len(mesh_objects)==0:
        return []

    saved_locations = store_object_location(mesh_objects)
    offset = anchor_obj.location.copy()
    
    for obj in mesh_objects:
        
        obj.location -= offset
        
    return saved_locations
    
    
def save_validation_report(objects, export_folder, file_name):
    report = []

    for obj in objects:
        result = validate_object(obj)
        report.append(result)

    os.makedirs(export_folder, exist_ok=True)

    report_path = os.path.join(export_folder, file_name)

    with open(report_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("Validation report saved:")
    print(report_path)

    return report_path

def load_pending_imports(queue_path):
    if not os.path.exists(queue_path):
        return {
            "pending_manifests": []
        }

    with open(queue_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if "pending_manifests" not in data:
        data["pending_manifests"] = []

    return data


def save_pending_imports(queue_path, data):
    os.makedirs(os.path.dirname(queue_path), exist_ok=True)

    with open(queue_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    print("Pending imports queue saved:")
    print(queue_path)


def add_manifest_to_pending_queue(manifest_path, export_root_folder):
    queue_path = os.path.join(export_root_folder, PENDING_IMPORTS_FILE_NAME)

    manifest_path = os.path.abspath(manifest_path)

    data = load_pending_imports(queue_path)

    pending_manifests = data["pending_manifests"]


    if manifest_path in pending_manifests:
        pending_manifests.remove(manifest_path)

    pending_manifests.append(manifest_path)

    data["last_updated"] = datetime.now().isoformat(timespec="seconds")

    save_pending_imports(queue_path, data)

    print("Added manifest to pending queue:")
    print(manifest_path)

def save_unreal_manifest(asset_name,objects,export_folder,fbx_file_name,validation_report_name,unreal_destination_root):
    mesh_objects = []

    for obj in objects:
        if obj.type == "MESH":
            mesh_objects.append(obj.name)

    fbx_path = os.path.join(export_folder, fbx_file_name)
    validation_report_path = os.path.join(export_folder, validation_report_name)

    manifest = {
        "asset_name": asset_name,
        "source_software": "Blender",
        "target_software": "Unreal Engine",
        "export_type": "FBX",
        "fbx_file": fbx_file_name,
        "fbx_path": os.path.abspath(fbx_path),
        "validation_report": validation_report_name,
        "validation_report_path": os.path.abspath(validation_report_path),
        "unreal_destination_path": unreal_destination_root + "/" + asset_name,
        "objects": mesh_objects
    }

    manifest_file_name = asset_name + "_manifest.json"
    manifest_path = os.path.join(export_folder, manifest_file_name)

    with open(manifest_path, "w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=4)

    print("Unreal manifest saved:")
    print(manifest_path)

    return manifest_path


def export_selected_to_fbx(objects, export_folder, file_name):
    mesh_objects = []

    for obj in objects:
        if obj.type == "MESH":
            mesh_objects.append(obj)

    if len(mesh_objects) == 0:
        print("No mesh objects selected. Export cancelled.")
        return False

    os.makedirs(export_folder, exist_ok=True)

    export_path = os.path.join(export_folder, file_name)

    bpy.ops.object.select_all(action="DESELECT")

    for obj in mesh_objects:
        obj.select_set(True)

    bpy.context.view_layer.objects.active = mesh_objects[0]

    bpy.ops.export_scene.fbx(
        filepath=export_path,
        use_selection=True,
        object_types={"MESH"},
        apply_unit_scale=True,
        bake_space_transform=False,
        bake_anim=False,
        use_mesh_modifiers=True,
        mesh_smooth_type="FACE",
        use_tspace=True
    )

    print("Exported FBX:")
    print(export_path)

    return True


def get_export_asset_name(objects):
    active_obj = bpy.context.active_object

    if active_obj in objects and active_obj.type == "MESH":
        return active_obj.name

    for obj in objects:
        if obj.type == "MESH":
            return obj.name

    return None


def run_export_package():
    scene = bpy.context.scene
    selected_objects = list(bpy.context.selected_objects)

    export_root_folder = scene.ta_export_root_folder.strip()
    unreal_destination_root = scene.ta_unreal_destination_root.strip()

    if export_root_folder == "":
        print("Export folder is empty. Export cancelled.")
        return

    if unreal_destination_root == "":
        unreal_destination_root = "/Game/BlenderExports"

    print("---- VALIDATION BEFORE FIX ----")

    for obj in selected_objects:
        result = validate_object(obj)
        print(result)

    print("---- APPLYING FIXES ----")

    for obj in selected_objects:
        result = validate_object(obj)

        needs_transform_fix = False
        needs_name_fix = False

        for issue in result["issues"]:
            if issue["code"] == "scale_not_applied" or issue["code"] == "rotation_not_applied":
                needs_transform_fix = True

            if issue["code"] == "invalid_name":
                needs_name_fix = True

        if obj.type != "MESH":
            print(f"Skipped, not a mesh: {obj.name}")

        else:
            if needs_name_fix and scene.ta_auto_fix_name:
                fix_mesh_name(obj)

            if scene.ta_normal_mode != "KEEP":
                apply_normal_mode(obj, scene.ta_normal_mode)
            
            if needs_transform_fix and scene.ta_auto_fix_transforms:
                print(f"Applying scale/rotation to: {obj.name}")
                apply_scale_rotation(obj)

            if scene.ta_set_pivot_bottom_center:
                set_pivot_to_bottom_center(obj)

            if not needs_name_fix and not needs_transform_fix and not scene.ta_set_pivot_bottom_center:
                print(f"No automatic fix needed: {obj.name}")

    print("---- VALIDATION AFTER FIX ----")

    for obj in selected_objects:
        result = validate_object(obj)
        print(result)

    print("---- EXPORT PACKAGE ----")

    asset_name = get_export_asset_name(selected_objects)

    if asset_name is None:
        print("No mesh object found. Export cancelled.")
        return

    asset_export_folder = os.path.join(export_root_folder, asset_name)

    fbx_file_name = asset_name + ".fbx"
    report_file_name = asset_name + "_validation_report.json"

    export_success = False
    saved_locations = None

    if scene.ta_export_fbx:
        try:
            if scene.ta_export_from_world_origin:
                anchor_obj = bpy.context.active_object

                if anchor_obj is None or anchor_obj.type != "MESH":
                    anchor_obj = get_mesh_objects(selected_objects)[0]

                saved_locations = move_export_group_to_world_origin(
                    selected_objects,
                    anchor_obj
                )

            export_success = export_selected_to_fbx(
                selected_objects,
                asset_export_folder,
                fbx_file_name
            )

        finally:
            if saved_locations is not None:
                restore_location(saved_locations)

    else:
        print("FBX export disabled.")

    if scene.ta_save_validation_report:
        print("---- SAVE VALIDATION REPORT ----")

        save_validation_report(
            selected_objects,
            asset_export_folder,
            report_file_name
        )

    if scene.ta_save_unreal_manifest:
        if export_success:
            print("---- SAVE UNREAL MANIFEST ----")

            manifest_path = save_unreal_manifest(
                asset_name,
                selected_objects,
                asset_export_folder,
                fbx_file_name,
                report_file_name,
                unreal_destination_root
            )
            
            add_manifest_to_pending_queue(manifest_path,export_root_folder)
        else:
            print("Manifest skipped because FBX export did not run successfully.")

class TA_OT_export_package(bpy.types.Operator):
    bl_idname = "ta.export_package"
    bl_label = "Validate / Fix / Export Package"
    bl_description = "Validate selected objects, apply safe fixes, export FBX, save report and manifest"

    def execute(self, context):
        run_export_package()
        self.report({"INFO"}, "Export package finished")
        return {"FINISHED"}


class TA_PT_unreal_export_prep_panel(bpy.types.Panel):
    bl_label = "TA Unreal Export Prep"
    bl_idname = "TA_PT_unreal_export_prep_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "TA Tools"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.label(text="Blender to Unreal")
        
        layout.separator()
        
        layout.label(text="Options")
        layout.prop(scene,"ta_auto_fix_name")
        layout.prop(scene, "ta_auto_fix_transforms")

        layout.prop(scene, "ta_normal_mode")
        layout.prop(scene, "ta_set_pivot_bottom_center")

        layout.prop(scene, "ta_export_from_world_origin")
        layout.prop(scene, "ta_validate_pivot_bottom_center")
        layout.prop(scene, "ta_export_fbx")
        layout.prop(scene, "ta_save_validation_report")
        layout.prop(scene, "ta_save_unreal_manifest")
        
        
        
        layout.label(text="Paths")
        layout.prop(scene, "ta_export_root_folder")
        layout.prop(scene, "ta_unreal_destination_root")

        layout.separator()

        layout.separator()
        layout.operator("ta.export_package")
        


def register_properties():
    bpy.types.Scene.ta_auto_fix_name = bpy.props.BoolProperty(
        name="Auto Fix Name",
        description="Automatically add SM_ prefix to mesh objects",
        default=True
    )

    bpy.types.Scene.ta_auto_fix_transforms = bpy.props.BoolProperty(
        name="Auto Fix Transforms",
        description="Automatically apply scale and rotation",
        default=True
    )

    bpy.types.Scene.ta_validate_pivot_bottom_center = bpy.props.BoolProperty(
        name="Validate Bottom Center Pivot",
        description="Warn if the pivot is not at the bottom center of the mesh",
        default=True
    )
    bpy.types.Scene.ta_set_pivot_bottom_center = bpy.props.BoolProperty(
        name="Set Pivot Bottom Center",
        description="Move the object origin to the bottom center of the mesh",
        default=False
    )
    bpy.types.Scene.ta_export_fbx = bpy.props.BoolProperty(
        name="Export FBX",
        description="Export selected mesh objects to FBX",
        default=True
    )

    bpy.types.Scene.ta_save_validation_report = bpy.props.BoolProperty(
        name="Save Validation Report",
        description="Save validation report as JSON",
        default=True
    )

    bpy.types.Scene.ta_save_unreal_manifest = bpy.props.BoolProperty(
        name="Save Unreal Manifest",
        description="Save Unreal import manifest as JSON",
        default=True
    )
    bpy.types.Scene.ta_export_from_world_origin = bpy.props.BoolProperty(
        name = "Export From World Origin",
        description = "Temporarily move selected mesh objects to world origin before exporting, then restore their original positions",
        default = True
    )
    
    bpy.types.Scene.ta_export_root_folder = bpy.props.StringProperty(
        name = "Export Folder",
        description = "Root folder where FBX packahes will be exported",
        default = EXPORT_ROOT_FOLDER,
        subtype = "DIR_PATH"
    )
    
    bpy.types.Scene.ta_unreal_destination_root = bpy.props.StringProperty(
        name="Unreal Destination",
        description="Unreal Content Browser path, for example /Game/BlenderExports",
        default=UNREAL_DESTINATION_ROOT
    )
    
    bpy.types.Scene.ta_normal_mode = bpy.props.EnumProperty(
    name="Normal Mode",
    description="Choose how normals should be prepared before export",
    items=[
        ("KEEP", "Keep Current", "Do not modify normals"),
        ("FLAT", "Shade Flat", "Use flat normals for hard edges"),
        ("SMOOTH", "Shade Smooth", "Smooth all faces"),
        ("WEIGHTED", "Weighted Normals", "Smooth faces and add a weighted normal modifier")
    ],
    default="KEEP"
)

def unregister_properties():
    del bpy.types.Scene.ta_auto_fix_name
    del bpy.types.Scene.ta_auto_fix_transforms
    del bpy.types.Scene.ta_validate_pivot_bottom_center
    del bpy.types.Scene.ta_export_fbx
    del bpy.types.Scene.ta_save_validation_report
    del bpy.types.Scene.ta_save_unreal_manifest
    del bpy.types.Scene.ta_export_from_world_origin    
    del bpy.types.Scene.ta_set_pivot_bottom_center
    del bpy.types.Scene.ta_export_root_folder
    del bpy.types.Scene.ta_unreal_destination_root
    del bpy.types.Scene.ta_normal_mode

def register():
    register_properties()
    
    bpy.utils.register_class(TA_OT_export_package)
    bpy.utils.register_class(TA_PT_unreal_export_prep_panel)


def unregister():
    bpy.utils.unregister_class(TA_PT_unreal_export_prep_panel)
    bpy.utils.unregister_class(TA_OT_export_package)
    unregister_properties()

register()