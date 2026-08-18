import unreal
import json
import os


SETTINGS_FILE_NAME = "bridge_settings.json"
PENDING_IMPORTS_FILE_NAME = "_pending_imports.json"


def get_queue_path(export_root_folder):
    return os.path.join(export_root_folder, PENDING_IMPORTS_FILE_NAME)


def load_json(path):
    if not os.path.exists(path):
        unreal.log_error(f"JSON file not found: {path}")
        return None

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

def get_script_folder():
    return os.path.dirname(os.path.abspath(__file__))


def get_settings_path():
    return os.path.join(get_script_folder(), SETTINGS_FILE_NAME)


def load_bridge_settings():
    settings_path = get_settings_path()

    unreal.log("Reading bridge settings:")
    unreal.log(settings_path)

    if not os.path.exists(settings_path):
        unreal.log_error(f"Bridge settings file not found: {settings_path}")
        return None

    settings = load_json(settings_path)

    if settings is None:
        return None

    if "export_root_folder" not in settings:
        unreal.log_error("bridge_settings.json missing key: export_root_folder")
        return None

    export_root_folder = settings["export_root_folder"].strip()

    if export_root_folder == "":
        unreal.log_error("export_root_folder is empty in bridge_settings.json")
        return None

    if not os.path.exists(export_root_folder):
        unreal.log_error(f"Export root folder does not exist: {export_root_folder}")
        return None

    return settings

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_pending_queue(queue_path):
    if not os.path.exists(queue_path):
        unreal.log_warning(f"Pending queue not found: {queue_path}")
        return {
            "pending_manifests": []
        }

    data = load_json(queue_path)

    if data is None:
        return {
            "pending_manifests": []
        }

    if "pending_manifests" not in data:
        data["pending_manifests"] = []

    return data


def validate_manifest(manifest, manifest_path):
    required_keys = [
        "asset_name",
        "fbx_path",
        "unreal_destination_path"
    ]

    missing_keys = []

    for key in required_keys:
        if key not in manifest:
            missing_keys.append(key)

    if len(missing_keys) > 0:
        unreal.log_error(f"Manifest missing keys: {manifest_path} -> {missing_keys}")
        return False

    if not os.path.exists(manifest["fbx_path"]):
        unreal.log_error(f"FBX file not found: {manifest['fbx_path']}")
        return False

    if not manifest["unreal_destination_path"].startswith("/Game/"):
        unreal.log_error(
            f"Invalid Unreal destination path: {manifest['unreal_destination_path']}"
        )
        return False

    return True


def get_unreal_asset_path(destination_path, asset_name):
    return destination_path + "/" + asset_name + "." + asset_name


def import_fbx_to_unreal(fbx_path, destination_path, asset_name):
    unreal.EditorAssetLibrary.make_directory(destination_path)

    asset_path = get_unreal_asset_path(destination_path, asset_name)
    asset_already_exists = unreal.EditorAssetLibrary.does_asset_exist(asset_path)

    if asset_already_exists:
        unreal.log(f"Updating existing asset: {asset_path}")
    else:
        unreal.log(f"Importing new asset: {asset_path}")

    task = unreal.AssetImportTask()

    task.set_editor_property("filename", fbx_path)
    task.set_editor_property("destination_path", destination_path)
    task.set_editor_property("destination_name", asset_name)
    task.set_editor_property("automated", True)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("replace_existing_settings", False)
    task.set_editor_property("save", True)

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    asset_tools.import_asset_tasks([task])

    imported_paths = task.get_editor_property("imported_object_paths")

    if len(imported_paths) == 0:
        unreal.log_warning(f"No imported paths returned for: {asset_name}")
    else:
        unreal.log("Imported / updated paths:")
        for path in imported_paths:
            unreal.log(path)

    return imported_paths


def import_manifest(manifest_path):
    manifest = load_json(manifest_path)

    if manifest is None:
        return False

    if not validate_manifest(manifest, manifest_path):
        return False

    asset_name = manifest["asset_name"]
    fbx_path = manifest["fbx_path"]
    destination_path = manifest["unreal_destination_path"]

    unreal.log("---- IMPORTING BLENDER EXPORT ----")
    unreal.log(f"Manifest: {manifest_path}")
    unreal.log(f"Asset: {asset_name}")
    unreal.log(f"FBX: {fbx_path}")
    unreal.log(f"Destination: {destination_path}")

    imported_paths = import_fbx_to_unreal(
        fbx_path,
        destination_path,
        asset_name
    )

    return len(imported_paths) > 0


def clear_imported_manifests(queue_path, queue_data, imported_manifests):
    pending_manifests = queue_data["pending_manifests"]

    remaining_manifests = []

    for manifest_path in pending_manifests:
        if manifest_path not in imported_manifests:
            remaining_manifests.append(manifest_path)

    queue_data["pending_manifests"] = remaining_manifests

    save_json(queue_path, queue_data)

    unreal.log("Pending queue updated.")
    unreal.log(f"Remaining pending manifests: {len(remaining_manifests)}")


def run_import_pending():
    settings = load_bridge_settings()
    
    if settings is None:
        return
    
    export_root_folder = settings["export_root_folder"].strip()
    
    queue_path = get_queue_path(export_root_folder)

    unreal.log("---- READING BLENDER PENDING IMPORT QUEUE ----")
    unreal.log(queue_path)

    queue_data = load_pending_queue(queue_path)
    pending_manifests = queue_data["pending_manifests"]

    if len(pending_manifests) == 0:
        unreal.log("No pending Blender exports to import.")
        return

    imported_manifests = []

    for manifest_path in pending_manifests:
        success = import_manifest(manifest_path)

        if success:
            imported_manifests.append(manifest_path)

    clear_imported_manifests(
        queue_path,
        queue_data,
        imported_manifests
    )

    unreal.log("---- BLENDER PENDING IMPORT FINISHED ----")
    unreal.log(f"Imported manifests: {len(imported_manifests)}")


run_import_pending()