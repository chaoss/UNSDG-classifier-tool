import requests
import json
from sdg_constants import SDG_LABELS_DICT as SDG_LABELS


def main(text: str, project_name: str = None, project_url: str = None):
    """
    Classify text using Aurora SDG API and format output to match embedding models.
    
    Args:
        text: Project description text to classify
        project_name: Optional project name for metadata
        project_url: Optional project URL for metadata
    
    Returns:
        Dictionary with predictions in standardized format
    """
    try:
        url = "https://aurora-sdg.labs.vu.nl/classifier/classify/elsevier-sdg-multi"
        payload = json.dumps({"text": text})
        headers = {'Content-Type': 'application/json'}
        response = requests.request("POST", url, headers=headers, data=payload)
        # response.raise_for_status()
        
        raw_result = response.json()
        
        # Transform Aurora API response to match embedding model format
        # Aurora API can return different structures, handle both cases
        
        sdg_predictions = {}
        
        # Check if predictions exist and iterate
        if "predictions" in raw_result and isinstance(raw_result["predictions"], list):
            for idx, pred in enumerate(raw_result["predictions"]):
                
                # Handle case where pred might be a dict with nested structure
                if isinstance(pred, dict):
                    # Extract SDG code and score
                    sdg_code = None
                    sdg_name = None
                    score = None
                    
                    # Check if sdg is a dict with code field (Aurora API format)
                    if "sdg" in pred and isinstance(pred["sdg"], dict):
                        sdg_value = pred["sdg"]
                        # Get the SDG code (e.g., "1", "2", etc.)
                        sdg_code = sdg_value.get("code")
                        # Try to get label from the API response
                        sdg_label = sdg_value.get("label") or sdg_value.get("name")
                        
                        if sdg_code:
                            # Get the full SDG name from our mapping
                            sdg_full_name = SDG_LABELS.get(str(sdg_code), sdg_label or "")
                            # Format as "SDG {number}: {name}"
                            sdg_name = f"SDG {sdg_code}: {sdg_full_name}"
                    
                    # Fallback to old logic if code extraction fails
                    if not sdg_name:
                        if "sdg" in pred:
                            sdg_value = pred["sdg"]
                            if isinstance(sdg_value, dict):
                                sdg_name = sdg_value.get("name") or sdg_value.get("label") or str(sdg_value.get("id", ""))
                            else:
                                sdg_name = str(sdg_value)
                        # Try alternative field names
                        if not sdg_name:
                            sdg_name = pred.get("label") or pred.get("name") or pred.get("sdg_label")
                    
                    # Get score/prediction value
                    score = pred.get("prediction") or pred.get("score") or pred.get("confidence") or 0
                    
                    if sdg_name and isinstance(sdg_name, str):
                        # Format score to 3 decimal places
                        if score > 0.5:
                            sdg_predictions[sdg_name] = round(score, 3)
                    else:
                        print(f"DEBUG - Warning: Could not extract SDG name from prediction {idx}")
                else:
                    print(f"DEBUG - Warning: Prediction {idx} is not a dict: {type(pred)}")
        
        # Format output to match embedding_url.py structure
        formatted_result = {
            "project_name": project_name or "Unknown",
            "project_url": project_url or "",
            "sdg_predictions": sdg_predictions,
            "method": "aurora-api",
        }
        
      
        
        return formatted_result
        
    except requests.exceptions.RequestException as e:
       
        return {
            "project_name": project_name or "Unknown",
            "project_url": project_url or "",
            "sdg_predictions": {},
            "error": str(e),
            "message": "Aurora API request failed"
        }
    except Exception as e:
        return {
            "project_name": project_name or "Unknown",
            "project_url": project_url or "",
            "sdg_predictions": {},
            "error": f"{type(e).__name__}: {str(e)}",
            "message": "Aurora API processing failed"
        }
