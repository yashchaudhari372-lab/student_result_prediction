import os
import pickle
import numpy as np
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Load the SVM model using pickle
MODEL_PATH = "model.pkl"
if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
else:
    model = None

# Attractive UI Template with Modern Glassmorphism & Animations
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Performance Predictor</title>
    <style>
        :root {
            --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            --glass-bg: rgba(255, 255, 255, 0.07);
            --glass-border: rgba(255, 255, 255, 0.1);
            --accent-glow: linear-gradient(90deg, #6366f1, #a855f7);
            --text-main: #f8fafc;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }

        body {
            background: var(--bg-gradient);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem 1rem;
            overflow-x: hidden;
            position: relative;
        }

        /* Background Decorative Animated Blobs */
        body::before, body::after {
            content: '';
            position: absolute;
            width: 300px;
            height: 300px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(99,102,241,0.2) 0%, transparent 70%);
            z-index: 0;
            animation: float 8s ease-in-out infinite alternate;
        }
        body::before { top: 10%; left: 10%; }
        body::after { bottom: 10%; right: 10%; animation-delay: 4s; }

        @keyframes float {
            0% { transform: translateY(0) scale(1); }
            100% { transform: translateY(-20px) scale(1.1); }
        }

        .container {
            background: var(--glass-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 2.5rem;
            width: 100%;
            max-width: 650px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            z-index: 1;
            animation: fadeIn 0.8s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        h1 {
            text-align: center;
            margin-bottom: 0.5rem;
            background: var(--accent-glow);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2rem;
        }

        .subtitle {
            text-align: center;
            color: #94a3b8;
            font-size: 0.95rem;
            margin-bottom: 2rem;
        }

        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.2rem;
        }

        @media (max-width: 500px) {
            .grid { grid-template-columns: 1fr; }
        }

        .form-group {
            display: flex;
            flex-direction: column;
        }

        .form-group.full-width {
            grid-column: span 2;
        }
        @media (max-width: 500px) {
            .form-group.full-width { grid-column: span 1; }
        }

        label {
            font-size: 0.85rem;
            color: #cbd5e1;
            margin-bottom: 0.4rem;
            font-weight: 500;
        }

        input, select {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--glass-border);
            border-radius: 8px;
            padding: 0.75rem;
            color: white;
            font-size: 0.95rem;
            transition: all 0.3s ease;
            outline: none;
        }

        input:focus, select:focus {
            border-color: #6366f1;
            box-shadow: 0 0 10px rgba(99, 102, 241, 0.3);
        }

        button {
            margin-top: 1.5rem;
            width: 100%;
            padding: 0.85rem;
            border: none;
            border-radius: 8px;
            background: var(--accent-glow);
            color: white;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(168, 85, 247, 0.6);
        }

        button:active {
            transform: translateY(1px);
        }

        .result-box {
            margin-top: 2rem;
            padding: 1.2rem;
            border-radius: 10px;
            text-align: center;
            font-size: 1.2rem;
            font-weight: 600;
            animation: pulse 2s infinite alternate;
        }

        .result-Yes {
            background: rgba(34, 197, 94, 0.15);
            border: 1px solid rgba(34, 197, 94, 0.4);
            color: #4ade80;
        }

        .result-No {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.4);
            color: #f87171;
        }

        .error-box {
            background: rgba(234, 179, 8, 0.15);
            border: 1px solid rgba(234, 179, 8, 0.4);
            color: #fde047;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 1rem;
        }
    </style>
</head>
<body>

<div class="container">
    <h1>Performance Analytics</h1>
    <p class="subtitle">SVM Predictive Classification Engine</p>

    {% if not model_loaded %}
    <div class="error-box">
        ⚠️ Warning: <strong>model.pkl</strong> was not found or failed to load. Please make sure it is uploaded in the root directory.
    </div>
    {% endif %}

    <form method="POST" action="/predict">
        <div class="grid">
            <div class="form-group">
                <label for="gender">Gender</label>
                <select id="gender" name="gender" required>
                    <option value="0">Female (0)</option>
                    <option value="1">Male (1)</option>
                </select>
            </div>

            <div class="form-group">
                <label for="age">Age</label>
                <input type="number" id="age" name="age" step="any" placeholder="e.g. 18" required>
            </div>

            <div class="form-group">
                <label for="study_hours">Study Hours / Week</label>
                <input type="number" id="study_hours" name="study_hours" step="any" placeholder="e.g. 15" required>
            </div>

            <div class="form-group">
                <label for="attendance">Attendance Rate (%)</label>
                <input type="number" id="attendance" name="attendance" step="any" placeholder="e.g. 92" required>
            </div>

            <div class="form-group">
                <label for="parent_edu">Parent Education Level</label>
                <select id="parent_edu" name="parent_edu" required>
                    <option value="0">High School (0)</option>
                    <option value="1">College/Associate (1)</option>
                    <option value="2">Bachelor's Degree (2)</option>
                    <option value="3">Master's / Ph.D. (3)</option>
                </select>
            </div>

            <div class="form-group">
                <label for="internet">Internet Access</label>
                <select id="internet" name="internet" required>
                    <option value="1">Yes (1)</option>
                    <option value="0">No (0)</option>
                </select>
            </div>

            <div class="form-group">
                <label for="extracurricular">Extracurricular Activities</label>
                <select id="extracurricular" name="extracurricular" required>
                    <option value="1">Yes (1)</option>
                    <option value="0">No (0)</option>
                </select>
            </div>

            <div class="form-group">
                <label for="previous_score">Previous Score</label>
                <input type="number" id="previous_score" name="previous_score" step="any" placeholder="e.g. 78" required>
            </div>

            <div class="form-group full-width">
                <label for="final_score">Final Score Reference</label>
                <input type="number" id="final_score" name="final_score" step="any" placeholder="e.g. 82" required>
            </div>
        </div>

        <button type="submit">Execute Prediction</button>
    </form>

    {% if prediction %}
    <div class="result-box result-{{ prediction }}">
        Prediction Output: Class [ {{ prediction }} ]
    </div>
    {% endif %}
</div>

</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE, model_loaded=(model is not None), prediction=None)

@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return render_template_string(HTML_TEMPLATE, model_loaded=False, prediction="Model Error")
    
    try:
        # Extract features exactly matching the 9 variables inside feature_names_in_
        features = [
            float(request.form["gender"]),
            float(request.form["age"]),
            float(request.form["study_hours"]),
            float(request.form["attendance"]),
            float(request.form["parent_edu"]),
            float(request.form["internet"]),
            float(request.form["extracurricular"]),
            float(request.form["previous_score"]),
            float(request.form["final_score"])
        ]
        
        # Format for Scikit-Learn prediction
        input_data = np.array([features])
        prediction_val = model.predict(input_data)[0]
        
        return render_template_string(HTML_TEMPLATE, model_loaded=True, prediction=str(prediction_val))
    
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, model_loaded=True, prediction=f"Error processing input: {str(e)}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
