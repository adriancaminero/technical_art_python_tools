import unreal
import os


EXPORT_ROOT_FOLDER = r"C:\Users\adric\OneDrive\Escritorio\Python\Github\technical_art_python_tools\03_blender_unreal_export_prep\Test_export"
PENDING_IMPORTS_FILE_NAME = "_pending_imports.json"

queue_path = os.path.join(EXPORT_ROOT_FOLDER, PENDING_IMPORTS_FILE_NAME)

unreal.log("Checking pending queue path:")
unreal.log(queue_path)

if os.path.exists(queue_path):
    unreal.log("Pending queue found.")
else:
    unreal.log_error("Pending queue NOT found.")