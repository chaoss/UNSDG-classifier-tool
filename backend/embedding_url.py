import os
import re
import base64
import requests
from urllib.parse import urlparse
from typing import List, Dict, Tuple
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import numpy as np
from sdg_constants import SDG_LABELS, SDG_NAMES, SDG_DESCS

# --- GitHub fetch utilities ---
GITHUB_API = "https://api.github.com"

def parse_repo(url: str) -> Tuple[str, str]:
    """
    Accepts strictly URLs like https://github.com/owner/repo or owner/repo.
    Returns (owner, repo).
    Raises ValueError if URL is invalid.
    """
    u = url.strip()
    if u.startswith("http://") or u.startswith("https://"):
        parsed = urlparse(u)
        if parsed.hostname not in ["github.com", "www.github.com"]:
            raise ValueError(f"Invalid domain (expected github.com): {url}")
            
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) != 2:
            raise ValueError(f"Invalid repository URL format (expected https://github.com/owner/repo): {url}")
            
        owner, repo = path_parts[0], path_parts[1]
        if repo.endswith(".git"):
            repo = repo[:-4]
        return owner, repo
    else:
        parts = u.strip("/").split("/")
        if len(parts) != 2:
            raise ValueError(f"Invalid repository format (expected owner/repo): {url}")
            
        owner, repo = parts[0], parts[1]
        if repo.endswith(".git"):
            repo = repo[:-4]
        return owner, repo

def gh_get(path: str, params: dict = None, accept_preview: bool = False) -> dict:
    headers = {"User-Agent": "sdg-classifier"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if accept_preview:
        # topics API requires a custom media type on some API versions
        headers["Accept"] = "application/vnd.github.mercy-preview+json, application/vnd.github+json"
    else:
        headers["Accept"] = "application/vnd.github+json"
    r = requests.get(GITHUB_API + path, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def fetch_repo_text(url: str, max_issues: int = 10) -> Dict:
    owner, repo = parse_repo(url)

    repo_data = gh_get(f"/repos/{owner}/{repo}", accept_preview=True)
    name = repo_data.get("name") or ""
    description = repo_data.get("description") or ""
    topics = " ".join(repo_data.get("topics") or [])
    homepage = repo_data.get("homepage") or ""

    # README
    readme = ""
    try:
        rd = gh_get(f"/repos/{owner}/{repo}/readme")
        content_b64 = rd.get("content", "")
        if content_b64:
            readme = base64.b64decode(content_b64).decode(errors="ignore")
    except Exception:
        pass

   
    # Issues (titles only, open ones)
    issues_texts = []
    try:
        issues = gh_get(f"/repos/{owner}/{repo}/issues", params={"state": "open", "per_page": max_issues})
        for it in issues:
            if "pull_request" not in it:  # skip PRs
                issues_texts.append(it.get("title", ""))
    except Exception:
        pass

    # Concatenate
    corpus = "\n".join([
        name, description, topics, homepage, readme, "\n".join(issues_texts)
    ])

    # Light clean
    corpus = re.sub(r"[ \t]+", " ", corpus)
    corpus = re.sub(r"\n{2,}", "\n", corpus).strip()

    repo_text = {
        "owner": owner, "repo": repo, "text": corpus,
        "meta": {"name": name, "description": description, "topics": topics.split(), "homepage": homepage}
    }
    
    return repo_text

# --- Zero-shot and embedding models (lazy-load) ---
_zeroshot = None
_embedder = None

def get_zeroshot():
    global _zeroshot
    if _zeroshot is None:
        _zeroshot = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device_map="auto")
    return _zeroshot

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _embedder

def zero_shot_scores(text: str, labels: List[str]) -> np.ndarray:
    """
    Returns probabilities for each label using NLI zero-shot (multi-label).
    """
    clf = get_zeroshot()
    out = clf(text, labels, multi_label=True)
    detailed_info = {
        "labels" : out["labels"],
        "scores" : out["scores"],
        "sequence" : text[:500] + "..." if len(text) > 500 else text
    }
    # transformers returns in label order provided
    return np.array(out["scores"], dtype=float), detailed_info

def embedding_similarity_scores(text: str, label_texts: List[str]) -> np.ndarray:
    """
    Cosine similarity between text embedding and each label description.
    """
    emb = get_embedder()
    v_text = emb.encode([text], normalize_embeddings=True)[0]
    v_lbls = emb.encode(label_texts, normalize_embeddings=True)
    sims = np.dot(v_lbls, v_text)  # cosine since normalized
    # Normalize to 0..1
    sims = (sims - sims.min()) / (sims.max() - sims.min() + 1e-8)
    return sims

def ensemble_scores(zs: np.ndarray, es: np.ndarray, alpha: float = 0.5) -> np.ndarray:
    """
    Simple mean ensemble; tune alpha if desired.
    """
    return alpha * zs + (1 - alpha) * es

def classify_repo(url: str, threshold: float = 0.4, top_k: int = 10, use_ensemble: bool = True):
    data = fetch_repo_text(url)
    text = data["text"][:6000]  # cap for speed; increase if needed
    if not text:
        raise ValueError("No text extracted from this repository. Add README or description.")

    # Zero-shot on label NAMES *and* include SDG descriptions for embedding sim
    zs, zs_details = zero_shot_scores(text, SDG_NAMES)


    label_score_pairs = list(zip(zs_details["labels"],zs_details["scores"]))
    label_score_pairs.sort(key=lambda x:x[1], reverse=True)

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
        # Embedding similarity against richer label descriptions
        es = embedding_similarity_scores(text, SDG_DESCS)
        scores = ensemble_scores(zs, es, alpha=0.8) 

    
    else:
        scores = zs

    # Rank + threshold
    idx = np.argsort(scores)[::-1]
    ranked = [(SDG_NAMES[i], float(scores[i])) for i in idx]

    selected = [(name, sc) for (name, sc) in ranked if sc >= threshold]
    if not selected:
        selected = ranked[:max(1, min(top_k, 3))]

    return {
        "repo": f"{data['owner']}/{data['repo']}",
        "predictions": selected[:top_k],
        "top_all": ranked[:top_k],
        "meta": data["meta"]
    }

def main(url: str):
   
    result = classify_repo(url, threshold=0.5, use_ensemble=True)
   
    predictions = {
        "project_name": result["repo"],
        "project_url": url,
        "sdg_predictions": {
            name: float(f"{score:.3f}") for (name, score) in result["predictions"]
        }
    }
  
    
    return predictions

# if __name__ == "__main__":
#     url = "https://github.com/processing/p5.js"
#     main(url) 