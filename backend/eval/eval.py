import json
import csv
import string


with open("dpgs.json", "r") as f:
    data = json.load(f)

    fieldnames = ["name", "github_url", "project_description"]
    for num in range(1, 18):
        fieldnames.append(f"act_sdg{num}") 

    with open("dpgs.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader() 
        
        project_counter = 0
        
        for project in data:
            if project_counter == 150:
                break
                
        
            desc = project["description"]
            url = project["sourceURL"]
            
            #filter out lacking repos from dpgf registry
            if not url or "github.com" not in url or len(desc.split()) < 20:
                continue
                
            
            row_dict = {
                "name": project["name"],
                "github_url": url,
                "project_description": desc
            }
            
           
            for num in range(1, 18):
                row_dict[f"act_sdg{num}"] = 0
                
            # 7. Map the Ground Truth
            actual_sdgs_list = project["sdgs"]
            for sdg_item in actual_sdgs_list:
                raw_number = sdg_item.get("number")
                if raw_number:
                    sdg_num = int(raw_number)
                    # Flip the 0 to a 1 for the specific SDG!
                    row_dict[f"act_sdg{sdg_num}"] = 1
                    
            
            writer.writerow(row_dict)
            project_counter += 1

    print("success")