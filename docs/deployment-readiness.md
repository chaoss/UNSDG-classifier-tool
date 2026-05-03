# Deployment Readiness Plan

This document maps the current application to the hosting and CI/CD part of
[DMP 2026 issue #8](https://github.com/chaoss/UNSDG-classifier-tool/issues/8).
It does not close the full MVP issue; the DPG registry evaluation and accuracy
work remain separate milestones.

## Recommended Hosting Shape

The current architecture is a split application:

- Next.js frontend in `frontend/`
- Flask backend in `backend/`
- External classifier services called from the backend
- GitHub API access for repository metadata

Because GitHub Pages cannot run the Flask backend or Python ML dependencies, a
static-only GitHub Pages deployment is not sufficient for the full tool. A
practical zero-budget MVP path is:

1. Host the Next.js frontend on a static/Node-capable frontend host.
2. Host the Flask backend on a Python-capable host.
3. Configure the frontend with `NEXT_PUBLIC_API_BASE_URL` so staging and
   production can point at different backend URLs without code changes.
4. Keep classifier endpoints, tokens, and rate-limit-sensitive settings outside
   source code through environment variables.

## Configuration

Frontend configuration:

```bash
cd frontend
cp .env.example .env.local
# Set NEXT_PUBLIC_API_BASE_URL to the hosted Flask API origin.
```

Backend configuration should keep external API endpoints and credentials in the
host environment. If PR #23 is merged first, the backend will have a centralized
`backend/config.py` and `backend/.env.example` for these values.

## CI/CD Baseline

This repository now includes `.github/workflows/ci.yml`, which runs on every
pull request and push to `main`:

- Python backend compile check with Python 3.11
- Frontend dependency install from `package-lock.json`
- ESLint
- TypeScript typecheck
- Next.js production build

That gives maintainers a merge gate before connecting a deployment provider.

## Follow-Up Work For #8

- Add a backend health endpoint for deployment monitoring.
- Add backend tests around API request/response contracts.
- Add deployment provider-specific instructions once maintainers choose the
  final no-budget hosting platform.
- Add the DPG registry evaluation spreadsheet/notebook for the 100-project and
  85% accuracy acceptance criteria.
- Add API throttling/backoff around Aurora and OSDG calls to preserve the
  documented one-request-per-second limit.
