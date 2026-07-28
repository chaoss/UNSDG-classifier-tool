import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
#from embedding_description import main as classify_description
from embedding_url import main as classify_url
from aurora_api import main as aurora_classify
from dotenv import load_dotenv
load_dotenv()

try:
    from services.repo_fetcher import (
        InvalidURLError,
        UnsupportedHostError,
        RepositoryNotFoundError,
        RateLimitError,
        FetchError,
    )
except Exception:
    # If import fails, degrade gracefully — all map to ValueError
    InvalidURLError         = ValueError
    UnsupportedHostError    = ValueError
    RepositoryNotFoundError = ValueError
    RateLimitError          = ValueError
    FetchError              = ValueError

app = Flask(__name__)
CORS(app)


@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello, World!'})


# ---------------------------------------------------------------------------
# Aurora
# ---------------------------------------------------------------------------

@app.route('/api/classify_aurora', methods=['POST'])
def classify_aurora():
    data               = request.json
    projectName        = data.get('projectName')
    projectUrl         = data.get('projectUrl')
    projectDescription = data.get('projectDescription')

    if not projectDescription:
        return jsonify({'error': 'Project description is required'}), 400

    print("\n===== RUNNING AURORA API MODEL =====")
    try:
        aurora_result = aurora_classify(
            text         = projectDescription,
            project_name = projectName,
            project_url  = projectUrl,
        )
        print("Aurora API model completed successfully")
    except Exception as e:
        print(f"Aurora API model failed: {e}")
        return jsonify({"error": str(e), "message": "Aurora API classification failed"}), 500

    sdg_preds = aurora_result.get("sdg_predictions", {})
    preds = (
        [{"sdg": name, "prediction": score} for name, score in sdg_preds.items()]
        if isinstance(sdg_preds, dict)
        else sdg_preds
    )
    filtered = [p for p in preds if p.get("prediction", 0) > 0.4]

    return jsonify({
        "projectName": aurora_result.get("project_name"),
<<<<<<< Updated upstream
        "projectUrl":  aurora_result.get("project_url"),
        "predictions": filtered,
=======
        "projectUrl": aurora_result.get("project_url"),
        "predictions": preds
>>>>>>> Stashed changes
    }), 200


# ---------------------------------------------------------------------------
# ST Description
# ---------------------------------------------------------------------------

# @app.route('/api/classify_st_description', methods=['POST'])
# def classify_st_description():
#     data               = request.json
#     projectName        = data.get('projectName')
#     projectUrl         = data.get('projectUrl')
#     projectDescription = data.get('projectDescription')

#     if not projectDescription:
#         return jsonify({'error': 'Project description is required'}), 400

#     print("\n===== RUNNING SENTENCE TRANSFORMER DESCRIPTION MODEL =====")
#     try:
#         st_desc_result = classify_description(
#             project_description = projectDescription,
#             project_name        = projectName,
#             project_url         = projectUrl,
#         )
#         print("ST Description model completed successfully")
#     except Exception as e:
#         print(f"ST Description model failed: {e}")
#         return jsonify({
#             "error":   str(e),
#             "message": "Sentence Transformer Description model classification failed",
#         }), 500

#     preds = [
#         {"sdg": name, "prediction": score}
#         for name, score in st_desc_result.get("sdg_predictions", {}).items()
#     ]
#     filtered = [p for p in preds if p.get("prediction", 0) > 0.4]

#     return jsonify({
#         "projectName": projectName,
#         "projectUrl":  projectUrl,
#         "predictions": filtered,
#     }), 200


<<<<<<< Updated upstream
# ---------------------------------------------------------------------------
# ST URL
# ---------------------------------------------------------------------------
=======
    # 3. Sentence Transformer Description Model (text-based)
    print("\n===== RUNNING SENTENCE TRANSFORMER DESCRIPTION MODEL =====")
    try:
        st_desc_result = classify_description(
            project_description=projectDescription,
            project_name=projectName,
            project_url=projectUrl
        )

        print("ST Description model completed successfully")
    except Exception as e:
        print(f"ST Description model failed: {str(e)}")
        st_desc_result = {
            "error": str(e),
            "message": "Sentence Transformer Description model classification failed"
        }
        return jsonify(st_desc_result), 500

    # Convert st-description-model predictions to the expected format for logging
    # (keeping backward compatibility with existing data/predictions.json structure)
    preds = [
        {"sdg": name, "prediction": score}
        for name, score in st_desc_result.get("sdg_predictions", {}).items()
    ]
    
    return jsonify({
            "projectName": projectName,
            "projectUrl": projectUrl,
            "predictions": preds,
        }), 200

>>>>>>> Stashed changes

@app.route('/api/classify_st_url', methods=['POST'])
def classify_st_url():
    data               = request.json
    projectName        = data.get('projectName')
    projectUrl         = data.get('projectUrl')
    projectDescription = data.get('projectDescription', '')

    if not projectDescription:
        return jsonify({'error': 'Project description is required'}), 400

    print("\n===== RUNNING SENTENCE TRANSFORMER URL MODEL =====")

    if not projectUrl:
        return jsonify({
            "projectName": projectName,
            "projectUrl":  projectUrl,
            "predictions": [],
            "message":     "No project URL provided, skipping URL-based classification",
        }), 200

    try:
        st_url_result = classify_url(
            url                 = projectUrl,
            project_description = projectDescription,
        )
        print("ST URL model completed successfully")

    # ── 400 — bad input from the user ────────────────────────────────────────
    # These all mean the URL is wrong in some way the user can fix themselves.
    except (InvalidURLError, UnsupportedHostError, ValueError) as e:
        print(f"ST URL model bad URL: {e}")
        return jsonify({
            "error":   str(e),
            "message": "Invalid or unsupported repository URL. "
                       "Accepted: github.com, gitlab.com, codeberg.org, bitbucket.org "
                       "and self-hosted GitLab instances.",
        }), 400

    # ── 404 — repo exists in a valid URL shape but can't be reached ──────────
    except RepositoryNotFoundError as e:
        print(f"ST URL model repo not found: {e}")
        return jsonify({
            "error":   str(e),
            "message": "Repository not found. Check the URL and ensure the repo is public.",
        }), 404

    # ── 429 — rate limited by the forge API ───────────────────────────────────
    except RateLimitError as e:
        print(f"ST URL model rate limited: {e}")
        return jsonify({
            "error":   str(e),
            "message": "Rate limit hit on the repository API. Try again in a few minutes.",
        }), 429

    # ── 502 — network/HTTP failure fetching from the forge ────────────────────
    except (FetchError, requests.exceptions.HTTPError) as e:
        print(f"ST URL model fetch error: {e}")
        return jsonify({
            "error":   str(e),
            "message": "Failed to fetch repository data. "
                       "Ensure the repository is public and the URL is correct.",
        }), 502

    # ── 500 — anything else (model failure, microservice down, etc.) ──────────
    except Exception as e:
        print(f"ST URL model unexpected error: {e}")
        return jsonify({
            "error":   str(e),
            "message": "Sentence Transformer URL model classification failed.",
        }), 500

    preds = [
        {"sdg": name, "prediction": score}
        for name, score in st_url_result.get("sdg_predictions", {}).items()
    ]
<<<<<<< Updated upstream
    filtered = [p for p in preds if p.get("prediction", 0) > 0.4]
=======
    
    return jsonify({
            "projectName": projectName,
            "projectUrl": projectUrl,
            "predictions": preds,
        }), 200

@app.route("/api/osdg_api", methods=["POST"])
def osdg_external_api():
    data = request.json
    projectName = data.get('projectName')
    projectUrl  = data.get('projectUrl')
    projectDescription = data.get('projectDescription')

    if not projectDescription:
        return jsonify({'error': 'Project description is required'}), 400

    # Call the external OSDG API
    try:
        osdg_response = requests.post(
            "http://20.73.166.85/label_text",
            json={
                "text": projectDescription
            },
            headers={
                "token": os.environ.get("OSDG_TOKEN")  # Ensure you have the OSDG token set in your environment variables
            },
            timeout=1000  # Set a timeout for the request
        )
        osdg_response.raise_for_status()  # Raise an error for bad status codes
        osdg_result = osdg_response.json()
    except requests.exceptions.RequestException as e:
        print(f"OSDG API request failed: {str(e)}")
        return jsonify({
            "error": f"Failed to connect to OSDG API: {str(e)}",
            "message": "OSDG API classification failed"
        }), 500
>>>>>>> Stashed changes

    return jsonify({
        "projectName": projectName,
        "projectUrl":  projectUrl,
        "predictions": filtered,
    }), 200


if __name__ == '__main__':
    app.run(debug=True)