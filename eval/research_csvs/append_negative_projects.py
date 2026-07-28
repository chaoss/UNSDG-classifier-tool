import ast
import csv
from pathlib import Path

base_dir = Path(__file__).resolve().parent
source_path = base_dir / "testt.py"
csv_path = base_dir / "projects_sdg_matrix.csv"

with source_path.open("r", encoding="utf-8") as f:
    tree = ast.parse(f.read(), filename=str(source_path))

negative_projects = None
for node in tree.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "NEGATIVE_PROJECTS":
                negative_projects = ast.literal_eval(node.value)
                break
    if negative_projects is not None:
        break

if negative_projects is None:
    raise RuntimeError("Could not find NEGATIVE_PROJECTS in testt.py")

with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

if fieldnames is None:
    raise RuntimeError("CSV header not found")

fieldnames = [field.lstrip("\ufeff") for field in fieldnames]

for project in negative_projects:
    row = {
        "name": project.get("projectName", ""),
        "github_url": project.get("projectUrl", ""),
        "project_description": project.get("projectDescription", ""),
    }

    for i in range(1, 18):
        row[f"act_sdg{i}"] = 0
        row[f"pred_readme_sdg{i}"] = 0.0

    rows.append(row)

with csv_path.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Appended {len(negative_projects)} projects to {csv_path}")
print(f"Total rows now: {len(rows)}")
