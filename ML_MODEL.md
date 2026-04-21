# ML Model — AI Answer Evaluator

A hybrid machine learning system that automatically scores student answers against a model answer, returning a mark out of 10 with a full breakdown of semantic similarity, keyword coverage, and answer completeness.

---

## Table of Contents

- [What It Does](#what-it-does)
- [How It Works](#how-it-works)
- [Technique & Why We Chose It](#technique--why-we-chose-it)
- [Comparison With Alternatives](#comparison-with-alternatives)
- [Project Structure](#project-structure)
- [How to Run](#how-to-run)
- [How to Use — Web UI](#how-to-use--web-ui)
- [How to Use — API](#how-to-use--api)
- [Scoring Breakdown](#scoring-breakdown)
- [Score Verdicts](#score-verdicts)
- [Known Limitations](#known-limitations)

---

## What It Does

Given two pieces of text — a **model answer** (the correct expected answer written by a lecturer) and a **student answer** — the system returns:

| Field | Type | Description |
|---|---|---|
| `final_score` | float (0–10) | The overall mark |
| `similarity` | float (0–1) | How close the meaning is to the model answer |
| `keyword_score` | float (0–1) | How much of the technical terminology was covered |
| `length_score` | float (0–1) | Whether the answer is appropriately complete |

Example response:
```json
{
  "final_score": 7.85,
  "similarity": 0.7812,
  "keyword_score": 0.6667,
  "length_score": 1.0
}
```

---

## How It Works

The system runs three independent components and combines them into one final score.

```
Student Answer ──┐
                 ├──► clean() ──► SentenceTransformer ──► 384-dim vectors
Model Answer  ───┘                                              │
                                                    cosine_similarity()
                                                                │
                                                    calibrate_similarity()  ← removes artificial floor
                                                                │
                                          ┌─────────────────────────────────┐
                                          │         combine_scores()         │
                                          │                                  │
                                          │  60% × semantic                  │
                                          │  30% × keyword_score()           │
                                          │  10% × length_score()            │
                                          └─────────────────────────────────┘
                                                                │
                                                      Final Score (0–10)
```

### Step 1 — Text Cleaning (`preprocessing.py`)

Before anything is fed into the model, both answers are cleaned:

- Lowercased
- Punctuation stripped — but **alphanumeric tokens are preserved** so technical terms like `3NF`, `HDFS`, `IPv4`, `O(log n)` survive intact
- Hyphens collapsed to spaces — `open-source` becomes `open source` (two matchable tokens)
- Extra whitespace removed

> Without this step, a student writing `3NF` would get zero keyword credit because the original code stripped all digits.

---

### Step 2 — Semantic Similarity (`model.py`)

Both cleaned answers are passed through `all-MiniLM-L6-v2`, a pre-trained transformer model. It converts each answer into a **384-dimensional vector** that represents its meaning in semantic space.

**Cosine similarity** is then computed between the two vectors:
- `1.0` = identical meaning
- `0.0` = completely unrelated

**Calibration** is applied after:
```
calibrated = (raw_similarity - 0.20) / (1.0 - 0.20)
```
This is necessary because `all-MiniLM-L6-v2` rarely produces cosine scores below `0.20` even for completely wrong answers — without calibration, a totally incorrect answer could still score 4–5/10 just from the semantic baseline. Calibration stretches the range to a true 0–1.

---

### Step 3 — Keyword Coverage (`scoring.py`)

Extracts the important technical words from both answers and checks how many of the model's keywords appear in the student's answer.

Two things make this fair:

1. **Stopword removal** — common words like `the`, `is`, `a`, `for` are ignored so only meaningful content words are compared
2. **Suffix stemming** — common word endings are stripped before matching:
   - `storage` → `stor`
   - `stores` → `stor`
   - `stored` → `stor`
   - `distributed` → `distribut`
   - `distributing` → `distribut`

   This means a student who **paraphrases correctly** is not penalised for not copying the exact words from the model answer.

```
keyword_score = matched_stemmed_keywords / total_model_keywords
```

---

### Step 4 — Length Score (`scoring.py`)

Checks whether the student's answer is appropriately complete relative to the model answer.

| Student length vs model length | Score |
|---|---|
| Below 30% | Linear penalty from 0 → 1 (genuinely too short) |
| 30% – 200% | Full marks — concise answers are fine |
| Above 200% | Gentle penalty, never below 0.5 — verbose ≠ wrong |

> The original implementation penalised answers shorter than 50% of the model answer, which unfairly punished students who wrote sharp, accurate, concise answers.

---

### Step 5 — Final Score (`scoring.py`)

```
final_score = (0.60 × semantic) + (0.30 × keyword) + (0.10 × length)
final_score = final_score × 10   # scale to 0–10
```

| Component | Weight | Reason |
|---|---|---|
| Semantic similarity | 60% | Meaning and conceptual correctness matter most |
| Keyword coverage | 30% | Technical terminology is critical in academic answers |
| Length score | 10% | Completeness signal only — not a proxy for quality |

---

## Technique & Why We Chose It

### Type of ML: Zero-Shot Transfer Learning

The system uses **zero-shot transfer learning** — a pre-trained model is applied directly to a new task without any fine-tuning or labelled training data.

The core technique is **Semantic Textual Similarity (STS)** using a **Sentence Transformer** — a BERT-based neural network fine-tuned specifically to produce meaningful sentence-level embeddings.

### The Model: `all-MiniLM-L6-v2`

| Property | Value |
|---|---|
| Architecture | BERT → 6 transformer layers (MiniLM distillation) → mean pooling |
| Output | 384-dimensional dense vector per sentence |
| Pre-trained on | 1 billion+ sentence pairs (contrastive learning) |
| Model size | ~22 MB |
| Inference | CPU-compatible, no GPU required |
| Source | `sentence-transformers/all-MiniLM-L6-v2` on Hugging Face |

It was chosen specifically because:
- It understands **meaning**, not just word overlap — `"stores data across nodes"` and `"distributed storage"` score as similar
- It is small enough to run on CPU without noticeable delay after the first load
- It requires no API key, no internet after the first download, and no cost per request
- It was pre-trained on academic and general text, making it well-suited for exam answer scoring

---

## Comparison With Alternatives

| Approach | Handles Paraphrasing | Needs Training Data | Runs Offline | Cost | Why Not Chosen |
|---|---|---|---|---|---|
| **SentenceTransformer (this project)** | ✅ Yes | ❌ None needed | ✅ Yes | Free | — Chosen |
| TF-IDF + Cosine | ❌ No | ❌ None needed | ✅ Yes | Free | Surface-level only — paraphrased correct answers score 0 |
| BM25 | ❌ No | ❌ None needed | ✅ Yes | Free | Same weakness as TF-IDF |
| Fine-tuned regression model | ✅ Yes | ✅ Hundreds of labelled pairs | ✅ Yes | Free | No labelled AUCA dataset exists |
| GPT-4 / LLM API | ✅ Excellent | ❌ None needed | ❌ No | Per request | External dependency, cost, slow, not offline |
| Word2Vec average | ⚠️ Partial | ❌ None needed | ✅ Yes | Free | Weaker than transformers, no sentence-level context |

---

## Project Structure

```
ml_model/
├── __init__.py          # Exports evaluate_answer and batch_evaluate
├── preprocessing.py     # Text cleaning — lowercasing, punctuation, token preservation
├── scoring.py           # keyword_score, length_score, calibrate_similarity, combine_scores
└── model.py             # Loads SentenceTransformer, runs evaluation pipeline

apps/assessments/
├── ai_evaluator.py      # Thin wrapper — decouples ml_model from Django
├── views.py             # evaluator_page, evaluate_view, batch_evaluate_view
├── urls.py              # URL routing for /assessments/
└── templates/
    └── assessments/
        └── evaluator.html   # Web UI
```

---

## How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

Key packages installed:
```
sentence-transformers>=2.7.0
torch>=2.0.0
pypdf>=4.0.0
Django==6.0.3
```

### 2. Set up environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### 3. Run migrations

```bash
python manage.py migrate
```

### 4. Start the server

```bash
python manage.py runserver
```

### 5. First request — model download

On the very first evaluation request, `all-MiniLM-L6-v2` (~22 MB) will be downloaded automatically from Hugging Face and cached locally. This happens once. All subsequent requests use the cached model.

You will see this in the terminal — it is normal:
```
Loading weights: 100%|████| 103/103 [00:00<00:00]
BertModel LOAD REPORT from: sentence-transformers/all-MiniLM-L6-v2
embeddings.position_ids | UNEXPECTED   ← safe to ignore
```

To silence the Hugging Face unauthenticated warning, add to `.env`:
```env
HF_TOKEN=your_huggingface_token
```
This is optional — the model works without it.

---

## How to Use — Web UI

1. Log in at `http://127.0.0.1:8000/` using Staff credentials:
   - Email: `staff@auca.ac.rw`
   - Password: `staff123`

2. From the dashboard, scroll below the Finance & Announcements section and click **Open Evaluator** in the AI Tools card.

3. On the evaluator page at `/assessments/`:

   **Type Answers tab:**
   - Paste the model (correct) answer in the left box
   - Paste the student answer in the right box
   - Click **Evaluate Answer**

   **Upload Files tab:**
   - Upload a `.txt` or `.pdf` file for the model answer
   - Upload a `.txt` or `.pdf` file for the student answer
   - Click **Evaluate Answer**

   **Quick Examples:**
   - Click any preset button (Big Data, Database, Web Dev, Data Structures, Software Eng.) to auto-fill both fields with a sample pair

4. The result card appears below with:
   - Score circle showing the final mark out of 10
   - Verdict badge (Excellent / Good / Average / Poor)
   - Three animated progress bars for Semantic Similarity, Keyword Coverage, and Answer Length

> The evaluator is only accessible to **Staff** and **Lecturer** roles. Students are redirected to the login page.

---

## How to Use — API

The evaluator exposes two REST endpoints.

### Single Evaluation

**`POST /assessments/evaluate/`**

**JSON request:**
```bash
curl -X POST http://127.0.0.1:8000/assessments/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{
    "model_answer": "Hadoop is an open-source framework for distributed storage and processing of large datasets using HDFS and MapReduce.",
    "student_answer": "Hadoop stores and processes big data across multiple machines using HDFS for storage and MapReduce for computation."
  }'
```

**File upload request:**
```bash
curl -X POST http://127.0.0.1:8000/assessments/evaluate/ \
  -F "model_file=@model_answer.txt" \
  -F "student_file=@student_answer.txt"
```

**Response:**
```json
{
  "final_score": 8.45,
  "similarity": 0.8123,
  "keyword_score": 0.7500,
  "length_score": 1.0
}
```

---

### Batch Evaluation

**`POST /assessments/evaluate/batch/`**

Evaluate multiple answer pairs in one request. All texts are encoded in a single forward pass for efficiency.

```bash
curl -X POST http://127.0.0.1:8000/assessments/evaluate/batch/ \
  -H "Content-Type: application/json" \
  -d '{
    "pairs": [
      ["Student answer one.", "Model answer one."],
      ["Student answer two.", "Model answer two."],
      ["Student answer three.", "Model answer three."]
    ]
  }'
```

**Response:**
```json
{
  "results": [
    { "final_score": 8.45, "similarity": 0.8123, "keyword_score": 0.75, "length_score": 1.0 },
    { "final_score": 5.20, "similarity": 0.5400, "keyword_score": 0.50, "length_score": 1.0 },
    { "final_score": 2.10, "similarity": 0.2200, "keyword_score": 0.20, "length_score": 0.60 }
  ]
}
```

---

### Error Responses

| Status | Cause | Response |
|---|---|---|
| `400` | Missing student or model answer | `{"error": "Both student_answer and model_answer are required."}` |
| `400` | Unsupported file type | `{"error": "Unsupported file type: file.docx. Use .txt or .pdf"}` |
| `400` | Invalid JSON body | `{"error": "Invalid JSON body."}` |
| `500` | Model inference failure | `{"error": "Evaluation failed.", "detail": "..."}` |

---

## Scoring Breakdown

### Semantic Similarity

Measures how close the **meaning** of the student answer is to the model answer using transformer embeddings. This is the most important component — it catches correct answers even when the student uses completely different words.

- `0.9+` — near-identical meaning
- `0.6–0.9` — same concept, different wording
- `0.3–0.6` — partially related
- `0.0–0.3` — unrelated or wrong

### Keyword Coverage

Measures how much of the **technical vocabulary** from the model answer appears in the student answer, after stemming. Important for academic subjects where specific terminology is expected.

- `1.0` — all key terms covered
- `0.5–0.9` — most terms covered
- `0.0–0.5` — significant terminology missing

### Length Score

A soft completeness check. It does **not** reward longer answers — it only penalises answers that are genuinely too short (under 30% of model length) to have covered the topic.

- `1.0` — appropriate length (30%–200% of model answer)
- `0.5–1.0` — slightly too short or slightly too long
- `0.0–0.5` — very short, likely incomplete

---

## Score Verdicts

| Score Range | Verdict | Meaning |
|---|---|---|
| 8.0 – 10.0 | Excellent Answer | Correct meaning, strong terminology, complete |
| 6.0 – 7.9 | Good Answer | Mostly correct, minor gaps in terminology or detail |
| 4.0 – 5.9 | Average Answer | Partially correct, missing key concepts or terms |
| 0.0 – 3.9 | Poor Answer | Incorrect, off-topic, or far too short |

---

## Known Limitations

- **Acronym expansion** — `HDFS` and `Hadoop Distributed File System` are treated as different keywords. A student who spells out the full name instead of using the acronym may lose keyword points even though they are correct.

- **Model answer quality** — the system scores relative to the model answer. If the lecturer writes a vague or incomplete model answer, scores will be unreliable.

- **Logical errors** — the system cannot detect factual contradictions. A student who writes fluent, confident, wrong information may score higher than expected on semantic similarity.

- **Language** — the model is optimised for English. Answers in French, Kinyarwanda, or mixed languages will produce unreliable scores.

- **Fine-tuning ceiling** — the most accurate possible version of this system would be a regression model fine-tuned on real AUCA exam answers with human-assigned scores. That would require a labelled dataset of several hundred scored answer pairs, which does not currently exist.

---

*Last updated: April 2026 — AUCA Intro to Big Data Project*
