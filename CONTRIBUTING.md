# Contributing to UNSDG Classifier Tool

Thank you for your interest in contributing! This project is part of the [CHAOSS](https://chaoss.community) community — A Linux Foundation project and we welcome contributors of all experience levels, whether this is your first open source contribution or your hundredth.

## Code of Conduct
 
All contributors are expected to follow the [CHAOSS Code of Conduct](https://chaoss.community/about/code-of-conduct/). Please read it before participating. We are committed to building a welcoming, inclusive, and respectful community for everyone.

## Ways to Contribute
 
You don't need to be a developer to contribute! There are many meaningful ways to help:
 
- **Code** — Fix bugs, implement features, improve performance
- **Design** — Improve UI/UX, create or refine SDG icon assets
- **Documentation** — Improve the README, add inline code comments, write usage guides
- **Testing** — Write or improve tests, report bugs with detailed reproduction steps
- **SDG Mapping** — Improve the keyword or semantic mappings used for classification
- **Outreach** — Share the project with open source communities who might benefit from it
- **Triage** — Help label, confirm, and prioritize GitHub issues

## Before You Start
 
- Check the [open issues](https://github.com/chaoss/UNSDG-classifier-tool/issues) to see what's being worked on.
- If you're new to the project, look for issues tagged **`good first issue`** or **`help wanted`**.
- For substantial changes (new features, architectural decisions), open an issue first to align with maintainers before writing code.
- Join the [CHAOSS Slack](https://join.slack.com/t/chaoss-workspace/shared_invite/zt-r65szij9-QajX59hkZUct82b0uACA6g) and introduce yourself in `#newcomers` or `#wg-un-sdg`.

---
 
## Development Setup
 
### Prerequisites
 
- [Node.js](https://nodejs.org/) v18 or higher
- [npm](https://www.npmjs.com/) or [yarn](https://yarnpkg.com/)
- A GitHub personal access token (for API access during development)
- Git

### Local Setup
 
1. **Fork the repository** on GitHub, then clone your fork:
   ```bash
   git clone https://github.com/<your-username>/UNSDG-classifier-tool.git
   cd UNSDG-classifier-tool
   ```
 
2. **Add the upstream remote** so you can pull in future updates:
   ```bash
   git remote add upstream https://github.com/chaoss/UNSDG-classifier-tool.git
   ```
 
3. **Install dependencies:**
   ```bash
   npm install
   ```
 
4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
 
   Then edit `.env` to add your GitHub personal access token:
   ```
   GITHUB_TOKEN=your_token_here
   ```
 
5. **Start the development server:**
   ```bash
   npm run dev
   ```
 
   The app should be running at `http://localhost:3000`.
---
