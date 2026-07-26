import os
import pickle
import numpy as np
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Load the trained Model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')

try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    print("Model loaded successfully.")
except Exception as e:
    model = None
    print(f"Error loading model: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model pickle file not loaded properly.'}), 500

    try:
        data = request.form
        
        # Extract features from form input
        gender = float(data.get('gender', 0))
        age = float(data.get('age', 20))
        study_hours = float(data.get('study_hours_per_week', 10))
        attendance_rate = float(data.get('attendance_rate', 80))
        parent_education = float(data.get('parent_education', 1))
        internet_access = float(data.get('internet_access', 1))
        extracurricular = float(data.get('extracurricular', 0))
        previous_score = float(data.get('previous_score', 70))
        final_score = float(data.get('final_score', 75))

        # Array of 9 feature values matching `feature_names_in_`
        features = np.array([[
            gender, age, study_hours, attendance_rate, 
            parent_education, internet_access, extracurricular, 
            previous_score, final_score
        ]])

        # Prediction
        prediction = model.predict(features)[0]
        
        # Decision function / Confidence score calculation
        try:
            decision_val = float(model.decision_function(features)[0])
            confidence = round(100 / (1 + np.exp(-decision_val)), 2)
        except Exception:
            confidence = 85.0  # Fallback visualization percentage

        # Analytics for visual charting
        radar_metrics = {
            'Study Effort': min(100, (study_hours / 40) * 100),
            'Attendance': attendance_rate,
            'Academic History': previous_score,
            'Recent Score': final_score,
            'Environment Index': ((parent_education + internet_access + extracurricular) / 3) * 100
        }

        return jsonify({
            'success': True,
            'prediction': str(prediction),
            'confidence': confidence,
            'metrics': radar_metrics,
            'decision_value': round(decision_val, 3)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
