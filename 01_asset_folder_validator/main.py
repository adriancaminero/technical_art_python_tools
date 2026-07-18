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
    
    validated_folders = {}
    ignored_folders = []
    
    for folder in content:
        
        if folder not in rules:
            ignored_folders.append(folder)
            continue
        
        files = content[folder]
        valid_extension = rules[folder]
        
        validation = validate_files(files,valid_extension)
        
        validated_folders[folder]=validation
        
    return {
        "validated_folders":validated_folders,
        "ignored_folders":ignored_folders
    }

def save_json(path,data):
    
    with open(path,"w") as file:
        json.dump(data,file,indent=4)

def print_summary(report,report_path):
       
    validated_folders = report["validated_folders"]   
    ignored_folders = report["ignored_folders"]
    
    print("Asset Folder Validator")
    print("")
    print("Validated folders:")
    
    for folder in validated_folders:
        folder_report = validated_folders[folder]
        
        print(f"Folder Name: {folder}")
        print(f"Total valid: {folder_report['total_valid']}")
        print(f"Total review: {folder_report["total_review"]}")
        print("")
        
    print("")
    print("Ignored Folders: ")
    
    for folder in ignored_folders:
        
        print(folder)
        print("")
        
    print("")
    print("Report saved in:")
    print(report_path)   
    
def main():
    
    base_path = os.path.dirname(__file__)       #Get the script folder
    
    sample_project_path = os.path.join(base_path,"sample_project") # Built projects and output path
    output_path = os.path.join(base_path,"output")
    report_path = os.path.join(output_path,"report.json")
    
    os.makedirs(output_path, exist_ok=True)
    
    content = read_project_folders(sample_project_path) # Read project folders
    
    report = generate_report(content,rules) # Generate the validation report
    
    save_json(report_path,report) # Save the report as JSON
        
    print_summary(report,report_path)
   

        


if __name__ == "__main__": 
   main()
    

