import os
import pickle
import numpy as np
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

MODEL_PATH = 'model.pkl'

# Load the model directly using pickle
model = None
if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" data-theme="emerald">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Student Performance Analytics Dashboard</title>
    <!-- Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root[data-theme="emerald"] {
            --bg-primary: #0b132b;
            --bg-secondary: #1c2541;
            --bg-card: rgba(28, 37, 65, 0.7);
            --accent-primary: #10b981;
            --accent-secondary: #06b6d4;
            --accent-gradient: linear-gradient(135deg, #10b981, #06b6d4);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border-color: rgba(255, 255, 255, 0.1);
            --shadow-glow: 0 10px 30px -10px rgba(16, 185, 129, 0.3);
            --input-bg: rgba(15, 23, 42, 0.6);
        }

        :root[data-theme="cyber"] {
            --bg-primary: #09090e;
            --bg-secondary: #161623;
            --bg-card: rgba(22, 22, 35, 0.85);
            --accent-primary: #ff007f;
            --accent-secondary: #7928ca;
            --accent-gradient: linear-gradient(135deg, #ff007f, #7928ca);
            --text-main: #ffffff;
            --text-muted: #a0a0b8;
            --border-color: rgba(255, 0, 127, 0.2);
            --shadow-glow: 0 10px 30px -10px rgba(255, 0, 127, 0.4);
            --input-bg: rgba(10, 10, 18, 0.8);
        }

        :root[data-theme="velvet"] {
            --bg-primary: #0f172a;
            --bg-secondary: #1e1b4b;
            --bg-card: rgba(30, 27, 75, 0.75);
            --accent-primary: #8b5cf6;
            --accent-secondary: #ec4899;
            --accent-gradient: linear-gradient(135deg, #8b5cf6, #ec4899);
            --text-main: #f8fafc;
            --text-muted: #cbd5e1;
            --border-color: rgba(139, 92, 246, 0.25);
            --shadow-glow: 0 10px 30px -10px rgba(139, 92, 246, 0.4);
            --input-bg: rgba(15, 23, 42, 0.7);
        }

        :root[data-theme="sunset"] {
            --bg-primary: #1c1917;
            --bg-secondary: #292524;
            --bg-card: rgba(41, 37, 36, 0.8);
            --accent-primary: #f97316;
            --accent-secondary: #eab308;
            --accent-gradient: linear-gradient(135deg, #f97316, #eab308);
            --text-main: #fafaf9;
            --text-muted: #a8a29e;
            --border-color: rgba(249, 115, 22, 0.2);
            --shadow-glow: 0 10px 30px -10px rgba(249, 115, 22, 0.35);
            --input-bg: rgba(12, 10, 9, 0.7);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            transition: background-color 0.3s ease, border-color 0.3s ease;
        }

        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }

        /* Glassmorphism Header */
        header {
            background: rgba(15, 23, 42, 0.6);
            backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--border-color);
            position: sticky;
            top: 0;
            z-index: 100;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 1.3rem;
            font-weight: 800;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .theme-selector {
            display: flex;
            gap: 8px;
            background: var(--input-bg);
            padding: 6px;
            border-radius: 30px;
            border: 1px solid var(--border-color);
        }

        .theme-btn {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            border: 2px solid transparent;
            cursor: pointer;
            transition: transform 0.2s;
        }

        .theme-btn:hover { transform: scale(1.15); }
        .theme-btn.active { border-color: var(--text-main); }

        .theme-btn[data-t="emerald"] { background: linear-gradient(135deg, #10b981, #06b6d4); }
        .theme-btn[data-t="cyber"] { background: linear-gradient(135deg, #ff007f, #7928ca); }
        .theme-btn[data-t="velvet"] { background: linear-gradient(135deg, #8b5cf6, #ec4899); }
        .theme-btn[data-t="sunset"] { background: linear-gradient(135deg, #f97316, #eab308); }

        /* Main Container Layout */
        .container {
            max-width: 1400px;
            margin: 2rem auto;
            padding: 0 1.5rem;
            display: grid;
            grid-template-columns: 1fr 1.1fr;
            gap: 2rem;
            width: 100%;
            flex: 1;
        }

        @media (max-width: 1024px) {
            .container { grid-template-columns: 1fr; }
        }

        /* Glass Cards */
        .card {
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            animation: fadeIn 0.6s ease-out forwards;
        }

        .card-header {
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .card-title {
            font-size: 1.25rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .card-title i {
            color: var(--accent-primary);
        }

        /* Form Grid Controls */
        .form-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.2rem;
        }

        @media (max-width: 640px) {
            .form-grid { grid-template-columns: 1fr; }
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .form-group.full-width {
            grid-column: span 2;
        }

        label {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        input, select {
            width: 100%;
            padding: 0.75rem 1rem;
            background: var(--input-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            color: var(--text-main);
            font-family: inherit;
            font-size: 0.95rem;
            outline: none;
            transition: all 0.2s ease;
        }

        input:focus, select:focus {
            border-color: var(--accent-primary);
            box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
        }

        /* Submit Button */
        .submit-btn {
            margin-top: 1.5rem;
            width: 100%;
            padding: 1rem;
            border: none;
            border-radius: 12px;
            background: var(--accent-gradient);
            color: white;
            font-weight: 700;
            font-size: 1rem;
            cursor: pointer;
            box-shadow: var(--shadow-glow);
            transition: transform 0.2s, box-shadow 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }

        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 35px -5px rgba(0,0,0,0.5);
        }

        .submit-btn:active { transform: translateY(0); }

        /* Results & Dashboard Dashboard Styling */
        .analytics-panel {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        .result-card {
            background: rgba(15, 23, 42, 0.5);
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: relative;
            overflow: hidden;
        }

        .result-card::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 6px;
            background: var(--accent-gradient);
        }

        .prediction-badge {
            font-size: 2rem;
            font-weight: 800;
            padding: 0.2rem 1.5rem;
            border-radius: 30px;
            letter-spacing: 1px;
            text-transform: uppercase;
            animation: pulse 2s infinite;
        }

        .badge-pass { background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; }
        .badge-fail { background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid #ef4444; }

        .chart-container {
            position: relative;
            height: 300px;
            width: 100%;
            margin-top: 1rem;
        }

        /* Keyframe Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.03); }
            100% { transform: scale(1); }
        }

        /* Status Banner */
        .status-alert {
            padding: 0.8rem 1rem;
            border-radius: 10px;
            font-size: 0.85rem;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .status-success { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
        .status-warning { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    </style>
</head>
<body>

    <header>
        <div class="logo">
            <i class="fa-solid fa-microchip"></i>
            <span>SVC Model Analytics</span>
        </div>
        <div class="theme-selector">
            <div class="theme-btn active" data-t="emerald" title="Emerald Dark"></div>
            <div class="theme-btn" data-t="cyber" title="Cyberpunk Neon"></div>
            <div class="theme-btn" data-t="velvet" title="Royal Velvet"></div>
            <div class="theme-btn" data-t="sunset" title="Sunset Amber"></div>
        </div>
    </header>

    <div class="container">
        <!-- Input Section -->
        <div class="card">
            <div class="card-header">
                <div class="card-title">
                    <i class="fa-solid fa-sliders"></i> Feature Parameters
                </div>
            </div>

            {% if not model_loaded %}
            <div class="status-alert status-warning">
                <i class="fa-solid fa-triangle-exclamation"></i>
                `model.pkl` not detected. Using heuristic fallbacks for display.
            </div>
            {% else %}
            <div class="status-alert status-success">
                <i class="fa-solid fa-circle-check"></i>
                Model file loaded successfully!
            </div>
            {% endif %}

            <form id="predictionForm">
                <div class="form-grid">
                    <div class="form-group">
                        <label>Gender</label>
                        <select name="gender">
                            <option value="0">Female</option>
                            <option value="1">Male</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Age</label>
                        <input type="number" name="age" value="18" min="10" max="100" required>
                    </div>

                    <div class="form-group">
                        <label>Weekly Study (hrs)</label>
                        <input type="number" step="0.1" name="study_hours" value="15.5" required>
                    </div>

                    <div class="form-group">
                        <label>Attendance Rate (%)</label>
                        <input type="number" step="0.1" name="attendance" value="85.0" min="0" max="100" required>
                    </div>

                    <div class="form-group">
                        <label>Parent Education Level</label>
                        <select name="parent_edu">
                            <option value="0">High School</option>
                            <option value="1" selected>Bachelor's</option>
                            <option value="2">Master's</option>
                            <option value="3">Doctorate</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Internet Access</label>
                        <select name="internet">
                            <option value="1">Yes</option>
                            <option value="0">No</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Extracurriculars</label>
                        <select name="extracurricular">
                            <option value="1">Yes</option>
                            <option value="0">No</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Previous Score</label>
                        <input type="number" step="0.1" name="prev_score" value="72.5" required>
                    </div>

                    <div class="form-group full-width">
                        <label>Final Score (Current/Midterm)</label>
                        <input type="number" step="0.1" name="final_score" value="78.0" required>
                    </div>
                </div>

                <button type="submit" class="submit-btn">
                    <i class="fa-solid fa-chart-line"></i> Run Machine Prediction
                </button>
            </form>
        </div>

        <!-- Dashboard Output Analytics -->
        <div class="analytics-panel">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">
                        <i class="fa-solid fa-square-poll-vertical"></i> Output Prediction
                    </div>
                </div>

                <div class="result-card">
                    <div>
                        <div style="font-size: 0.85rem; color: var(--text-muted);">PREDICTED TARGET</div>
                        <div style="font-size: 1.1rem; font-weight: 600; margin-top: 4px;">Student Status</div>
                    </div>
                    <div id="predictionResult" class="prediction-badge badge-pass">--</div>
                </div>

                <div class="chart-container">
                    <canvas id="analyticsChart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Theme Switcher Logic
        const themeBtns = document.querySelectorAll('.theme-btn');
        themeBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                themeBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const theme = btn.getAttribute('data-t');
                document.documentElement.setAttribute('data-theme', theme);
                updateChartColors();
            });
        });

        // Initialize Dynamic Chart
        const ctx = document.getElementById('analyticsChart').getContext('2d');
        let chart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Study Hours', 'Attendance', 'Prev Score', 'Final Score', 'Parent Edu (x25)'],
                datasets: [{
                    label: 'Metrics Normalized Score',
                    data: [60, 85, 72.5, 78, 25],
                    backgroundColor: 'rgba(16, 185, 129, 0.2)',
                    borderColor: '#10b981',
                    borderWidth: 2,
                    pointBackgroundColor: '#06b6d4'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        pointLabels: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', size: 11 } },
                        ticks: { display: false }
                    }
                },
                plugins: {
                    legend: { labels: { color: '#f8fafc', font: { family: 'Plus Jakarta Sans' } } }
                }
            }
        });

        function updateChartColors() {
            const style = getComputedStyle(document.documentElement);
            const primary = style.getPropertyValue('--accent-primary').trim();
            const secondary = style.getPropertyValue('--accent-secondary').trim();

            chart.data.datasets[0].borderColor = primary;
            chart.data.datasets[0].pointBackgroundColor = secondary;
            chart.data.datasets[0].backgroundColor = primary + '33'; // hex opacity
            chart.update();
        }

        // Async Form Submission
        document.getElementById('predictionForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);

            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            const badge = document.getElementById('predictionResult');
            badge.innerText = data.prediction;

            if (data.prediction.toLowerCase() === 'yes') {
                badge.className = 'prediction-badge badge-pass';
            } else {
                badge.className = 'prediction-badge badge-fail';
            }

            // Update Radar Chart Metrics dynamically
            const studyNormalized = Math.min((data.features.study_hours / 30) * 100, 100);
            chart.data.datasets[0].data = [
                studyNormalized,
                data.features.attendance,
                data.features.prev_score,
                data.features.final_score,
                (data.features.parent_edu / 3) * 100
            ];
            chart.update();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, model_loaded=(model is not None))

@app.route('/predict', methods=['POST'])
def predict():
    try:
        gender = float(request.form.get('gender', 0))
        age = float(request.form.get('age', 18))
        study_hours = float(request.form.get('study_hours', 0))
        attendance = float(request.form.get('attendance', 0))
        parent_edu = float(request.form.get('parent_edu', 0))
        internet = float(request.form.get('internet', 0))
        extracurricular = float(request.form.get('extracurricular', 0))
        prev_score = float(request.form.get('prev_score', 0))
        final_score = float(request.form.get('final_score', 0))

        # Reconstruct feature array according to model schema
        features = np.array([[gender, age, study_hours, attendance, parent_edu, internet, extracurricular, prev_score, final_score]])

        if model:
            prediction = model.predict(features)[0]
        else:
            # Fallback evaluation metric if running standalone without PKL binary in directory
            prediction = "Yes" if (attendance > 75 and final_score > 50) else "No"

        return jsonify({
            'status': 'success',
            'prediction': str(prediction),
            'features': {
                'study_hours': study_hours,
                'attendance': attendance,
                'parent_edu': parent_edu,
                'prev_score': prev_score,
                'final_score': final_score
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
