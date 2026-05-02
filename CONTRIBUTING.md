# Contributing to UN SDG Advocate

Thank you for your interest in contributing to UN SDG Advocate. This guide explains how to set up the project locally, follow repository standards, and collaborate effectively with maintainers and the broader CHAOSS community.

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. Ways to Contribute](#2-ways-to-contribute)
  - [Good First Contributions](#good-first-contributions)
- [3. Before You Start](#3-before-you-start)
- [4. Local Setup](#4-local-setup)
- [5. Project Structure](#5-project-structure)
- [6. Coding Standards](#6-coding-standards)
- [7. Commit Message Guidelines](#7-commit-message-guidelines)
- [8. Testing Expectations](#8-testing-expectations)
- [9. API and External Service Considerations](#9-api-and-external-service-considerations)
- [10. Issue Workflow](#10-issue-workflow)
- [11. Pull Request Checklist](#11-pull-request-checklist)
- [12. Community](#12-community)
- [13. Security](#13-security)
- [14. Helpful Links](#14-helpful-links)

## 1. Introduction

**UN SDG Advocate** is an AI-assisted application that scores GitHub repositories against the [United Nations Sustainable Development Goals (SDGs)](https://sdgs.un.org/goals). Users supply a project name, a public GitHub URL, and a short description; the backend combines remote classifiers and local models, and the frontend presents editable results.

**Community context:** The project is maintained in connection with the **CHAOSS UN SDG working group** (see [README.md](./README.md#community)). It is also listed under the **Code4GoodTech Dedicated Mentoring Program (DMP) 2026**; contributors participating through DMP 2026 may also reference the dedicated [DMP 2026 issue template](.github/ISSUE_TEMPLATE/DMP_2026.yml).

Whether you are fixing a typo, improving SDG accuracy, or extending the API, your contributions are welcome.

## 2. Ways to Contribute

| Area | Examples |
|------|----------|
| **Code — frontend** | Next.js app UI, accessibility, API client (`frontend/services/api.ts`), results flow |
| **Code — backend** | Flask routes in `backend/app.py`, Aurora integration (`aurora_api.py`), sentence-transformer pipelines (`embedding_*.py`), GitHub fetch logic (`embedding_url.py`) |
| **Documentation** | README accuracy, setup notes, API examples, this file |
| **Bug fixes** | Crashes, wrong validation, failed GitHub fetches, CORS or env handling |
| **Testing / QA** | Manual runs through analyze → results → export; `npm run lint`; reporting regressions with steps to reproduce |
| **Research / SDG quality** | Comparing model outputs to ground truth, suggesting thresholds or label text in `sdg_constants.py`, responsible use of external classifiers |

### Good First Contributions

If you are new to the project, consider starting with:

- Documentation improvements (README, this guide, inline comments where clarity helps)
- Small UI fixes (layout, copy, loading states)
- Input validation and clearer error messages (frontend or Flask responses)
- Lint-driven cleanups that do not change behavior
- Test coverage or reproducible manual test notes (the repo is light on automated tests today)

## 3. Before You Start

1. **Read [README.md](./README.md)** for features, architecture summary, and community calls.
2. **Search existing open and closed issues** in the repository before opening a new one, to avoid duplicate work.
3. **Comment on an issue** before large refactors or multi-file features so maintainers can align on direction (README notes limited maintainer bandwidth—early coordination helps).
4. **Use a fork and a focused branch** (`feat/…`, `fix/…`, `docs/…`) and keep commits scoped to one concern where practical.

## 4. Local Setup

### Prerequisites

- **Node.js 18+** and **npm** ([nodejs.org](https://nodejs.org/en/download/))
- **Python 3.8+** ([python.org](https://www.python.org/downloads/))
- **Git**
- **Bash** (for `./bash.sh`): Git Bash or WSL on Windows, or any Unix shell where `chmod` applies

> **Note:** [README.md](./README.md) uses the example folder name `UNSDG-advocate`; your clone may be named differently (for example `UNSDG-classifier-tool-main`). Use your actual clone directory in the commands below.

### Option A — `bash.sh` quickstart (from repository root)

The script creates a Python virtual environment, installs backend dependencies, starts **Flask in the background**, then installs frontend packages and runs the **Next.js dev server** (foreground). On exit, the backend process is stopped.

```bash
chmod +x ./bash.sh
./bash.sh
```

On Windows without Bash, use **Option B** instead of relying on `bash.sh`.

### Option B — Manual setup

**Backend** (terminal 1):

```bash
cd backend
python3 -m venv myvenv
```

Activate the venv:

- **macOS / Linux:** `source ./myvenv/bin/activate`
- **Windows (cmd):** `myvenv\Scripts\activate.bat`
- **Windows (PowerShell):** `.\myvenv\Scripts\Activate.ps1`

Then:

```bash
pip install -r requirements.txt
python3 app.py
```

**Frontend** (terminal 2):

```bash
cd frontend
npm install
npm run dev
```

### URLs and ports

| Service | URL |
|---------|-----|
| Frontend (Next.js dev) | [http://localhost:3000](http://localhost:3000) |
| Backend (Flask) | [http://127.0.0.1:5000](http://127.0.0.1:5000) |

The frontend Axios client is configured with base URL `http://127.0.0.1:5000/` in `frontend/services/api.ts`. If you change the backend host or port, update that constant or introduce a shared env-based configuration in a follow-up.

### Environment variables (optional but important for some flows)

| Variable | Used in | Purpose |
|----------|---------|---------|
| `GITHUB_TOKEN` | `backend/embedding_url.py` | Optional **Bearer** token for `api.github.com` (higher rate limits; typical flows use public repos only). |
| `OSDG_TOKEN` | `backend/app.py` (`/api/osdg_api`) | Sent in request headers when calling the external OSDG endpoint configured in code. |

There is no committed `.env.example` in this tree; document new variables in README or here when you add them.

## 5. Project Structure

- **`frontend/`** — Next.js 15 app (`app/`), UI components (`components/`), shared types (`types/`), API wrapper (`services/api.ts`), Tailwind globals (`app/globals.css`), static assets (`public/`).
- **`backend/`** — Flask app (`app.py`), Aurora client (`aurora_api.py`), description and URL classifiers (`embedding_description.py`, `embedding_url.py`), SDG label metadata (`sdg_constants.py`), sample or cached data under `data/`, Python dependencies in `requirements.txt`.
- **`bash.sh`** — One-command local bootstrap (backend venv + `app.py` background + `npm run dev`).
- **`.github/ISSUE_TEMPLATE/`** — GitHub issue form(s), including **DMP 2026** project proposals.

## 6. Coding Standards

- **Python:** Follow **PEP 8** style; keep Flask handlers thin where possible and share parsing/validation helpers instead of duplicating request-field extraction. Match existing naming (`projectName` / `projectUrl` in JSON mirrors the frontend).
- **TypeScript / React / Next.js:** Use the existing **App Router** layout under `frontend/app/`. Prefer functional components and hooks as in `components/mainScreen.tsx`.
- **Linting:** Run `npm run lint` from `frontend/` (ESLint with `next/core-web-vitals` and TypeScript rules in `eslint.config.mjs`).
- **Tailwind CSS:** Prefer utility classes consistent with current screens (container, spacing, purple accent patterns). Avoid one-off inline styles unless necessary.
- **Modularity:** Colocate UI pieces in `components/`, keep API types in `types/`, and avoid hard-coding API URLs outside the API service layer.

## 7. Commit Message Guidelines

Conventional-style prefixes keep history readable:

| Prefix      | Use for                               |
|-------------|---------------------------------------|
| `feat:`     | New user-facing behavior or API       |
| `fix:`      | Bug fixes                             |
| `docs:`     | Documentation only                    |
| `refactor:` | Internal change without behavior change |
| `test:`     | Tests or lint config                  |
| `chore:`    | Tooling, dependencies, housekeeping   |

**Examples:**

- `feat: add error banner for failed Aurora classification`
- `fix: validate GitHub URL before ST URL classify`
- `docs: document OSDG_TOKEN in CONTRIBUTING`

## 8. Testing Expectations

This repository does **not** currently ship an automated Jest/pytest suite in-tree. Before opening a PR, please:

1. **Frontend:** `cd frontend && npm install && npm run lint && npm run dev` — confirm the app builds and the home flow loads.
2. **Backend:** `cd backend` (with venv active) — `python3 app.py`; hit `GET http://127.0.0.1:5000/api/hello` and exercise the POST routes you changed.
3. **End-to-end flow:** From the UI, submit a **public** `https://github.com/owner/repo` URL with name and description; confirm results or sensible errors.
4. **API failures:** Check browser devtools network tab and Flask logs for 4xx/5xx when testing bad URLs, missing description, or upstream errors.
5. **Resource-heavy paths:** Sentence-transformer and zero-shot paths download or load models on first use; allow time and sufficient disk/RAM when testing `classify_st_*` routes.

## 9. API and External Service Considerations

- **Aurora SDG API** — Called from `aurora_api.py` via `https://aurora-sdg.labs.vu.nl/classifier/classify/elsevier-sdg-multi`. This repository **does not document a fixed requests-per-second quota** for that service; treat it as a shared public endpoint and **avoid tight loops or load tests** against it from development machines.
- **GitHub REST API** — `embedding_url.py` issues several GETs per analysis (repo metadata, README, issues). Unauthenticated requests are subject to GitHub’s standard rate limits; set **`GITHUB_TOKEN`** for development if you hit HTTP 403 rate-limit responses.
- **OSDG** — The `/api/osdg_api` route posts to an external host and sends **`OSDG_TOKEN`** in headers. Only enable or test this path with a legitimate token and respect any terms of use supplied by the OSDG operators.

## 10. Issue Workflow

1. **Search** open and closed issues for duplicates.
2. **Bug reports:** Include OS, Python/Node versions, steps to reproduce, expected vs actual behavior, and relevant logs (browser console, Flask stdout).
3. **Feature requests:** Describe the user problem, proposed behavior, and affected areas (frontend/backend).
4. **Claiming work:** Comment on the issue you intend to pick up; for **DMP 2026**-style tickets, use the template fields (goals, acceptance criteria, mentors) so reviewers have context.

## 11. Pull Request Checklist

- [ ] **Linked issue** (e.g. “Closes #37”) when applicable
- [ ] **Focused branch** — one logical change set; no unrelated formatting sweeps
- [ ] **Lint / manual checks** — `npm run lint` for frontend changes; manual API smoke tests for backend
- [ ] **Docs updated** — README or CONTRIBUTING if behavior, ports, or env vars change
- [ ] **UI changes** — before/after screenshots or short screen recording in the PR description
- [ ] **No secrets** — no tokens, `.env` files, or private keys committed

**Suggested PR titles** (match the [commit prefix](#7-commit-message-guidelines) style when it fits):

- `docs: add CONTRIBUTING.md`
- `fix: validate GitHub URL input`
- `feat: improve batch repository analysis`

## 12. Community

- Join the **bi-weekly community call** linked from [README.md](./README.md#community) if you want synchronous coordination with CHAOSS UN SDG contributors.
- **Be patient and kind:** README explicitly calls out new maintainership and variable availability of past contributors—constructive reviews and clear PR descriptions help everyone.
- **Code of conduct:** There is **no** `CODE_OF_CONDUCT.md` in this repository at present. Follow respectful, inclusive collaboration norms consistent with CHAOSS and broader open source practice; if the project adds a formal code of conduct file later, treat it as the authoritative policy.

## 13. Security

- **Never commit** GitHub personal access tokens, OSDG tokens, or other secrets.
- Prefer **environment variables** (`GITHUB_TOKEN`, `OSDG_TOKEN`) for credentials and keep local-only values out of git history.
- Report sensitive vulnerabilities through the maintainers’ preferred security channel once one is published on GitHub; until then, avoid posting exploit details in public issues.

## 14. Helpful Links

- [README.md](./README.md) — Overview, features, quick start, API examples
- [LICENSE](./LICENSE) — MIT License (GW Open Source Program Office)
- [Community & mentoring (README)](./README.md#community) — Calls, CHAOSS context, DMP 2026
- [DMP 2026 issue template](.github/ISSUE_TEMPLATE/DMP_2026.yml)
- **CODE_OF_CONDUCT** — There is no `CODE_OF_CONDUCT.md` at the repository root today; see [§12 Community](#12-community). If the maintainers add one, it will supersede informal guidance for behavior expectations.

---

Thank you for helping improve UN SDG Advocate and the quality of SDG signals for open source projects.
