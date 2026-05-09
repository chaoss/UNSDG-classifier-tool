# Development Guide 🛠️

Welcome! This guide helps you set up your development environment and understand the contribution workflow for the UN SDG Advocate tool.

## 📋 System Requirements

Before you begin, ensure you have the following installed:

- **Node.js**: `v18.0.0` or higher (Recommended: `v20.x`)
- **Python**: `v3.8` to `v3.11`
- **Git**: For version control

Verify your versions:
```bash
node --version
npm --version
python --version
```

---

## 💻 Setup Instructions

### Linux / macOS

1. **Clone and Setup**:
   ```bash
   git clone https://github.com/chaoss/UNSDG-classifier-tool.git
   cd UNSDG-classifier-tool
   ```

2. **Backend Setup**:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**:
   ```bash
   cd ../frontend
   npm install
   ```

### Windows (PowerShell)

1. **Clone the repository**:
   ```powershell
   git clone https://github.com/chaoss/UNSDG-classifier-tool.git
   cd UNSDG-classifier-tool
   ```

2. **Backend Setup**:
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
   *Note: If you get an "Execution Policy" error, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`*

3. **Frontend Setup**:
   ```powershell
   cd ..\frontend
   npm install
   ```

---

## 🔑 Environment Variables (Optional)

The application can function without these, but they are recommended for full feature support.

1. Navigate to the `backend/` directory.
2. Copy `.env.example` to `.env`:
   ```bash
   # Linux / macOS
   cp .env.example .env
   ```
   ```powershell
   # Windows PowerShell
   copy .env.example .env
   ```
3. Open `backend/.env` and add your tokens if needed:
   - `GITHUB_TOKEN`: Increases GitHub API rate limits. [Create one here](https://github.com/settings/tokens).
   - `OSDG_TOKEN`: Required only for the OSDG model tab.

---

## 🚀 Running the Application

Run the backend and frontend in separate terminal windows.

**Terminal 1 (Backend):**
```bash
cd backend
# Activate venv if not already active
source venv/bin/activate # Linux/macOS
# OR
.\venv\Scripts\Activate.ps1 # Windows
python app.py
```
*Expected: Running on http://127.0.0.1:5000*

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```
*Expected: Running on http://localhost:3000*

---

## ⚠️ Troubleshooting

### First-Time Model Download
The first time you run a classification (especially the Sentence Transformer models), the application will download large AI models (approx. 1.5GB - 2GB total). 
- **Symptom**: The backend may seem unresponsive while downloading.
- **Solution**: Monitor the backend terminal for progress. Ensure you have a stable internet connection.

### Windows: "Scripts cannot be loaded..."
- **Fix**: Run PowerShell as Administrator and execute: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Backend: "ModuleNotFoundError"
- **Fix**: Ensure your virtual environment is activated and you have run `pip install -r requirements.txt`.

---

## 🤝 Contribution Workflow

1. **Find an Issue**: Look for [good first issues](https://github.com/chaoss/UNSDG-classifier-tool/issues).
2. **Fork & Branch**: Fork the repo and create a branch: `git checkout -b feature/your-feature-name`.
3. **Commit**: Keep commits small and descriptive.
4. **Test**: Verify your changes locally (both frontend and backend).
5. **PR**: Submit a Pull Request with a clear description of your changes.
