# Contributing to UN SDG Advocate

Thanks for your interest in contributing to this project.

## How to Contribute

1. Fork the repository and clone your fork locally.
2. Create a new branch for your work.
3. Make your changes in a focused, well-scoped commit.
4. Run the project locally and verify your changes.
5. Open a pull request against the main branch.

## Local Setup

This project has a Python backend and a Next.js frontend.

Backend:

```bash
cd backend
python3 -m venv myvenv
source ./myvenv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Contribution Guidelines

- Keep changes small and easy to review.
- Follow the existing code style and project structure.
- Include tests or validation steps when they apply to your change.
- Update documentation when your change affects usage or setup.
- Avoid unrelated refactors in the same pull request.

## Pull Request Checklist

- The branch is up to date with the latest main branch.
- The code builds and runs correctly.
- Any new behavior is described clearly in the pull request.
- Screenshots or logs are included when they help explain the change.

## Reporting Issues

If you find a bug or want to request a feature, open an issue with:

- A clear title
- Steps to reproduce
- Expected and actual behavior
- Relevant logs, screenshots, or links
- Create an issue beforehand and discuss with maintainers
