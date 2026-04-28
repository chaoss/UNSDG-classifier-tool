# UN SDG Advocate 🌍

An AI-powered tool that analyzes GitHub repositories and determines their alignment with the United Nations Sustainable Development Goals (SDGs). The application provides confidence scores for each of the 17 SDGs and can automatically create pull requests with the analysis results.

## Features

- 🔍 **Repository Analysis**: Analyzes GitHub repositories using AI to determine SDG alignment
- 📊 **Confidence Scoring**: Provides confidence levels (High/Medium/Low) for each SDG match
- ✏️ **Interactive Editing**: Edit and modify SDG predictions through an intuitive modal interface
- ➕ **Add/Remove SDGs**: Dynamically add or remove SDG predictions
- 📁 **Download the SDGs**: Download the SDG and upload it in your repository
- 💻 **Modern UI**: Clean, responsive React.js interface with real-time loading states

## Architecture

- **Frontend**: Next.js 14+ with TypeScript, Tailwind CSS, and React Icons
- **Backend**: Flask API with Aurora SDG API classifier
- **Integration**: GitHub API for pulling repository information

## Quick Start

### Prerequisites

- Node.js 18+ and npm (Download link: https://nodejs.org/en/download/)
- Python 3.8+ (Download link: https://www.python.org/downloads/)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd UNSDG-classifier-tool
```

### 2. Bash script approach

- Make sure you have all of your prerequisites installed in your local computer like Node.js and Python
- Make sure you are inside the folder.

```bash
chmod +x ./bash.sh
./bash.sh
```

### 3. Manual approach

### 3.1. Backend Setup

```bash
cd backend
python3 -m venv myvenv
source ./myvenv/bin/activate
pip install -r requirements.txt
python3 app.py
```

### 3.2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 4. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://127.0.0.1:5000

## Usage

1. **Enter GitHub URL**: Input any public GitHub repository URL
2. **Analyze**: Click "Let's find out" to start AI analysis
3. **Review Results**: View SDG predictions with confidence levels
4. **Edit (Optional)**: Use "Maybe, we need some edits" to modify predictions
5. **Create PR**: Click "Yes, Download SDG Analysis File" to create a pull request with results

## SDG Analysis Output

The tool generates a `unsdg.json` file containing:

```json
{
  "sdg_analysis": {
    "analyzed_at": "2025-01-11T10:30:00.000Z",
    "repository": "https://github.com/user/repo",
    "predictions": {
      "SDG 1": 0.85,
      "SDG 3": 0.72,
      "SDG 4": 0.91
    }
  }
}
```

## API Endpoints

### POST /api/classify

Analyzes a GitHub repository and its description for SDG alignment using Aurora SDG API.

**Request:**

- Project Name, Project Description and Github Url

**Response:**

```json
{
  "projectName": "XYZ",
  "projectUrl": "https://github.com/user/repo",
  "predictions": [
    {
      "prediction": 0.117522962,
      "sdg": {
        "@type": "sdg",
        "id": "http://metadata.un.org/sdg/4",
        "label": "Goal 4",
        "code": "4",
        "name": "Quality Education",
        "type": "Goal",
        "icon": "https://aurora-sdg-classifier.uni-due.de/resources/sdg_icon_4.png"
      }
    }
  ]
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

See LICENSE file for details.

## Support

For issues and questions:

- Check existing issues in the repository
- Create a new issue with detailed description
- Include logs and error messages when applicable

A responsive website for categorizing the open source projects into different UN SDG's goals that closely align with their repository by reading their directory.
