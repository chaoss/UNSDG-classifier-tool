"""Fetch targets and child targets for all 17 UN Sustainable Development Goals."""

import json
from pathlib import Path
import requests


API_URL = "https://unstats.un.org/sdgapi/v1/sdg/Goal/{goal}/Target/List"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "sdg_targets"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with requests.Session() as session:
        session.headers.update({"Accept": "application/json"})
        for goal in range(1, 18):
            response = session.get(
                API_URL.format(goal=goal),
                params={"includechildren": "true"},
                timeout=30,
            )
            response.raise_for_status()
            payload = response.json()

            output_path = OUTPUT_DIR / f"goal_{goal}.json"
            output_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(f"Fetched goal {goal}: {output_path}")


if __name__ == "__main__":
    main()