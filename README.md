# 🏏 Cricket Stats LLM

A comprehensive cricket statistics application that combines web search, LLM-powered code generation, and data visualization to provide detailed cricket player statistics and charts.

## 🌟 Features

- **Smart Search**: Searches the web for comprehensive cricket statistics
- **AI-Powered Analysis**: Uses LLMs to generate custom visualization code
- **Interactive Charts**: Creates professional bar charts showing player performance
- **Multi-Format Support**: Covers Test, ODI, and T20I cricket formats

## 🏗️ Architecture

```
cric_stats_llm/
├── backend/           # FastAPI backend service
│   ├── main.py       # Main API endpoints
│   ├── direct_search.py    # Web search functionality  
│   ├── coding_gen_test.py  # LLM code generation
│   └── docker_tmp/   # Generated charts and temp files
└── frontend/         # Streamlit frontend
    └── app.py       # Main UI application
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker Desktop (for chart generation)
- OpenAI API key
- Tavily API key (for web search)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd cric_stats_llm
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

### Running the Application

1. **Start the backend**
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

2. **Start the frontend** (in a new terminal)
   ```bash
   cd frontend
   streamlit run app.py --server.port 8501
   ```

3. **Access the application**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🎯 Usage

1. **Enter Player Name**: Type any cricket player's name (e.g., "Virat Kohli")
2. **Generate Stats**: Click "Get Stats" to search and analyze
3. **View Results**: See comprehensive statistics and visual charts
4. **Download Charts**: Save generated charts as PNG files

## 🔧 Configuration

### API Keys Required

- **OpenAI API**: For LLM-powered code generation
- **Tavily API**: For advanced web search capabilities

### Optional: Local LLM Setup

The application supports local LLM models via LM Studio:

1. Install [LM Studio](https://lmstudio.ai/)
2. Load models like `mistral-7b-instruct` or `deepseek-coder-6.7b`
3. Start local server on port 1234
4. Update `.env` with local model configurations

## 📊 Supported Statistics

- **Match Statistics**: Games played across all formats
- **Batting Records**: Runs scored, batting averages
- **Career Milestones**: Centuries, half-centuries
- **Format Breakdown**: Test, ODI, T20I separate analysis

## 🐛 Troubleshooting

### Common Issues

**Backend Connection Error**
```
❌ Cannot connect to backend server
```
- Ensure backend is running on port 8000
- Check firewall settings

**Chart Generation Failed**
```
⚠️ Chart was generated but could not be found
```
- Ensure Docker is running
- Check file permissions in `docker_tmp/` directory

**API Key Errors**
- Verify API keys in `.env` file
- Check API key validity and quotas

## 🛠️ Development

### Project Structure
- `backend/main.py`: FastAPI endpoints and main logic
- `backend/direct_search.py`: Web search and data parsing
- `backend/coding_gen_test.py`: LLM-based code generation
- `frontend/app.py`: Streamlit user interface

### Adding New Features
1. Backend endpoints in `main.py`
2. Search enhancements in `direct_search.py`
3. Chart modifications in the LLM prompts
4. UI improvements in `app.py`



---

**Built with**: FastAPI • Streamlit • AutoGen • OpenAI • Tavily • Docker 
