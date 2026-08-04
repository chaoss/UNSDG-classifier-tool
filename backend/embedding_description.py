import re
from typing import List, Dict
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import numpy as np
import sdg_constants
from sdg_constants import SDG_LABELS, SDG_NAMES, SDG_DESCS

# --- Zero-shot and embedding models (lazy-load) ---
_zeroshot = None
_embedder = None

def get_zeroshot():
    """Lazy load zero-shot classification model."""
    global _zeroshot
    if _zeroshot is None:
        _zeroshot = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device_map="auto")
    return _zeroshot

def get_embedder():
    """Lazy load sentence transformer model."""
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _embedder

def clean_text(text: str) -> str:
    """Clean and normalize input text."""
    # Remove excessive whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()

def zero_shot_scores(text: str, labels: List[str]) -> tuple[np.ndarray, Dict]:
    """
    Returns probabilities for each label using NLI zero-shot (multi-label).
    Returns (scores_array, detailed_info_dict)
    """
    clf = get_zeroshot()
    out = clf(text, labels, multi_label=True)
    detailed_info = {
        "labels": out["labels"],
        "scores": out["scores"],
        "sequence": text[:500] + "..." if len(text) > 500 else text
    }
    return np.array(out["scores"], dtype=float), detailed_info

def embedding_similarity_scores(text: str, label_texts: List[str]) -> np.ndarray:
    """
    Cosine similarity between text embedding and each label description.
    Returns normalized similarity scores (0-1 range).
    """
    emb = get_embedder()
    v_text = emb.encode([text], normalize_embeddings=True)[0]
    v_lbls = emb.encode(label_texts, normalize_embeddings=True)
    sims = np.dot(v_lbls, v_text)  # cosine since normalized
    # Normalize to 0..1
    sims = (sims - sims.min()) / (sims.max() - sims.min() + 1e-8)
    return sims

def ensemble_scores(zs: np.ndarray, es: np.ndarray, alpha: float = 0.0) -> np.ndarray:
    """
    Combine zero-shot and embedding scores.
    alpha: weight for zero-shot (default 0.0 means 0% zero-shot, 100% embedding)
    """
    return alpha * zs + (1 - alpha) * es

def classify_text(
    text: str, 
    threshold: float = 0.4, 
    top_k: int = 10, 
    use_ensemble: bool = True,
    verbose: bool = True
) -> Dict:
    """
    Classify project description text against SDGs.
    
    Args:
        text: Project description text to classify
        threshold: Minimum score for SDG inclusion (0-1)
        top_k: Maximum number of predictions to return
        use_ensemble: Whether to combine zero-shot + embedding models
        verbose: Whether to print detailed classification info
    
    Returns:
        Dictionary with predictions and metadata
    """
    # Clean and validate text
    text = clean_text(text)
    if not text:
        raise ValueError("Input text is empty. Please provide a project description.")
    
    # Cap text length for processing speed
    text = text[:6000].lower()
    
    # Zero-shot classification
    zs, zs_details = zero_shot_scores(text, SDG_NAMES)
    
    if verbose:
       
        
        label_score_pairs = list(zip(zs_details["labels"], zs_details["scores"]))
        label_score_pairs.sort(key=lambda x: x[1], reverse=True)
        
        for label, score in label_score_pairs:
            
            if score > 0.9:
                confidence = "HIGH"
            elif score > 0.7:
                confidence = "MEDIUM"
            elif score > 0.5:
                confidence = "LOW"
            else:
                confidence = "VERY LOW"
         
        
 
    
    if use_ensemble:
        # Embedding similarity against SDG descriptions
        es = embedding_similarity_scores(text, sdg_constants.SDG_DESCS)
        scores = ensemble_scores(zs, es, alpha=0.0)
        
        
    else:
        scores = zs
    
    # Rank and threshold
    idx = np.argsort(scores)[::-1]
    ranked = [(sdg_constants.SDG_NAMES[i], float(scores[i])) for i in idx]
    
    # Filter by threshold
    selected = [(name, sc) for (name, sc) in ranked if sc >= threshold]
    if not selected:
        # If nothing meets threshold, return top 1-3
        selected = ranked[:max(1, min(top_k, 3))]
    
    return {
        "predictions": selected[:top_k],
        "top_all": ranked[:top_k],
        "method": "ensemble" if use_ensemble else "zero-shot",
        "text_length": len(text)
    }

def main(project_description: str, project_name: str = None, project_url: str = None) -> Dict:
    """
    Main entry point for text classification.
    
    Args:
        project_description: The project description text to classify
        project_name: Optional project name for metadata
        project_url: Optional project URL for metadata
    
    Returns:
        Dictionary with predictions and metadata
    """
    result = classify_text(project_description, threshold=0.0, use_ensemble=True, verbose=True)
    
    # Format predictions
    predictions = {
        "project_name": project_name or "Unknown",
        "project_url": project_url or "",
        "sdg_predictions": {
            name: float(f"{score:.3f}") for (name, score) in result["predictions"]
        },
        "method": result["method"],
        "text_length": result["text_length"]
    }
    
   
    
    return predictions

# Example usage
if __name__ == "__main__":
#     sample_text = """
#    The Ushahidi Platform is an integrated data crowdsourcing and mapping tool that allows people to rapidly collect, manage and analyze crowdsourced information from their communities. Empowering communities to thrive as a result of accessible data and technology.
#     """
#     result = main(sample_text, project_name="Ushahidi")
#     print(result)
    project_data = [{'name': 'Go.Data',
  'project_description': 'Go.Data is an open-source platform for outbreak response and contact tracing developed by WHO in collaboration with GOARN partners. It streamlines all aspects of outbreak response and is highly versatile with customizable configurations for different scenarios.'},
 {'name': 'Harmony',
  'project_description': 'Harmony is an open-source, end-to end data integration and advanced analytics platform for integrating, harmonizing, analyzing, and visualizing any number of structured data sources from different sectors (e.g. health, education, agriculture, sustainable development, climate change adaptation), ranging from routinely collected individual level data to operational research and survey data.'},
 {'name': 'HOPE',
  'project_description': 'HOPE is UNICEFƒ??s humanitarian cash transfer management information system. HOPE allows to register and target beneficaries, track approval of payment list send them to payment providers, process reconciliation and payment verification and facilitate grievances and feedbacks.'},
 {'name': 'HOT Tasking Manager',
  'project_description': 'The HOT Tasking Manager is a specialized platform developed by the Humanitarian OpenStreetMap Team (HOT) for coordinating volunteers and facilitating collaborative mapping efforts to support disaster response, humanitarian aid, and development projects worldwide.'},
 {'name': 'QField',
  'project_description': 'Survey and digitize data in the field with seamless synchronization.QField focuses on efficiently getting GIS fieldwork done and exchanging data between the field and the office in a comfortable and user-friendly way.'},
 {'name': 'Rural Environmental Registry Registration Module',
  'project_description': 'The Rural Environmental Registry (RER) is a solution for managing declared geospatial environmental information on rural properties to serve as a database for control, monitoring, environmental and economic planning.'},
 {'name': 'The Ushahidi Platform',
  'project_description': 'The Ushahidi Platform is an integrated data crowdsourcing and mapping tool that allows people to rapidly collect, manage and analyze crowdsourced information from their communities. Empowering communities to thrive as a result of accessible data and technology.'},
 {'name': 'UPYOG',
  'project_description': 'The Urban Platform for DeliverY of Online Governance (UPYOG) is a set of Open APIs, services, and reference implementations, setup as a public good, to allow government entities, businesses, startups, and civil society to use a unique digital Infrastructure and build solutions at a large scale. Developed under the National Urban Digital Mission, MoHUA to facilitate the digital delivery of G2G, G2C, G2B services focussing on citizen centricity, UPYOG is available with customizable 14 reference modules.'}]
  
    for item in project_data:
        res = main(item['project_description'], project_name=item['name'])
        print(res)
