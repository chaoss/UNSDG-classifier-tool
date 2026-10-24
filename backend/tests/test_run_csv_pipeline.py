import csv
import sys
from types import SimpleNamespace

from flask import Flask, jsonify, request
import pytest

from run_csv_pipeline import (
    DEFAULT_INPUT_DIR,
    DEFAULT_OUTPUT_DIR,
    OUTPUT_COLUMNS,
    run,
)


def test_run_refuses_to_overwrite_input_files(tmp_path):
    fields = [
        "name",
        "repository_link",
        "description",
        "target_sdg",
    ]
    input_file = tmp_path / "sdg_1.csv"
    with input_file.open("w", encoding="utf-8", newline="") as csv_file:
        csv.writer(csv_file).writerow(fields)

    with pytest.raises(ValueError, match="overwrite input CSV files"):
        run(tmp_path, tmp_path)


def test_run_writes_predictions_to_separate_goal_files(tmp_path, monkeypatch):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "results"
    input_dir.mkdir()
    fields = [
        "name",
        "repository_link",
        "description",
        "target_sdg",
        *[f"sdg_{number}" for number in range(1, 18)],
    ]

    for filename, project in (
        (
            "sdg_4.csv",
            [
                "Education project",
                "https://example.org/education",
                "Learning for students.",
                "4",
            ],
        ),
        (
            "sdg_8.csv",
            [
                "Jobs project",
                "https://example.org/jobs",
                "Decent work for all.",
                "8",
            ],
        ),
    ):
        with (input_dir / filename).open("w", encoding="utf-8", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(fields)
            writer.writerow([*project, *([0] * 17)])

    fake_app = Flask(__name__)
    received_names = []

    @fake_app.post("/api/classify_st_url")
    def classify():
        project_name = request.json["projectName"]
        received_names.append(project_name)
        predictions = (
            [
                {"sdg": "SDG 4: Quality Education", "prediction": 0.81},
                {"sdg": "SDG 17: Partnerships", "prediction": 0.42},
            ]
            if project_name == "Education project"
            else []
        )
        return jsonify({"predictions": predictions})

    monkeypatch.setitem(sys.modules, "app", SimpleNamespace(app=fake_app))
    sleep_calls = []
    monkeypatch.setattr("run_csv_pipeline.time.sleep", sleep_calls.append)

    run(input_dir, output_dir)

    assert received_names == ["Education project", "Jobs project"]
    assert sleep_calls == [30]
    output_files = list(output_dir.glob("sdg_*.csv"))
    assert len(output_files) == 17
    for number in range(1, 18):
        with (output_dir / f"sdg_{number}.csv").open(
            "r", encoding="utf-8", newline=""
        ) as csv_file:
            reader = csv.DictReader(csv_file)
            assert reader.fieldnames == OUTPUT_COLUMNS
            rows = list(reader)
            if number in (4, 17):
                assert len(rows) == 1
                assert rows[0]["name"] == "Education project"
                expected_score = "0.81" if number == 4 else "0.42"
                assert rows[0]["prediction"] == expected_score
            else:
                assert rows == []


def test_run_resumes_at_file_row_and_appends_existing_results(tmp_path, monkeypatch):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "results"
    input_dir.mkdir()
    fields = ["name", "repository_link", "description", "target_sdg"]

    with (input_dir / "sdg_1.csv").open(
        "w", encoding="utf-8", newline=""
    ) as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(fields)
        writer.writerow(["Earlier file project", "https://example.org/1", "Description", "1"])

    with (input_dir / "sdg_2.csv").open(
        "w", encoding="utf-8", newline=""
    ) as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(fields)
        for row_number in range(2, 14):
            writer.writerow(
                [
                    f"Project row {row_number}",
                    f"https://example.org/{row_number}",
                    "Description",
                    "2",
                ]
            )

    output_dir.mkdir()
    existing_result = {
        "source_file": "sdg_2.csv",
        "source_row": "11",
        "name": "Previously processed",
        "repository_link": "https://example.org/previous",
        "description": "Earlier result",
        "target_sdg": "2",
        "predicted_sdg": "SDG 2: Zero Hunger",
        "prediction": "0.5",
    }
    with (output_dir / "sdg_2.csv").open(
        "w", encoding="utf-8", newline=""
    ) as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerow(existing_result)

    fake_app = Flask(__name__)
    received_names = []

    @fake_app.post("/api/classify_st_url")
    def classify():
        project_name = request.json["projectName"]
        received_names.append(project_name)
        return jsonify(
            {
                "predictions": [
                    {"sdg": "SDG 2: Zero Hunger", "prediction": 0.75}
                ]
            }
        )

    monkeypatch.setitem(sys.modules, "app", SimpleNamespace(app=fake_app))
    sleep_calls = []
    monkeypatch.setattr("run_csv_pipeline.time.sleep", sleep_calls.append)

    run(input_dir, output_dir, start_file="sdg_2.csv", start_row=12)

    assert received_names == ["Project row 12", "Project row 13"]
    assert sleep_calls == [30]
    with (output_dir / "sdg_2.csv").open(
        "r", encoding="utf-8", newline=""
    ) as csv_file:
        rows = list(csv.DictReader(csv_file))
    assert [row["name"] for row in rows] == [
        "Previously processed",
        "Project row 12",
        "Project row 13",
    ]


def test_main_defaults_to_last_recorded_cutoff(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "run_csv_pipeline.run",
        lambda *args: calls.append(args),
    )
    monkeypatch.setattr(sys, "argv", ["run_csv_pipeline.py"])

    from run_csv_pipeline import main

    main()

    assert calls == [
        (DEFAULT_INPUT_DIR, DEFAULT_OUTPUT_DIR, "sdg_9.csv", 19)
    ]
