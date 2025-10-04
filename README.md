# Freakquency — Disease Risk Prediction & AI Recommendations

This repository contains a Streamlit web app that predicts a user's risk category for chronic diseases based on a short questionnaire and then provides AI-generated lifestyle recommendations. The app also includes a small rule-based chatbot for quick health tips.

## What it does
- Collects user inputs (age, gender, BMI, blood pressure, cholesterol, glucose, physical activity, smoking, alcohol intake, family history).
- Uses a pre-trained machine learning model (`model.pkl`) and a pre-fitted scaler (`scaler.pkl`) to predict one of several disease categories (e.g., Healthy, Diabetes, Cardiovascular Disorder, Cancer, Multi-condition Cases).
- Sends a short prompt to OpenAI to generate 3 practical lifestyle recommendations based on the predicted disease category.
- Provides a minimal keyword-based chatbot for quick answers about exercise, diet, blood pressure, cholesterol, and glucose.

## Files of interest
- `app.py` — Streamlit application entrypoint.
- `model.pkl` — Trained scikit-learn model used for prediction.
- `scaler.pkl` — Feature scaler used to transform input features before prediction.
- `chronic_disease_dataset.csv` — Dataset used during development (optional for running the app).
- `llm_recommender.pkl` — (Optional) additional recommender artifact.
- `requirements.txt` — Python dependencies.

## Requirements
- Python 3.8+ recommended
- The dependencies in `requirements.txt`. Main packages include: `streamlit`, `pandas`, `numpy`, `scikit-learn`, `joblib`, `openai`.

## Setup (Windows PowerShell)

1. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. Add your OpenAI API key to an environment variable. The app expects `OPENAI_API_KEY` to be available (the project uses `python-dotenv` if you prefer a `.env` file):

```powershell
$env:OPENAI_API_KEY = 'sk-...'
# or create a .env file in the same folder as app.py with:
# OPENAI_API_KEY=sk-...
```

Note: If you don't intend to use OpenAI (no API key), the app still works for predictions and the built-in fallback chatbot will answer some keyword queries. However, recommendations from OpenAI will not be available.

## Run the Streamlit app

From the `submissions/Freakquency/code/` folder run:

```powershell
streamlit run app.py
```

This will open the app in your default browser (or show a local URL in the terminal such as http://localhost:8501).

## Usage
1. Fill the questionnaire and click `Predict`.
2. The app will display the predicted disease category and a short description.
3. If OpenAI is configured, it will show 3 AI-generated lifestyle recommendations. Otherwise fallback recommendations are shown for certain keywords.
4. Use the text input at the bottom to ask the small rule-based chatbot questions (e.g., "exercise", "diet").

## Troubleshooting
- If `model.pkl` or `scaler.pkl` are missing, the app will fail at startup. Make sure both files are in the same folder as `app.py`.
- If you see OpenAI authentication errors, confirm that `OPENAI_API_KEY` is set correctly in your environment or `.env`.
- If Streamlit fails to start, ensure your Python path and virtual environment are correct and that `streamlit` is installed in the active environment.

## Security & Privacy
- Do not commit your OpenAI API key to version control. Use environment variables or a local `.env` file excluded from source control.
- This app is for demo/educational purposes only and does not replace professional medical advice.

## License
This project was created for the Oct-4 Hackathon 2025. Check the project or team repository for license details.

---
If you want, I can also add a brief CONTRIBUTING or LICENSE file, or update the README with screenshots and example inputs. What would you like next?
