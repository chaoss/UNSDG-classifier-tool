"""Run the ST URL classification pipeline over the SDG CSV datasets.

Run from the repository root with:
    python backend/run_csv_pipeline.py

Or from the backend directory with:
    python run_csv_pipeline.py

By default, resume from the recorded cutoff without replacing existing results.
To choose another physical row:
    python backend/run_csv_pipeline.py --start-file sdg_2.csv --start-row 12
"""

import argparse
import csv
import re
import sys
import time
from contextlib import ExitStack
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent
REQUEST_DELAY_SECONDS = 30
DEFAULT_INPUT_DIR = BACKEND_DIR / "csv_data_per_sdg"
DEFAULT_OUTPUT_DIR = DEFAULT_INPUT_DIR / "res_per_sdg"
DEFAULT_START_FILE = "sdg_9.csv"
DEFAULT_START_ROW = 19
REQUIRED_COLUMNS = {"name", "repository_link", "description", "target_sdg"}
OUTPUT_COLUMNS = [
    "source_file",
    "source_row",
    "name",
    "repository_link",
    "description",
    "target_sdg",
    "predicted_sdg",
    "prediction",
]


def _sdg_number(prediction):
    """Return the goal number from an API label such as ``SDG 4: ...``."""
    label = prediction.get("sdg", "")
    match = re.match(r"^\s*SDG\s*(\d+)\b", str(label), re.IGNORECASE)
    if not match:
        raise ValueError(f"Unrecognized SDG label: {label!r}")

    number = int(match.group(1))
    if not 1 <= number <= 17:
        raise ValueError(f"SDG number must be between 1 and 17: {number}")
    return number


def _read_input_files(input_dir):
    input_files = [
        path for path in input_dir.glob("sdg_*.csv")
        if re.fullmatch(r"sdg_\d+", path.stem)
    ]
    input_files.sort(key=lambda path: int(path.stem[4:]))
    if not input_files:
        raise FileNotFoundError(f"No sdg_*.csv files found in {input_dir}")

    records = []
    for input_file in input_files:
        with input_file.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            if reader.fieldnames is None:
                raise ValueError(f"CSV file has no header: {input_file}")

            missing_columns = REQUIRED_COLUMNS.difference(reader.fieldnames)
            if missing_columns:
                missing = ", ".join(sorted(missing_columns))
                raise ValueError(f"{input_file} is missing required columns: {missing}")

            for row_number, row in enumerate(reader, start=2):
                if not any(value and value.strip() for value in row.values()):
                    continue
                records.append((input_file.name, row_number, row))

    return input_files, records


def run(
    input_dir=DEFAULT_INPUT_DIR,
    output_dir=DEFAULT_OUTPUT_DIR,
    start_file=None,
    start_row=None,
):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    input_files, records = _read_input_files(input_dir)
    if (start_file is None) != (start_row is None):
        raise ValueError("--start-file and --start-row must be provided together")
    if start_file is not None:
        if start_row < 2:
            raise ValueError("--start-row must be a CSV data row number (2 or greater)")
        file_names = [path.name for path in input_files]
        if start_file not in file_names:
            raise ValueError(f"Start file not found among input CSVs: {start_file}")

        start_file_index = file_names.index(start_file)
        records = [
            record
            for record in records
            if file_names.index(record[0]) > start_file_index
            or (
                record[0] == start_file
                and record[1] >= start_row
            )
        ]

    input_paths = {path.resolve() for path in input_files}
    conflicting_outputs = [
        output_dir / f"sdg_{number}.csv"
        for number in range(1, 18)
        if (output_dir / f"sdg_{number}.csv").resolve() in input_paths
    ]
    if conflicting_outputs:
        raise ValueError(
            "Output directory would overwrite input CSV files: "
            + ", ".join(str(path) for path in conflicting_outputs)
        )
    output_dir.mkdir(parents=True, exist_ok=True)

    resuming = start_file is not None
    if resuming:
        for number in range(1, 18):
            output_file = output_dir / f"sdg_{number}.csv"
            if output_file.exists() and output_file.stat().st_size:
                with output_file.open("r", encoding="utf-8", newline="") as handle:
                    header = next(csv.reader(handle), None)
                if header != OUTPUT_COLUMNS:
                    raise ValueError(
                        f"Cannot resume: unexpected header in {output_file}"
                    )

    # Import only when running the job; importing app also loads the ML stack.
    from app import app

    output_counts = {number: 0 for number in range(1, 18)}
    failed_projects = 0
    projects_with_predictions = 0

    with ExitStack() as stack:
        writers = {}
        output_handles = {}
        for number in range(1, 18):
            output_file = output_dir / f"sdg_{number}.csv"
            write_header = (
                not resuming
                or not output_file.exists()
                or output_file.stat().st_size == 0
            )
            handle = stack.enter_context(
                output_file.open(
                    "a" if resuming else "w",
                    encoding="utf-8",
                    newline="",
                )
            )
            writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
            if write_header:
                writer.writeheader()
            handle.flush()
            writers[number] = writer
            output_handles[number] = handle

        client = app.test_client()
        print(
            f"Processing {len(records)} projects from {len(input_files)} CSV files"
            + (f", starting at {start_file} row {start_row}." if resuming else ".")
        )

        for index, (source_file, source_row, row) in enumerate(records, start=1):
            if index > 1:
                time.sleep(REQUEST_DELAY_SECONDS)

            response = client.post(
                "/api/classify_st_url",
                json={
                    "projectName": row["name"],
                    "projectUrl": row["repository_link"],
                    "projectDescription": row["description"],
                },
            )
            payload = response.get_json(silent=True)
            if response.status_code != 200 or not isinstance(payload, dict):
                failed_projects += 1
                detail = (
                    payload.get("error", payload)
                    if isinstance(payload, dict)
                    else payload
                )
                print(
                    f"Failed {source_file}:{source_row} "
                    f"(HTTP {response.status_code}): {detail}",
                    file=sys.stderr,
                )
                continue

            predictions = payload.get("predictions")
            if not isinstance(predictions, list):
                failed_projects += 1
                print(
                    f"Failed {source_file}:{source_row}: response has no predictions list",
                    file=sys.stderr,
                )
                continue

            if predictions:
                projects_with_predictions += 1

            for prediction in predictions:
                try:
                    number = _sdg_number(prediction)
                    score = float(prediction["prediction"])
                except (KeyError, TypeError, ValueError) as error:
                    failed_projects += 1
                    print(
                        f"Invalid prediction for {source_file}:{source_row}: {error}",
                        file=sys.stderr,
                    )
                    continue

                writers[number].writerow(
                    {
                        "source_file": source_file,
                        "source_row": source_row,
                        "name": row["name"],
                        "repository_link": row["repository_link"],
                        "description": row["description"],
                        "target_sdg": row["target_sdg"],
                        "predicted_sdg": prediction["sdg"],
                        "prediction": score,
                    }
                )
                output_handles[number].flush()
                output_counts[number] += 1

            if index % 25 == 0 or index == len(records):
                print(f"Processed {index}/{len(records)} projects.")

    print(
        f"Complete: {len(records)} projects processed; "
        f"{projects_with_predictions} had predictions; "
        f"{failed_projects} project/prediction errors."
    )
    print(f"Results written to {output_dir}")
    for number, count in output_counts.items():
        print(f"  SDG {number}: {count} predictions")


def main():
    parser = argparse.ArgumentParser(
        description="Classify projects in the SDG CSV files and split results by goal."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help=f"Directory containing sdg_*.csv files (default: {DEFAULT_INPUT_DIR})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory for the 17 result CSV files (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--start-file",
        help="Resume at this input CSV (for example, sdg_2.csv); appends to results.",
    )
    parser.add_argument(
        "--start-row",
        type=int,
        help="Physical CSV row number to resume at (the header is row 1).",
    )
    args = parser.parse_args()
    start_file = args.start_file
    start_row = args.start_row
    if start_file is None and start_row is None:
        start_file = DEFAULT_START_FILE
        start_row = DEFAULT_START_ROW
    run(args.input_dir, args.output_dir, start_file, start_row)


if __name__ == "__main__":
    main()
