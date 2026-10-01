    # Backend Classification Pipeline: Size, Lifecycle, and Cold Starts

    This document focuses on the size and runtime shape of the classification pipeline: which models and processes exist, what they do, when they load and run, and how today's in-process LUKE design compares with the former LUKE Flask service at `127.0.0.1:9010`.

    ## Executive Summary

    - The repository-classification path processes one summary text with two local models and returns scores for 17 SDGs.
    - **LUKE** is the fine-tuned 17-class classifier. Its checkpoint is approximately **1.7 GB** according to the implementation's own comments. It tokenizes up to 512 tokens per input.
    - **MPNet** (`all-mpnet-base-v2`) creates semantic embeddings for the summary and 17 SDG descriptions. The shared embedder code describes each of the formerly duplicated MPNet copies as approximately **420 MB**; current code keeps one process-wide instance.
    - The models do not load at module import in the current implementation. LUKE loads on the first request that reaches LUKE inference; MPNet loads on the first request that reaches embedding scoring. Their objects are then reused for the lifetime of that Python process.
    - The former model server loaded LUKE eagerly while importing `models/app.py`, before it started listening on port 9010. The backend called its `/predict` endpoint over loopback. Moving LUKE in-process removed that model-service dependency and request hop, but did not remove LUKE inference or the large fine-tuned checkpoint.
    - The in-process design improves **backend process startup/readiness** because Flask can bind before LUKE is loaded. It does **not guarantee a faster cold first classification**: the current first classification pays the deferred LUKE load. A previously started and warmed 9010 service could answer its first prediction without that load happening in the request.

    All weight sizes above are approximate implementation references, not a measurement of total RAM, peak RAM, or VRAM. This repository does not currently include a benchmark comparing cold start or inference time between the two architectures.

    ## What “Size” Means Here

    There are several different sizes worth distinguishing:

    1. **Model artifact size:** bytes stored in the Hugging Face cache or downloaded from the Hub.
    2. **Resident model size:** memory occupied by loaded model parameters and tokenizer state in a Python process.
    3. **Peak loading memory:** temporary memory used while creating the model, loading the state dictionary, converting precision, and moving tensors to the selected device.
    4. **Per-request input size:** text length, token sequence, and number of label descriptions evaluated.
    5. **Service/process footprint:** the application runtime plus models and any duplicated copies created by multiple worker processes.

    The repository gives rough references for the first two categories, but it does not measure peak memory or total service memory. Actual use depends on device, PyTorch/Transformers versions, allocator behavior, process count, and cached files.

    ## Current Classification Pipeline Size

    ### Models and task sizes

    | Component | Current role | Approximate size / work |
    |---|---|---|
    | LUKE (`studio-ousia/luke-large-lite` architecture) | Fine-tuned multi-label SDG classifier | Approximately 1.7 GB of checkpoint weights according to comments in the inference/model code. The full model is loaded once per backend worker process. |
    | MPNet (`sentence-transformers/all-mpnet-base-v2`) | Semantic similarity model for the ensemble and recommendation helper | The embedder comments cite about 420 MB per copy. Current code shares one instance between its call sites within a process. |
    | SDG output space | One model score per SDG | 17 output scores from LUKE; 17 summary-to-description similarities from the ensemble. |
    | Repository text | Input to both ensemble models | Summary is sliced to at most 6,000 characters before classification. LUKE tokenization truncates at 512 tokens and pads to exactly 512 tokens. |
    | Recommendation text | Optional post-classification diagnostic | Uses combined description/summary for a 20-word gate and keyword checks. If signals are found, MPNet embeds the submitted description and the 17 SDG descriptions. |

    The 1.7 GB reference should be interpreted as an approximate checkpoint/weight scale, not a promise that the process uses exactly 1.7 GB. Loading can temporarily require more than the final parameter footprint. In CUDA mode, LUKE parameters are converted to half precision for the resident model, reducing parameter storage relative to full precision; this does not mean every part of the process or load path uses half precision.

    ### Per-process model count

    For the normal in-process configuration, one Python backend process eventually holds:

    - At most one LUKE model instance, once loaded.
    - At most one tokenizer instance, once loaded.
    - At most one MPNet `SentenceTransformer` instance, once loaded.

    This is **per process**, not shared across operating-system processes. If a deployment runs four Flask/Gunicorn worker processes and every worker handles a classification request, each worker can initialize its own LUKE and MPNet objects. That can multiply resident memory substantially. A single-process development run does not reveal that production multiplier.

    ## How the Current Pipeline Is Used

    The usual repository path is:

    ```text
    Browser
    -> Flask /api/classify_st_url
    -> repository provider: metadata, topics, README
    -> Groq summarizer, or local fallback summary
    -> LUKE inference: 17 classifier scores
    -> MPNet inference: summary versus 17 SDG descriptions
    -> weighted ensemble and ranking
    -> optional recommendation assessment
    -> output filter and JSON response
    ```

    The frontend also starts the Aurora request concurrently, but Aurora is a separate external classification path. It does not call LUKE. This document's model-size comparison is specifically about the local repository path and its LUKE inference boundary.

    ### Classification input and output

    The repository summary text is cut to 6,000 characters. LUKE tokenizes the text, truncating to 512 tokens and padding to a fixed length of 512. It produces 17 logits, which are passed through sigmoid and rounded to four decimal places.

    MPNet encodes the summary and each of the 17 SDG descriptions as normalized vectors. The code computes their dot products (cosine similarities for normalized vectors), maps similarities through fixed bounds, and clips the resulting values to `[0, 1]`.

    The current ensemble weights the LUKE value at 0.3 and the MPNet similarity at 0.7:

    ```text
    final_score = 0.3 * luke_score + 0.7 * mpnet_similarity_score
    ```

    There are two relevant score cutoffs in the current route:

    - The repository classifier first selects scores `>= 0.3` and returns at most 10.
    - The Flask route then returns only predictions with scores strictly `> 0.4`.

    So the classifier may produce and rank 17 values, but the response is a short list of at most 10 values that also pass the route's stricter filter.

    ## When Each Model Is Loaded and Inferred

    ### LUKE

    LUKE loading is lazy in `backend/services/inference.py`:

    1. Importing the inference module defines constants and empty module-level slots; it does not load the checkpoint.
    2. `zero_shot_scores()` is called by the repository classifier after repository text has been fetched and summarized.
    3. With no non-empty `MODEL_SERVICE_URL`, it calls `predict_scores()` in-process.
    4. `predict_scores()` calls `load()`. On the first call in that process, `load()` resolves the tokenizer/config, creates the architecture from config, downloads or reads the fine-tuned checkpoint, validates and loads all checkpoint parameters, chooses precision/device, and stores the model and tokenizer in module-level variables.
    5. That request then tokenizes and runs inference. Later calls reuse the loaded objects and skip model construction and checkpoint loading.

    The model class is created with `AutoModel.from_config()`, not `AutoModel.from_pretrained()`. This is intentional: the checkpoint contains every parameter required by the fine-tuned classifier, so downloading pretrained LUKE weights and immediately overwriting them would be redundant. An explicit coverage check and strict state-dict load ensure the checkpoint really is complete.

    ### MPNet

    MPNet has a separate lazy singleton in `backend/services/embedder.py`:

    1. Importing the embedder module does not instantiate `SentenceTransformer`.
    2. The first call to `get_embedder()` constructs the model.
    3. The instance is reused by repository scoring and recommendation assessment for the rest of that process.

    In the common ST URL request, repository ensemble scoring invokes MPNet after LUKE. The recommendation helper runs later in the Flask route and may invoke MPNet again if the combined text is at least 20 words and a keyword signal is present. If recommendation checks do not reach the signal-positive branch, they do not make an extra MPNet inference call.

    Model object reuse does not mean every calculation is cached. The current repository scoring encodes the same 17 SDG descriptions per request. The recommendation branch also encodes its SDG descriptions if activated. The weights are reused, but those embeddings are recomputed.

    ## Former Architecture: LUKE on `127.0.0.1:9010`

    The former arrangement used a dedicated Flask application under `models/`:

    ```text
    Backend Flask process
    -> HTTP POST http://127.0.0.1:9010/predict
    -> Model Flask process
    -> LUKE scores returned as JSON
    -> Backend continues MPNet ensemble and response processing
    ```

    The model service's port defaulted to 9010. Its `models/app.py` defined the tokenizer, architecture, checkpoint load, and model at module scope. In other words, when the model service process imported its app module, it initialized the LUKE model before the process reached `app.run()` and began serving `/predict`.

    The backend's old inference path posted the text to `/predict`, parsed the JSON scores, and then continued with its own repository scoring logic. That loopback HTTP hop was local machine communication, not a call to a remote model host. It nevertheless introduced another service dependency, another process to start and monitor, request serialization/parsing, and a need for the model-service port/configuration to agree with the backend.

    The old model service also exposed a `/similarities` endpoint and imported its embedding utilities. The normal repository classifier path called `/predict` for LUKE and performed its MPNet embedding scoring in the backend process. The two model endpoints should not be confused with the inference path used for every normal classification.

    ### Historical optimization chronology

    The speed-related changes happened in two distinct steps:

    1. **While LUKE still ran as a separate service**, commit `9d26879` changed its architecture construction to `AutoModel.from_config()` and loaded the fine-tuned checkpoint strictly. This removed the redundant base-model weight download/load. That optimization predates removing the service boundary.
    2. Commit `9bab31f` moved the LUKE code into `backend/services/inference.py` and retired `models/app.py`. It preserved the model input/output contract, switched the default caller from a loopback HTTP request to `predict_scores()`, and made loading lazy so the backend could bind its port before the large checkpoint was read.

    Thus, attributing the removal of redundant base-weight loading only to the in-process move would be inaccurate. The `from_config()` optimization was already present in the microservice version immediately before retirement.

    ## Cold-Start Comparison

    “Cold start” can refer to two different events. The distinction determines which architecture appears faster.

    ### Backend process startup/readiness

    **Current in-process design:** Flask imports the inference module, but does not load LUKE immediately. The backend can start and bind its API port before the large checkpoint is read. If no model request arrives, LUKE is never loaded in that process.

    **Former microservice design:** importing `models/app.py` loaded the tokenizer, architecture, and checkpoint before `app.run()` could serve port 9010. The model service therefore did not become ready until that eager initialization completed.

    **Result:** the current design is faster to make the backend HTTP process available and avoids making backend operation depend on a separately started model service. This is the defensible cold-start improvement.

    ### First classification after a cold process start

    **Current in-process design:** the first request that reaches LUKE inference performs the deferred model load inside the classification request, then runs inference. If assets are not cached, that load may include network downloads; if cached, it still must read and initialize the weights. The first request can therefore be substantially slower than later requests.

    **Former microservice design:** the LUKE load was paid during model-service startup. If the service had already finished starting and was warm when the backend request arrived, the first `/predict` did not need to load the model during that request. If both services had just been launched together, however, the overall system was not ready until the eager model-service startup completed.

    **Result:** current startup-to-listening is faster, but cold first-request latency is not automatically faster. It shifts initialization work from model-service startup to the first classifier request. If measuring time from “start all processes” to “first successful classification,” compare the complete stacks under the same cache, hardware, and readiness definition.

    ### Warm classification requests

    After both designs have loaded LUKE, model inference itself is materially the same computation: same fine-tuned architecture, fixed-length tokenization, 17 output scores, and (in the current code) the same in-process model forward pass. The current default removes one local HTTP request and JSON encode/decode round trip around LUKE scores. On loopback that overhead is normally small compared with a large transformer forward pass; this repository has no benchmark that quantifies the savings.

    The removal also simplifies operational startup: there is one default Flask backend process rather than a separate model process that must bind port 9010 and be reachable. It does not make transformer math faster by itself.

    ### Cold-start comparison table

    | Measurement | Former LUKE microservice | Current in-process default |
    |---|---|---|
    | Backend API can bind before LUKE weights load | No issue for API process itself, but model server readiness is separate | Yes; LUKE loading is lazy |
    | Model-service readiness | Waits for eager LUKE initialization before serving | No model service is required by default |
    | First LUKE request after model service is already warm | Inference plus local HTTP/JSON overhead | Not applicable after current process is warm; later calls are direct in-process inference |
    | First classification after a completely cold launch | Model load is paid before model-service readiness, then request/inference | Model load is paid inside the first request that reaches LUKE |
    | Base-model weight download avoided | Yes in the optimized pre-retirement version, via `from_config()` | Yes, also via `from_config()` |
    | Fine-tuned checkpoint still needs to be loaded | Yes | Yes |
    | Local `/predict` HTTP hop on default path | Yes | No |
    | Separate service/port configuration | Yes, default 9010 | No by default; optional remote mode remains |

    ## Optional Remote LUKE Mode Still Present

    The current code retains a compatibility branch: if `MODEL_SERVICE_URL` is set, `zero_shot_scores()` sends a POST request to that service's `/predict` endpoint instead of calling `predict_scores()` directly. It reads the environment variable at call time. With an empty or unset `MODEL_SERVICE_URL`, the current default is in-process inference.

    This means the repository still contains the integration seam for a remote model service, but it does not mean a service on port 9010 is automatically started. Deployment configuration must explicitly point to a running compatible service if remote mode is intended.

    ## What Determines the Real Footprint and Cold Start

    - **Model cache state:** a warm Hugging Face cache avoids downloading files, but not loading weights into each new process.
    - **Storage:** reading a large checkpoint from fast local SSD differs from network or slower storage.
    - **Device:** CPU versus CUDA changes inference performance and memory placement. The current loader uses half precision for the LUKE model on CUDA; CPU model parameters remain default precision.
    - **Worker count:** each Python worker can own independent model instances. More workers can improve concurrency but multiply model memory.
    - **Concurrent first requests:** module-level lazy loading avoids repeated loads once complete, but this implementation does not show an explicit load lock. Avoid assuming multiple simultaneous first requests are coalesced into exactly one initialization without testing the chosen WSGI/threading setup.
    - **MPNet load timing:** depending on request path and signal checks, MPNet may load on the first ST request's ensemble stage, or on a recommendation-only path for Aurora. Its cold load can add to that request.
    - **External stages:** repository fetches and optional Groq summarization occur before local LUKE scoring in the ST URL flow. Their network latency can exceed local model inference and is unaffected by merging the model service into the backend.
    - **Readiness definition:** “port is accepting HTTP,” “model weights are loaded,” and “first full classification has completed” are three different timestamps. A meaningful cold-start benchmark should record all three.

    ## How to Benchmark This Fairly

    The code contains no measured per-stage latency values. For a useful comparison, instrument both historical and current revisions and record at least:

    1. Process launch to backend API port accepting a lightweight health request.
    2. Process launch to LUKE model ready.
    3. First classification response after a fully cold launch.
    4. First classification response with Hugging Face files already cached.
    5. Median and p95 warm classification latency after several requests.
    6. Peak RAM and, when applicable, VRAM during model load and inference.

    Use the same machine, Python/PyTorch versions, device, model cache state, repository text, Groq configuration, and number of workers. Separate repository/Groq time from LUKE and MPNet time, otherwise external network variation will obscure the architecture comparison.

    ## Source Map

    Current implementation:

    - [backend/services/inference.py](backend/services/inference.py): lazy LUKE loader, checkpoint source, device choice, tokenization, inference, score contract.
    - [backend/services/sdg_model.py](backend/services/sdg_model.py): config-only architecture creation and model forward pass.
    - [backend/embedding_url.py](backend/embedding_url.py): default in-process versus optional `MODEL_SERVICE_URL` branch, MPNet scoring, ensemble, and thresholds.
    - [backend/services/embedder.py](backend/services/embedder.py): single process-wide MPNet instance and approximate prior duplicate footprint comment.
    - [backend/app.py](backend/app.py): API route that invokes the repository classifier and applies the final response filter.
    - [backend/services/repo_fetcher.py](backend/services/repo_fetcher.py): synchronous repository provider requests.
    - [backend/services/summariser.py](backend/services/summariser.py): optional Groq summary and fallback behavior.

    Historical implementation:

    - In commit `9d26879`, `models/app.py` loaded tokenizer, LUKE architecture, and checkpoint at module scope and defaulted the model server to port 9010; `models/classifier.py` built the architecture from config rather than downloading base weights.
    - Commit `9bab31f` retired `models/app.py`, moved inference into `backend/services/inference.py`, and changed the backend's default from HTTP `/predict` to in-process `predict_scores()`.
