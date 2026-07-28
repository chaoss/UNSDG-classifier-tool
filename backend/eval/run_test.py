import csv 
import requests
import time
import os

server = "http://127.0.0.1:5000/api/classify_st_url"

print("get the tool")


completed_projects = set()

if os.path.exists("final_test_results.csv"):
    with open("final_test_results.csv", "r", encoding="utf-8") as existing_file:
        existing_reader = csv.DictReader(existing_file)
        for row in existing_reader:
            completed_projects.add(row["name"])

            

mode = "a" if len(completed_projects) > 0 else "w"

with open("dpgs.csv", "r", encoding="utf-8") as infile, \
     open("final_test_results.csv", mode, newline="", encoding="utf-8") as outfile:
    
    reader = csv.DictReader(infile)
    
    # Setup headers
    fieldnames = reader.fieldnames.copy()
    for i in range(1, 18):
        fieldnames.append(f"pred_sdg{i}")
        
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    
    # Only write the header if we are starting fresh
    if mode == "w":
        writer.writeheader()

    # 3. The Main Loop
    for i, row in enumerate(reader):
        project_name = row['name']
        
        # --- NEW: Skip if already done! ---
        if project_name in completed_projects:
            print(f"⏩ Skipping {project_name} (Already done)")
            continue
            
        print(f"reading the {i} row: {project_name}")
        payload = {
            "projectName": row['name'],
            "projectUrl": row['github_url'],
            "projectDescription": row["project_description"]
        }
        
        try:
            
            response = requests.post(server, json=payload)
            response.raise_for_status() 

            print(f"got the response for {i} row status code {response.status_code}")
            data = response.json() 
            
        except Exception as e:
            print(f"Error on {payload['projectName']}: {e}")
            continue 


        row_dict = row.copy()
        print("row_dict")
        for j in range(1, 18):
            row_dict[f"pred_sdg{j}"] = 0.0

        print("from the response get the predictions array which contains each sdg")
        predictions_array = data.get("predictions", [])
        
        for item in predictions_array:
            score = item.get("prediction", 0.0)
            sdg_data = item.get("sdg")
            
            code_num = None
            
            if isinstance(sdg_data, dict):
                print("sdg is a dictionary")
                code_str = sdg_data.get("code")
                if code_str and str(code_str).isdigit():
                    code_num = int(code_str)
                    print(f"sdg_{code_num} : {score}")
                    
        
            elif isinstance(sdg_data, str):
                print("sdg is a string")
                if "SDG" in sdg_data:
                    prefix = sdg_data.split(":")[0]
                    code_str = prefix.replace("SDG", "").strip()
                    if code_str.isdigit():
                        code_num = int(code_str)
                        print(f"sdg_{code_num} : {score}")

            
            if code_num is not None:
                row_dict[f"pred_sdg{code_num}"] = score
        
        print("writing row")
        writer.writerow(row_dict)
        print(row_dict)
        print("written row")
        
        print("pause")
        time.sleep(1.5)
        print("start again after 1.5 seconds")

print("success")
