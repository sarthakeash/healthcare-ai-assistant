# Healthcare Communication Assistant

An AI-powered tool for healthcare professionals to practice patient communication and receive detailed feedback using OpenAI's GPT models.

## Features

- 🏥 **Practice Scenarios**: Realistic healthcare communication scenarios
- 🤖 **AI Feedback**: Detailed analysis of communication skills
- 📊 **Progress Tracking**: Monitor improvement over time
- 🎯 **Skill Assessment**: Evaluation across multiple dimensions:
     - Medical Accuracy
     - Communication Clarity
     - Empathy & Tone
     - Completeness

## Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd healthcare-communication-assistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy environment template
cp .env.example .env

# Edit .env file and add your Gemini API key
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Start the Application

**Terminal 1 - Backend API:**

```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Streamlit Frontend:**

```bash
cd frontend
streamlit run app.py
```

### 4. Access the Application

- **Frontend**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs

## Project Structure

```
healthcare-communication-assistant/
├── backend/                  # FastAPI backend
│   ├── api/
│   │   └── routes/           # API endpoints (practice.py, results.py, scenarios.py)
│   ├── core/                 # Configuration and models (config.py, models.py)
│   ├── services/             # Business logic (transcription_service.py, storage_service.py, advanced_analysis_service.py, scenario_service.py)
│   ├── prompts/              # AI prompts (analysis_system_prompts.py)
│   ├── utils/                # Backend utilities (view_results.py)
│   ├── data/
│   │   └── results/
│   │       ├── attempts/     # Attempt JSONs
│   │       ├── feedback/     # Feedback JSONs
│   │       ├── daily_summaries/ # Daily summary JSONs
│   │       └── ...           # Complete result JSONs
│   │   └── scenarios/        # Scenario JSONs
│   ├── main.py               # Backend entrypoint
│   └── sample.txt            # Sample file
├── frontend/                 # Streamlit frontend
│   ├── app.py                # Main Streamlit app
│   ├── pages/                # App pages (1_🏥_Practice.py, 2_📊_Results.py)
│   ├── components/           # Reusable components (feedback_display.py, scenario_display.py)
│   └── utils/                # Frontend utilities (api_client.py)
├── data/
│   ├── scenarios/            # Practice scenarios (JSON)
│   └── results/              # (empty or legacy)
├── tests/                    # Test files
└── requirements.txt          # Python dependencies
```

## Usage

### Practice Mode

1. Navigate to the **Practice** page
2. Select a scenario from the dropdown
3. Read the scenario context and key points
4. Write your response as if speaking to the patient
5. Click "Analyze Response" to get AI feedback

### Results & Progress

1. Go to the **Results** page to view:
      - Overall performance metrics
      - Progress over time
      - Detailed breakdowns by skill category
      - Historical attempt reviews

## API Endpoints

### Scenarios

- `GET /api/v1/scenarios/` - List all scenarios
- `GET /api/v1/scenarios/{id}` - Get specific scenario

### Practice

- `POST /api/v1/practice/submit` - Submit practice attempt

### Results

- `GET /api/v1/results/feedback` - Get all feedback
- `GET /api/v1/results/attempts` - Get all attempts

## Configuration

### Environment Variables

| Variable         | Description          | Default                         |
| ---------------- | -------------------- | ------------------------------- |
| `GEMINI_API_KEY` | Gemini API key       | Required                        |
| `LLM_MODEL`      | Gemini model to use  | `gpt-4-turbo-preview`           |
| `DATABASE_URL`   | SQLite database path | `sqlite:///./healthcare_app.db` |

### Adding New Scenarios

Create JSON files in `data/scenarios/`:

```json
{
      "id": "scenario_new",
      "title": "Scenario Title",
      "description": "Brief description",
      "context": "Detailed scenario context...",
      "difficulty": "beginner|intermediate|advanced",
      "medical_area": "Medical specialty",
      "patient_type": "Patient description",
      "key_points": ["Point 1", "Point 2"]
}
```

## Development

### API Development

The FastAPI backend provides automatic API documentation at `/docs` when running in development mode.

## Troubleshooting

### Common Issues

**Backend not starting:**

- Check that port 8000 is available
- Verify OpenAI API key is set correctly
- Ensure all dependencies are installed

**Frontend not connecting:**

- Verify backend is running on port 8000
- Check CORS settings in backend configuration

**No scenarios loading:**

- Check that scenario JSON files exist in `data/scenarios/`
- Verify JSON format is valid

**Database errors:**

- Delete `healthcare_app.db` to reset the database
- Check file permissions in the project directory