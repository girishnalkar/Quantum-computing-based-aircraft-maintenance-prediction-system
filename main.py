from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
import pennylane as qml
import heapq
import os
from rtree import index
from tensorflow.keras.models import load_model
import google.generativeai as genai

# ---------------- CONFIGURE AI AGENT ---------------- #
# Set your Gemini API key here or in your environment variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "#add your own GEMINI API KEY here")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)

# ---------------- GLOBAL STORAGE ---------------- #

maintenance_queue = []
history_vault = {}
score_history = {}

# ---------------- LOAD MODELS ---------------- #

with open("models/quantum_weights.pkl", "rb") as f:
    weights = pickle.load(f)

with open("models/scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

future_model = load_model("models/future_model.keras")

# ---------------- QUANTUM DEVICE ---------------- #

dev = qml.device("default.qubit", wires=4)

@qml.qnode(dev)
def q_circuit(weights, inputs):
    for i in range(4):
        qml.RY(inputs[i] * np.pi, wires=i)

    for l in range(2):
        for i in range(4):
            qml.CNOT(wires=[i, (i+1)%4])
        for i in range(4):
            qml.Rot(weights[l,i,0], weights[l,i,1], weights[l,i,2], wires=i)

    return qml.expval(qml.PauliZ(0))

# ---------------- R-TREE ---------------- #

p = index.Property()
idx = index.Index(properties=p)

hangar_data = {
    1: (28.5562, 77.1000, "Indira Gandhi International Airport (DEL)"),
    2: (19.0896, 72.8656, "Chhatrapati Shivaji Maharaj International Airport (BOM)"),
    3: (13.1986, 77.7066, "Kempegowda International Airport (BLR)"),
    4: (17.2403, 78.4294, "Rajiv Gandhi International Airport (HYD)"),
    5: (22.6547, 88.4467, "Netaji Subhas Chandra Bose International Airport (CCU)"),
    6: (13.0827, 80.2707, "Chennai International Airport (MAA)"),
    7: (23.0726, 72.6347, "Sardar Vallabhbhai Patel International Airport (AMD)"),
    8: (15.3808, 73.8314, "Goa International Airport (GOI)"),
    9: (11.1368, 77.0420, "Coimbatore International Airport (CJB)"),
    10: (8.4821, 76.9201, "Trivandrum International Airport (TRV)"),
    11: (18.5821, 73.9197, "Pune International Airport (PNQ)")
}

for h_id, (lat, lon, name) in hangar_data.items():
    idx.insert(h_id, (lat, lon, lat, lon))

# ---------------- HELPER FUNCTIONS ---------------- #

def smooth_score(engine_id, new_score, alpha=0.6):
    if engine_id not in score_history:
        score_history[engine_id] = []

    hist = score_history[engine_id]

    if len(hist) == 0:
        smoothed = new_score
    else:
        smoothed = alpha * new_score + (1 - alpha) * hist[-1]

    hist.append(smoothed)

    if len(hist) > 10:
        hist.pop(0)

    return smoothed


def get_trend(engine_id):
    hist = score_history.get(engine_id, [])

    if len(hist) < 3:
        return "Stable"

    if hist[-1] > hist[-2] > hist[-3]:
        return "Increasing Risk 📈"
    elif hist[-1] < hist[-2] < hist[-3]:
        return "Improving 📉"
    else:
        return "Stable"


def get_sequence(engine_id, window=10):
    data = history_vault.get(engine_id, [])

    if len(data) < 3:
        return None

    recent_data = data[-window:]
    # Pad with the oldest available data point if we have less than 10
    while len(recent_data) < window:
        recent_data.insert(0, recent_data[0])

    seq = np.array(recent_data)
    return seq.reshape(1, window, 4)

# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict-page")
def predict_page():
    return render_template("predict.html")

# ---------------- MAIN API ---------------- #

@app.route("/predict", methods=["POST"])
def predict():
    global maintenance_queue

    data = request.json

    engine_id = data.get("engine_id", "ENG-1")
    curr_lat = float(data.get("lat", 18.5204))
    curr_lon = float(data.get("lon", 73.8567))

    # ✅ REAL VALUES INPUT
    sensors = np.array([[
        float(data["s11"]),
        float(data["s12"]),
        float(data["s13"]),
        float(data["s15"])
    ]])

    # -------- STORE HISTORY -------- #
    if engine_id not in history_vault:
        history_vault[engine_id] = []

    history_vault[engine_id].append(sensors[0].tolist())

    # -------- SCALE -------- #
    scaled = scaler.transform(sensors)

    # -------- QUANTUM PREDICTION -------- #
    raw_score = float(q_circuit(weights, scaled[0]))
    score = smooth_score(engine_id, raw_score)

    # -------- STATUS -------- #
    if score > 0.35:
        status = "⚠ High Failure Risk"
    elif score > -0.1:
        status = "🟡 Moderate Risk"
    else:
        status = "✅ Engine Healthy"

    # -------- FUTURE PREDICTION -------- #
    sequence = get_sequence(engine_id)
    future_health = None
    future_status = "Not enough data"

    if sequence is not None:
        window = sequence.shape[1]
        seq_scaled = scaler.transform(sequence.reshape(-1, 4)).reshape(1, window, 4)

        future_raw = float(future_model.predict(seq_scaled, verbose=0)[0][0])
        future_health = smooth_score(engine_id + "_future", future_raw)

        if future_health < 0.3:
            future_status = "⚠ Future Failure Risk"
        elif future_health < 0.6:
            future_status = "🟡 Future Moderate Risk"
        else:
            future_status = "✅ Future Healthy"

        # Enforce Rule: If currently High Risk, future must remain High Risk
        if score > 0.35:
            future_status = "⚠ Future Failure Risk"
            if future_health >= 0.3:
                future_health = min(future_health, 0.29)

    # -------- PRIORITY QUEUE -------- #
    maintenance_queue[:] = [item for item in maintenance_queue if item[1] != engine_id]
    heapq.heapify(maintenance_queue)

    heapq.heappush(maintenance_queue, (-score, engine_id))

    sorted_queue = sorted(maintenance_queue)
    engine_ids = [eid for _, eid in sorted_queue]
    rank = engine_ids.index(engine_id) + 1

    # -------- NEAREST AIRPORT -------- #
    nearest = list(idx.nearest((curr_lat, curr_lon, curr_lat, curr_lon), 1))
    hangar_lat, hangar_lon, hangar_name = hangar_data[nearest[0]]

    # -------- AUTO DECISION AGENT -------- #
    trend_val = get_trend(engine_id)
    
    def generate_decision(score, future_health, trend, rank, hangar_name):
        if not GEMINI_API_KEY:
            return "⚠️ Real AI Agent is offline. Please paste your GEMINI_API_KEY in main.py (line 10) to activate the LLM decision engine."

        prompt = f"""
        You are an expert AI Aircraft Maintenance Director. Given the following telemetry for an aircraft engine, provide a short, dynamic, 2-sentence operational decision.
        Do not use generic text, make it unique and authoritative. Be urgent if scores are critical.
        
        Current Quantum Risk Score: {score} (higher than 0.35 is critical, higher than -0.1 is warning)
        Future LSTM Health Score: {future_health} (lower than 0.3 is critical)
        Degradation Trend: {trend}
        Nearest Hangar: {hangar_name}
        Priority Queue Rank: {rank}
        
        Output ONLY the final decision text.
        """
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"🚨 AI Agent API Error: {str(e)}"

    decision_text = generate_decision(score, future_health, trend_val, rank, hangar_name)

    # -------- RESPONSE -------- #
    return jsonify({
        "status": status,
        "score": round(score, 4),
        "trend": trend_val,
        "decision": decision_text,

        "future_health": round(future_health, 4) if future_health is not None else None,
        "future_status": future_status,

        "priority": f"Priority Rank: {rank}",
        "hangar": hangar_name,
        "processed_at": [curr_lat, curr_lon],
        "history_version": len(history_vault[engine_id]),
        "hangar_coords": [hangar_lat, hangar_lon]
    })

# ---------------- REPORT ---------------- #

@app.route("/report")
def report_page():
    # Sort queue ascending by score (lowest negative = highest anomaly)
    sorted_queue = sorted(maintenance_queue, key=lambda x: x[0])

    return render_template("report.html",
                           history=history_vault,
                           queue=sorted_queue)

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(debug=True)
