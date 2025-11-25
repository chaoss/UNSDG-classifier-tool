from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from classify import main as classify_text
from datetime import datetime
from aurora_api import main as aurora_main
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)



@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello, World!'})



@app.route('/api/classify', methods=['POST'])
def classify():
    data = request.json
    projectName = data.get('projectName')
    projectUrl  = data.get('projectUrl')
    projectDescription = data.get('projectDescription')
    # problemStatement = data.get('problemStatement')
    # longTermGoal = data.get('longTermGoal')
    # solutionApproach = data.get('solutionApproach')
    # targetAudience = data.get('targetAudience')

    if not projectUrl:
        return jsonify({'error': 'URL is required'}), 400
    
    # text = "\n".join([
    #     projectName or "",
    #     problemStatement or "",
    #     solutionApproach or "",  
    #     longTermGoal or "",
    #     targetAudience or ""   
    # ])

    # print("Classifying text:", text)

    result = aurora_main(projectDescription)

    # Go through result.get("predictions") and remove all entries with value less than 0.4
    # print("Raw predictions:", result.get("predictions", []))

    preds = result.get("predictions", []) or []
    filtered_predictions = [p for p in preds if (p.get("prediction") or 0) > 0.4]


    return jsonify({
        "projectName": projectName,
        "projectUrl": projectUrl,
        "predictions": filtered_predictions
    }), 200


# def allowed_ext(filename: str) -> bool:
#     return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTS)




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