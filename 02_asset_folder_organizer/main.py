import os
import json

def list_files(path):
    
    files = os.listdir(path)
    
    return files

def save_json(path,data):
    
    with open(path,"w") as file:
        json.dump(data,file,indent=4)
        
def detect_file_type(file_name):
    
    ignored_image_keywords = [
        "screenshot",
        "capture",
        "reference",
        "render",
        "preview"
            ]
    
    name, extension = os.path.splitext(file_name)
    
    extension = extension.lower()
    name = name.lower()
    
    if extension==".fbx":
        return "mesh"
    
    if extension in (".png", ".jpg", ".jpeg", ".tga"):
        for keyword in ignored_image_keywords:
            if keyword in name:
                return "other"
        
        return "texture"

    return "other"

def classify_files(files):
    
    classified_files = {
        "mesh": [],
        "texture": [],
        "other": []
    }
    
    for file_name in files:
      
        file_type = detect_file_type(file_name)
        
        classified_files[file_type].append(file_name)
                    
    return classified_files
            
def generate_report(classified_files):
    
    meshes = classified_files["mesh"]
    textures = classified_files["texture"]
    other = classified_files["other"]
    
    assets = group_files_by_asset(classified_files)
    
    suggestion = generate_suggested_structure(assets)
    
    return{
        "summary":{
        "total_files":len(meshes)+len(textures)+len(other),
        "total_meshes":len(meshes),
        "total_textures":len(textures),
        "total_other":len(other),
        "total_assets":len(assets)
        },
        "classified_files":{
            "mesh":meshes,
            "texture":textures,
            "other":other            
        },
        "assets":assets,
        "suggested_structure":suggestion
    }
    
def extract_asset_id(file_name,file_type):
    
    suffixes= ["basecolor",
            "normal",
            "roughness",
            "metallic",
            "ao",
            "opacity",
            "emissive"
            ]
    
    name, extension = os.path.splitext(file_name)
    
    name = name.lower()
    if " " in name:
                name = name.replace(" ","_")
    
    if file_type=="mesh":        
            
        if name.startswith("sm_"):
            name = name.replace("sm_","",1)
        
        
    
    if file_type=="texture":              
                  
        if name.startswith("t_"):
            name = name.replace("t_","",1)
            
        for suffix in suffixes:            
            if  name.endswith(suffix):
                name = name[:-len(suffix)]
                break 
                 
         
    name = name.strip("_- ")
    
    
    return name

def group_files_by_asset(classified_files):
    
    assets = {}
    meshes = classified_files["mesh"]
    textures = classified_files["texture"]
    
    for mesh in meshes:
        file_type = detect_file_type(mesh)
        
        mesh_id = extract_asset_id(mesh,file_type)
                
        if mesh_id not in assets:
            assets[mesh_id] = {
                "meshes": [],
                "textures": []
            }
        
        assets[mesh_id]["meshes"].append(mesh)
        
    for texture in textures:
        file_type = detect_file_type(texture)
        texture_id = extract_asset_id(texture,file_type)
        
        if texture_id not in assets:
            assets[texture_id]={
                "meshes":[],
                "textures":[]
            }
        
        assets[texture_id]["textures"].append(texture)
        
    return assets    
        
def generate_suggested_structure(assets):
    
    suggested_structure = {}
    
    for asset in assets:
        
        asset_folder = f"organized_assets/{asset}"
        mesh_folder = asset_folder+"/meshes"
        texture_folder = asset_folder+"/textures"
        
        suggested_structure[asset]={
            "asset_folder":asset_folder,
            "meshes_folder":mesh_folder,
            "textures_folder":texture_folder
        }
     
    return suggested_structure
    
def main():
    
    base_path = os.path.dirname(__file__)

    input_path = os.path.join(base_path,"sample_input")
    output_path = os.path.join(base_path,"output")
    report_path = os.path.join(output_path,"organizer_report.json")
    
    os.makedirs(output_path,exist_ok=True)
    
    files = list_files(input_path)
    classified_files = classify_files(files)
    
    
    report = generate_report(classified_files)
    
    save_json(report_path,report)
    print("Organizer report generated successfully")
    print(f"Report saved in: {report_path}")
        
    
    #print(files)

 
    
if __name__ == "__main__":
    main()