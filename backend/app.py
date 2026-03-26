import uuid
import json
import requests
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from datetime import datetime, UTC
from embedding_description import main as classify_description
from embedding_url import main as classify_url
from aurora_api import main as aurora_classify


app = Flask(__name__)
CORS(app)



@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello, World!'})



@app.route('/api/classify_aurora', methods=['POST'])
def classify_aurora():
    data = request.json
    projectName = data.get('projectName')
    projectUrl  = data.get('projectUrl')
    projectDescription = data.get('projectDescription')

    if not projectDescription:
        return jsonify({'error': 'Project description is required'}), 400



    # 1. Aurora API Model (text-based)
    print("\n===== RUNNING AURORA API MODEL =====")
    try:
        aurora_result = aurora_classify(
            text=projectDescription,
            project_name=projectName,
            project_url=projectUrl
        )

        print("Aurora API model completed successfully")
    except Exception as e:
        print(f"Aurora API model failed: {str(e)}")
        return jsonify({
            "error": str(e),
            "message": "Aurora API classification failed"
        }), 500

    # Transform predictions to array format
    sdg_preds = aurora_result.get("sdg_predictions", {})
    if isinstance(sdg_preds, dict):
        preds = [
            {"sdg": name, "prediction": score}
            for name, score in sdg_preds.items()
        ]
    else:
        preds = sdg_preds  # Already in correct format

    filtered_predictions = [p for p in preds if p.get("prediction", 0) > 0.4]

    return jsonify({
        "projectName": aurora_result.get("project_name"),
        "projectUrl": aurora_result.get("project_url"),
        "predictions": filtered_predictions
    }), 200


@app.route('/api/classify_st_description', methods=['POST'])
def classify_st_description():
    data = request.json
    projectName = data.get('projectName')
    projectUrl  = data.get('projectUrl')
    projectDescription = data.get('projectDescription')

    if not projectDescription:
        return jsonify({'error': 'Project description is required'}), 400


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
    filtered_predictions = [p for p in preds if p.get("prediction", 0) > 0.4]
    return jsonify({
            "projectName": projectName,
            "projectUrl": projectUrl,
            "predictions": filtered_predictions,
        }), 200


@app.route('/api/classify_st_url', methods=['POST'])
def classify_st_url():
    data = request.json
    projectName = data.get('projectName')
    projectUrl  = data.get('projectUrl')
    projectDescription = data.get('projectDescription')

    if not projectDescription:
        return jsonify({'error': 'Project description is required'}), 400



     # 2. Sentence Transformer URL Model (GitHub URL-based)
    print("\n===== RUNNING SENTENCE TRANSFORMER URL MODEL =====")
    if projectUrl:
        try:
            st_url_result = classify_url(projectUrl)

            print("ST URL model completed successfully")
        except ValueError as ve:
            print(f"ST URL model invalid URL: {str(ve)}")
            return jsonify({'error': str(ve)}), 400
        except requests.exceptions.HTTPError as he:
            print(f"ST URL model HTTP Error: {str(he)}")
            return jsonify({
                "error": f"Failed to fetch repository data. Please ensure the repository is public and exists. ({str(he)})",
                "message": "Sentence Transformer URL model classification failed"
            }), 400
        except Exception as e:
            print(f"ST URL model failed: {str(e)}")
            return jsonify({
                "error": str(e),
                "message": "Sentence Transformer URL model classification failed"
            }), 500
    else:
        st_url_result = {
            "message": "No project URL provided, skipping URL-based classification"
        }

    preds = [
        {"sdg": name, "prediction": score}
        for name, score in st_url_result.get("sdg_predictions", {}).items()
    ]
    filtered_predictions = [p for p in preds if p.get("prediction", 0) > 0.4]
    return jsonify({
            "projectName": projectName,
            "projectUrl": projectUrl,
            "predictions": filtered_predictions,
        }), 200

# @app.post("/api/upload-md")
# def aurora_api():

#     project_name = request.form.get("project_name", "").strip()
#     project_url = request.form.get("project_url", "").strip()

#     if not project_name:
#         return jsonify({"error": "Project name is required"}), 400
#     if not project_url:
#         return jsonify({"error": "Project URL is required"}), 400


#     if "file" not in request.files:
#         return jsonify({"error":"No file part named 'file' in form-data."}), 400
#     f = request.files["file"]

#     if f.filename == "":
#         return jsonify({ "error": "Empty filename."}), 400
#     if not allowed_ext(f.filename):
#         return jsonify({"error" : "Only .md files are allowed."}), 400


#     filename = secure_filename(f.filename)

#     text = f.read().decode("utf-8", errors="replace")

#     result = aurora_main(text)

#     return jsonify({
#         "project_name": project_name,
#         "project_url": project_url,
#         "filename": filename,
#         "size_bytes": len(text.encode("utf-8")),
#         "content_preview": text[:2000],
#         "predictions": result.get("predictions", "")
#     }), 200

if __name__ == '__main__':
    app.run(debug=True)
