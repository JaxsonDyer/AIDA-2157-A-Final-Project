from flask import Flask, render_template, jsonify, request
from briefings import evaluate_sensor_data

app = Flask(__name__)

# This will hold the trained models
TRAINED_MODELS = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/briefing", methods=["POST"])
def get_briefing():
    if not TRAINED_MODELS:
        return jsonify({"error": "Models not loaded"}), 500
    
    sensor_data = request.json or {}
    briefings = evaluate_sensor_data(TRAINED_MODELS, sensor_data)
    return jsonify(briefings)

def start_server(models):
    global TRAINED_MODELS
    TRAINED_MODELS = models
    print("\nStarting Web UI...")
    print("Open http://127.0.0.1:5000 in your browser.")
    app.run(host="0.0.0.0", port=5000, debug=False)
