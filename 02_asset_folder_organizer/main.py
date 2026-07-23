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
    
    suggestion = generate_suggested_structure(assets,other)
    
    actions = generate_suggested_actions(assets,other)
    
    conflicts = detect_destination_conflict(actions)
   
    
    return{
        "summary":{
        "total_files":len(meshes)+len(textures)+len(other),
        "total_meshes":len(meshes),
        "total_textures":len(textures),
        "total_other":len(other),
        "total_assets":len(assets),
        "total_suggested_actions":len(actions),
        "total_conflicts":len(conflicts)
        },
        "classified_files":{
            "mesh":meshes,
            "texture":textures,
            "other":other            
        },
        "assets":assets,
        "suggested_structure":suggestion,
        "suggested_actions":actions,
        "conflicts":conflicts
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
        
def generate_suggested_structure(assets,other_files):
    
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
    
    if len(other_files)>0:
        suggested_structure["misc"]={
            "misc_folder":"organized_assets/misc"
        }
        
        
     
    return suggested_structure
  
def generate_suggested_actions(assets,other_files):
    
    suggested_actions = []
    
    
    for asset in assets:
        asset_data = assets[asset]
        
        meshes = asset_data["meshes"]
        textures = asset_data["textures"]    
        
        for mesh in meshes:
            source_path = "sample_input/"+mesh     
            suggested_name = suggest_file_name(mesh,"mesh",asset)       
            destination_path = f"organized_assets/{asset}/meshes/{suggested_name}"
            needs_rename = suggested_name!=mesh
            
            
            suggested_actions.append({
                "action":"move",
                "file":mesh,
                "needs_rename":needs_rename,
                "suggested_name": suggested_name,
                "from":source_path,
                "to":destination_path
            })
            
        for texture in textures:
            source_path = "sample_input/"+texture   
            suggested_name = suggest_file_name(texture,"texture",asset)         
            destination_path = f"organized_assets/{asset}/textures/{suggested_name}"
            needs_rename = suggested_name!=texture
            
            suggested_actions.append({
                "action":"move",
                "file":texture,
                "needs_rename":needs_rename,
                "suggested_name": suggested_name,
                "from":source_path,
                "to":destination_path
                })
    for other_file in other_files:
            source_path = "sample_input/"+other_file   
            needs_rename = False
              
            destination_path = f"organized_assets/misc/{other_file}"
            suggested_actions.append({
                "action": "move",
                "file": other_file,
                "needs_rename":needs_rename
                "from": source_path,
                "to": destination_path
                })
            
    return suggested_actions
 
def detect_texture_map_type(file_name):
    map_types= ["basecolor",
                "normal",
                "roughness",
                "metallic",
                "ao",
                "opacity",
                "emissive"
                ]
    
    name, extension = os.path.splitext(file_name)
    
    name = name.lower()
    
    for map_type in map_types:
        if map_type in name:
            return map_type
        
    return None
           
def suggest_file_name(file_name,file_type,asset_id):
    name , extension = os.path.splitext(file_name)
    extension = extension.lower()
    if file_type ==  "mesh":
                
        suggested_name = f"sm_{asset_id}{extension}" 
        return suggested_name
    
    if file_type == "texture":
        
        map_type =detect_texture_map_type(file_name)
        if map_type==None:
            return file_name
        
        suggested_name = f"t_{asset_id}_{map_type}{extension}"
        
        return suggested_name  
    
    return file_name
  
def detect_destination_conflict(suggested_actions):
    
    destination_seen = {}
    conflicts = []
    
    for action in suggested_actions:
                
        destination_path = action["to"]
        
        if destination_path in destination_seen:
            conflicts.append({
                "destination":destination_path,
                "files":[
                    destination_seen[destination_path]["file"],
                    action["file"]
                ]
            })
        else:
            destination_seen[destination_path]=action
        
    return conflicts
      
def main():
    
    base_path = os.path.dirname(__file__)

    input_path = os.path.join(base_path,"sample_input")
    output_path = os.path.join(base_path,"output")
    report_path = os.path.join(output_path,"organizer_report.json")
    
    os.makedirs(output_path,exist_ok=True)
    
    files = list_files(input_path)
    classified_files = classify_files(files)
    assets = group_files_by_asset(classified_files)
    #print(generate_suggested_actions(assets))
    report = generate_report(classified_files)
    
    save_json(report_path,report)
    print("Organizer report generated successfully")
    print(f"Report saved in: {report_path}")
        
    
    #print(files)

 
    
if __name__ == "__main__":
    main()