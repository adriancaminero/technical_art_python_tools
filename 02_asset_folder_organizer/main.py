import os
import json

def list_files(path):
    
    files = os.listdir(path)
    
    return files

def save_json(path,data):
    
    with open(path,"w") as file:
        json.dump(data,file,indent=4)
        
def detect_file_type(file_name):
    
    name, extension = os.path.splitext(file_name)
    
    extension = extension.lower()
    
    if extension==".fbx":
        return "mesh"
    
    if extension in (".png", ".jpg", ".jpeg", ".tga"):
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
    
    return{
        "summary":{
        "total_files":len(meshes)+len(textures)+len(other),
        "total_meshes":len(meshes),
        "total_textures":len(textures),
        "total_other":len(other),
        },
        "classified_files":{
            "mesh":meshes,
            "texture":textures,
            "other":other            
        }
    }
    
        

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