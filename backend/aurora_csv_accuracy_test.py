import csv
from pathlib import Path
import re
import time

from aurora_api import main as aurora_classify

CSV_PATH = Path(__file__).with_name('tese_set_2.csv')
ACT_SDG_FIELDS = [f'act_sdg{i}' for i in range(1, 18)]


def extract_predicted_sdg_numbers(sdg_predictions: dict) -> set[int]:
    """Extract SDG numbers from Aurora prediction keys like 'SDG 3: ...'."""
    nums = set()
    for key in sdg_predictions.keys():
        match = re.match(r"SDG\s*(\d+)", key)
        if match:
            nums.add(int(match.group(1)))
    return nums


def load_csv_projects(path: Path) -> list[dict]:
    projects = []
    with path.open('r', encoding='utf-8-sig', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            project_name = (row.get('name') or '').strip()
            project_url = (row.get('github_url') or '').strip()
            project_description = (row.get('project_description') or '').strip()
            if not project_description:
                continue
            ground_truth_sdgs = {
                i
                for i in range(1, 18)
                if str(row.get(f'act_sdg{i}', '')).strip() in {'1', '1.0', 'true', 'True'}
            }
            projects.append(
                {
                    'projectName': project_name,
                    'projectUrl': project_url,
                    'projectDescription': project_description,
                    'ground_truth_sdgs': ground_truth_sdgs,
                }
            )
    return projects


def main(limit: int | None = None):
    projects = load_csv_projects(CSV_PATH)
    if limit is not None:
        projects = projects[:limit]

    total_projects = len(projects)
    project_hits = 0
    total_gt_labels = 0
    total_predicted_labels = 0
    total_overlap_labels = 0
    total_false_positive_labels = 0
    total_negative_projects = 0
    correct_negatives = 0

    print(f"Loaded {total_projects} projects from {CSV_PATH.name}")

    for index, project in enumerate(projects, start=1):
        print(f"\n[{index}/{total_projects}] {project['projectName'] or '<unnamed>'}")
        result = aurora_classify(
            text=project['projectDescription'],
            project_name=project['projectName'],
            project_url=project['projectUrl'],
        )
        if 'error' in result:
            print(f"  ERROR: {result.get('error')} - {result.get('message')}")
            continue

        predicted = extract_predicted_sdg_numbers(result.get('sdg_predictions', {}))
        gt = project['ground_truth_sdgs']
        overlap = predicted & gt
        false_positives = predicted - gt

        total_predicted_labels += len(predicted)
        total_gt_labels += len(gt)
        total_overlap_labels += len(overlap)
        total_false_positive_labels += len(false_positives)

        if gt:
            if overlap:
                project_hits += 1
                print(f"  ✓ hit: predicted {predicted}, ground truth {gt}, overlap {overlap}")
            else:
                print(f"  ✗ miss: predicted {predicted}, ground truth {gt}")
        else:
            total_negative_projects += 1
            if not predicted:
                correct_negatives += 1
                print("  ✓ correct negative: no SDG predicted")
            else:
                print(f"  ✗ false positive: predicted {predicted} for no-ground-truth project")

        if false_positives:
            print(f"    false-positive labels: {false_positives}")

        time.sleep(2)

    positive_projects = total_projects - total_negative_projects
    project_accuracy = project_hits / positive_projects if positive_projects else 0.0
    label_recall = total_overlap_labels / total_gt_labels if total_gt_labels else 0.0
    precision = (
        total_overlap_labels / total_predicted_labels if total_predicted_labels else 0.0
    )
    negative_accuracy = (
        correct_negatives / total_negative_projects if total_negative_projects else 0.0
    )

    print("\n=== SUMMARY ===")
    print(f"Projects evaluated: {total_projects}")
    if positive_projects:
        print(
            f"Positive-project hit rate: {project_hits}/{positive_projects} "
            f"({project_accuracy:.1%})"
        )
    if total_gt_labels:
        print(
            f"Label recall: {total_overlap_labels}/{total_gt_labels} "
            f"({label_recall:.1%})"
        )
    if total_predicted_labels:
        print(
            f"Label precision: {total_overlap_labels}/{total_predicted_labels} "
            f"({precision:.1%})"
        )
    if total_negative_projects:
        print(
            f"Negative-project accuracy: {correct_negatives}/{total_negative_projects} "
            f"({negative_accuracy:.1%})"
        )

    print(f"Total false-positive labels: {total_false_positive_labels}")


if __name__ == '__main__':
    main()