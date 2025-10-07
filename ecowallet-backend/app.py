import os
import json
import pathlib
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

DB_FILE = os.path.join('database', 'users.json')
os.makedirs('database', exist_ok=True)

def get_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump({}, f)
    
    try:
        with open(DB_FILE, 'r') as f:
            content = f.read().strip()
            if not content:
                with open(DB_FILE, 'w') as f:
                    json.dump({}, f)
                return {}
            return json.loads(content)
    except (json.JSONDecodeError, ValueError):
        with open(DB_FILE, 'w') as f:
            json.dump({}, f)
        return {}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_gemini_analysis(image_path):
    """
    Analyzes a receipt image using a single multimodal model call.
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')

        image_parts = [
            {
                "mime_type": "image/jpeg",
                "data": pathlib.Path(image_path).read_bytes()
            }
        ]
        
        prompt = f"""
        You are an AI sustainability assistant for an app called "EcoWallet".
        Analyze the items from the receipt image provided.
        
        Based on the items in the image, do the following:
        1. Calculate a "sustainabilityScore" from 1 (very poor) to 100 (excellent).
        2. Provide 3 specific, actionable suggestions for more sustainable alternatives.
        3. Estimate the "potentialMonthlySavings" in USD if the user switches to these alternatives.
        4. Provide a brief, one-sentence "summary" of the spending.

        Return the response ONLY in a valid JSON format with the following keys:
        "sustainabilityScore", "potentialMonthlySavings", "summary", "suggestions".
        Each object in the "suggestions" array should have "original", "alternative", and "reasoning".
        """
        
        response = model.generate_content([prompt, image_parts[0]])
        
        cleaned_json_string = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(cleaned_json_string)

    except Exception as e:
        print(f"An error occurred with Gemini: {e}")
        return None

@app.route('/api/analyze-receipt', methods=['POST'])
def analyze_receipt():
    files = request.files.getlist('files')
    if not files or all(file.filename == '' for file in files):
        return jsonify({"error": "No files provided"}), 400
    
    username = request.form.get('username')
    if not username:
        return jsonify({"error": "Username is required"}), 400

    results = []
    db = get_db()
    if username not in db:
        db[username] = {"history": []}

    for file in files:
        if file.filename == '':
            continue
            
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        analysis_result = get_gemini_analysis(filepath)

        #os.remove(filepath)
        
        if analysis_result:
            results.append(analysis_result)
            db[username]["history"].append(analysis_result)
            db[username]["latestScore"] = analysis_result.get("sustainabilityScore")
        else:
            error_result = {
                "sustainabilityScore": 0,
                "potentialMonthlySavings": 0,
                "summary": f"Failed to analyze {filename}",
                "suggestions": [],
                "error": f"Failed to analyze {filename}"
            }
            results.append(error_result)

    save_db(db)
    
    if not results:
        return jsonify({"error": "Failed to analyze any receipts"}), 500
    
    return jsonify(results)

@app.route('/api/analyze-receipt-single', methods=['POST'])
def analyze_receipt_single():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    username = request.form.get('username')

    if not username:
        return jsonify({"error": "Username is required"}), 400
        
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        analysis_result = get_gemini_analysis(filepath)

        #os.remove(filepath)
        
        if not analysis_result:
            return jsonify({"error": "Failed to analyze receipt"}), 500

        db = get_db()
        if username not in db:
            db[username] = {"history": []}
        db[username]["history"].append(analysis_result)
        db[username]["latestScore"] = analysis_result.get("sustainabilityScore")
        save_db(db)

        return jsonify(analysis_result)

@app.route('/api/user/<username>', methods=['GET'])
def get_user_data(username):
    db = get_db()
    user_data = db.get(username)
    if not user_data:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user_data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)