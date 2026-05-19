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

## Making a Contribution
 
### 1. Find or Create an Issue
 
- Browse [open issues](https://github.com/chaoss/UNSDG-classifier-tool/issues).
- Comment on an issue to let others know you're working on it.
- If you've found a bug or have a feature idea not yet tracked, open a new issue first.
  
### 2. Fork and Branch
 
Always work on a dedicated branch, not directly on `main`:
 
```bash
# Sync with upstream first
git fetch upstream
git checkout main
git merge upstream/main
 
# Create a new branch
git checkout -b type/short-description
```
 
**Branch naming conventions:**
 
| Prefix | Use for |
|--------|---------|
| `feat/` | New features |
| `fix/` | Bug fixes |
| `docs/` | Documentation changes |
| `chore/` | Maintenance, dependency updates |
| `test/` | Adding or updating tests |
| `refactor/` | Code restructuring without behavior changes |
 
Examples: `feat/add-sdg-tooltip`, `fix/api-timeout-handling`, `docs/update-setup-guide`
 
### 3. Make Your Changes
 
- Keep changes focused on a single concern per pull request.
- Write clear, readable code with comments where the intent isn't immediately obvious.
- Update or add documentation if your change affects user facing behavior.
- If you're updating SDG mappings or classification logic, include a brief rationale in your PR description.

### 4. Test Your Changes
 
Before opening a PR, make sure all tests pass:
 
```bash
npm test
```
 
If you're adding new functionality, include tests that cover the new behavior. If you're fixing a bug, add a test that would have caught the bug.
 
### 5. Open a Pull Request
 
Push your branch to your fork:
 
```bash
git push origin type/short-description
```
 
Then open a pull request against the `main` branch of `chaoss/UNSDG-classifier-tool`.

## Pull Request Guidelines
 
A good pull request:
 
- **Has a clear title** — summarizes what the PR does (not just "fix bug" or "update code")
- **References the related issue** — include `Closes #<issue-number>` or `Related to #<issue-number>` in the description
- **Describes the change** — explain *what* you changed and *why*, not just *how*
- **Includes screenshots** for UI changes
- **Is focused** — one logical change per PR; split large changes into smaller ones if possible
- **Passes all CI checks** — the PR won't be merged if tests or linting fail
### PR Description Template
 
```markdown
## Summary
Brief description of what this PR does.
 
## Related Issue
Closes #<issue-number>
 
## Changes Made
- Change 1
- Change 2
 
## Screenshots (if applicable)
 
## Testing Done
Describe how you tested your changes.
 
## Checklist
- [ ] My code follows the project's coding standards
- [ ] I have updated relevant documentation
- [ ] I have added tests for new functionality
- [ ] All existing tests pass
```
 

## Commit Message Style
 
This project follows the [Conventional Commits](https://www.conventionalcommits.org/) specification.
 
**Format:** `type(scope): short description`
 
**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
 
**Examples:**
 
```
feat(classifier): add confidence scoring to SDG results
fix(ui): correct SDG icon alignment on mobile screens
docs(readme): update prerequisites section
chore(deps): upgrade node dependencies
```
 
Keep the subject line under 72 characters. Use the body to explain the *why* behind the change when it's not obvious from the title.
 
