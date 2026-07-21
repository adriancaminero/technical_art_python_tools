import os
import json

def list_files(path):
    
    files = os.listdir(path)
    
    return files

def save_json(path,data):
    
    with open(path,"w") as file:
        json.dump(data,file,indent=4)


def main():
    
    base_path = os.path.dirname(__file__)

    input_path = os.path.join(base_path,"sample_input")
    output_path = os.path.join(base_path,"output")
    report_path = os.path.join(output_path,"organizer_report.json")
    
    os.makedirs(output_path,exist_ok=True)
    
    files = list_files(input_path)
    print(files)
    
    
if __name__ == "__main__":
    main()