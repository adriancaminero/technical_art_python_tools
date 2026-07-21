import os
import json

rules = {
    "Meshes": {
        "extensions": (".fbx",),
        "prefix": "sm_"
    },
    "Textures": {
        "extensions": (".png", ".jpg", ".jpeg", ".tga"),
        "prefix": "t_"
    }
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

def validate_files(file_list,folder_rule):
    
    valid = []
    review = []
    
    for file_name in file_list:
        
        file_report = validate_file(file_name,folder_rule)
        
        if file_report["errors"]==[]:
            
            valid.append(file_name)
        else:
            
            review.append(file_report)
            
    return{
        "valid":valid,
        "review":review,
        "total":len(file_list),
        "total_valid":len(valid),
        "total_review":len(review)
    }

def validate_file(file_name,folder_rule):
    errors = []
    
    valid_extension = folder_rule["extensions"]
    required_prefix = folder_rule["prefix"]
    
    if not file_name.endswith(valid_extension):
        errors.append("Invalid extension")

    name_errors = validate_file_name(file_name,required_prefix)
    errors.extend(name_errors)
    
    return {
        "file":file_name,
        "errors":errors
    }

def validate_file_name(file,required_prefix):
    
    errors = []
    
    name, extensions = os.path.splitext(file)
    
    if not name.startswith(required_prefix):
        errors.append("Invalid prefix")
        
    if  not name.islower():
        errors.append("File must be lowercase")
    
    if " " in name:
        errors.append("File name cannot contain spaces")
        
    return errors


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
        
        file_list = content[folder]
        folder_rule = rules[folder]
        
        
        validation = validate_files(file_list,folder_rule)
        
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
    
    base_path = os.path.dirname(__file__)       # Get the script folder
    
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
    

