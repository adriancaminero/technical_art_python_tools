import os
import json

rules = {
    "Meshes": (".fbx",),
    "Textures": (".png", ".jpg", ".jpeg", ".tga")
}

def list_files(path):
    files = os.listdir(path)
    
    return files

def list_folders(path):
    
    folders = []
    
    elements = list_files(path)

    for element in elements:
        
        element_path = os.path.join(path,element)
        
        if os.path.isdir(element_path):
            folders.append(element)
    
    return folders    

def validate_files(files,valid_extensions):
    
    valid = []
    review = []
    
    for file in files:
        
        if file.endswith(valid_extensions):
            valid.append(file)
        else:
            review.append(file)
            
    return{
        "valid":valid,
        "review":review,
        "total":len(files),
        "total_valid":len(valid),
        "total_review":len(review)
    }

def read_project_folders(path):
    
    folders = list_folders(path)
    
    content = {}
    
    for folder in folders:
        
        folder_path = os.path.join(path,folder)
        
        files = list_files(folder_path)
        
        content[folder]=files
        
    return content
    
def generate_report(content,rules):
    
    report = {}
    
    for folder in content:
        
        if folder not in rules:
            continue
        
        files = content[folder]
        valid_extension = rules[folder]
        
        validation = validate_files(files,valid_extension)
        
        report[folder]=validation
        
    return report

def save_json(path,data):
    
    with open(path,"w") as file:
        json.dump(data,file,indent=4)
    
    
        
    
base_path = os.path.dirname(__file__)



sample_project_path = os.path.join(base_path,"sample_project")
content = read_project_folders(sample_project_path)
print(generate_report(content,rules))