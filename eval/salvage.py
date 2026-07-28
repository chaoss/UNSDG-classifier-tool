import csv
import time
import requests
import os

target_file = "eval_subset_no_readme_cleanup_only_cos_sim.csv"
temp_file = "temp_processing_pipeline.csv"
server = "http://127.0.0.1:5000/api/classify_st_url"

with open(target_file, "r", encoding="utf-8-sig") as f:
    target_reader = csv.DictReader(f)
    target_fields = target_reader.fieldnames
    target_rows = list(target_reader)

source_rows = target_rows.copy()  
target_map = {row['github_url']: row for row in target_rows if 'github_url' in row}

print(f"Loaded {len(target_rows)} rows, fields: {target_fields[:5]}...")


print("server...")
try:
    warmup = requests.post(
        server,
        json={"projectName": "test", "projectUrl": "https://github.com/torvalds/linux", "projectDescription": "test"},
        timeout=300
    )
    print(f"Server warm: {warmup.status_code}")
except Exception as e:
    print(f"Warmup: {e}")
time.sleep(3)

# Inference loop — no files open
for source_row in source_rows:
    gh_url = source_row.get('github_url', '')
    if not gh_url or gh_url not in target_map:
        continue

    project_name = source_row.get('name', '')
    payload = {
        "projectName": project_name,
        "projectUrl": gh_url,
        "projectDescription": source_row.get("project_description", "")
    }
    print(f"Requesting: {project_name}")

    try:
        response = requests.post(server, json=payload, timeout=300)
        response.raise_for_status()
        data = response.json()
        print(f"Done: {project_name}")

        target_row = target_map[gh_url]
        for pred in data.get("predictions", []):
            sdg_prefix = pred["sdg"].split(":")[0]
            num = sdg_prefix.replace("SDG", "").strip()
            column_key = f"pred_readme_sdg{num}"
            if column_key in target_row:
                target_row[column_key] = pred["prediction"]

    except Exception as e:
        print(f"Error {project_name}: {e}. Skipped.")

    time.sleep(1)

# Write to temp then atomically replace
with open(temp_file, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=target_fields)
    writer.writeheader()
    writer.writerows(target_rows)

os.replace(temp_file, target_file)
print(f"\nDone. {target_file} updated.")