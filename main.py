from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
import pennylane as qml
import heapq 
from rtree import index 

app = Flask(__name__)

maintenance_queue = []

p = index.Property()
idx = index.Index(properties=p)

hangar_data = {
    1: (18.5821, 73.9197, "Pune International Airport (PNQ)"),
    2: (19.0896, 72.8656, "Mumbai CSIA Hangar (BOM)"),
    3: (18.4575, 73.8677, "Pune Institute of Aviation Tech"),
    4: (19.0433, 73.0233, "Navi Mumbai International (NMI)"),
    5: (21.0922, 79.0472, "Nagpur MRO Facility (MIHAN)"),
    6: (19.8762, 75.3933, "Aurangabad Airport Hangar (IXU)"),
    7: (16.6636, 74.2811, "Kolhapur Airport (KLH)"),
    8: (17.6775, 75.9064, "Solapur Maintenance Base"),
    9: (19.9789, 73.8278, "HAL Nashik Division (Ozar)"),
    10: (15.3789, 73.8273, "Goa Dabolim Hangar (GOI)")
}
for h_id, (lat, lon, name) in hangar_data.items():
    idx.insert(h_id, (lat, lon, lat, lon))

history_vault = {} 

with open("quantum_weights.pkl","rb") as f:
    weights = pickle.load(f)

with open("scaler.pkl","rb") as f:
    scaler = pickle.load(f)

dev = qml.device("default.qubit", wires=4)

@qml.qnode(dev)
def q_circuit(weights, inputs):
    for i in range(4):
        qml.RY(inputs[i] * np.pi, wires=i)
    for l in range(2):
        for i in range(4):
            qml.CNOT(wires=[i,(i+1)%4])
        for i in range(4):
            qml.Rot(weights[l,i,0], weights[l,i,1], weights[l,i,2], wires=i)
    return qml.expval(qml.PauliZ(0))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict-page")
def predict_page():
    return render_template("predict.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    
    curr_lat = float(data.get("lat", 18.5204)) 
    curr_lon = float(data.get("lon", 73.8567))

    engine_id = data.get("engine_id", "ENG-777")

    sensors = np.array([[
        float(data["s11"]),
        float(data["s12"]),
        float(data["s13"]),
        float(data["s15"])
    ]])

    if engine_id not in history_vault:
        history_vault[engine_id] = []
    history_vault[engine_id].append(sensors.tolist())
    version_count = len(history_vault[engine_id])

    scaled = scaler.transform(sensors)
    result = q_circuit(weights, scaled[0])
    score = float(result)

    priority_rank = "N/A"
    recommended_hangar = "None"

    if score > 0:
        status = "⚠ High Failure Risk"
        
        heapq.heappush(maintenance_queue, (-score, engine_id))
        priority_rank = f"Priority Rank: {len(maintenance_queue)}"
        
        nearest = list(idx.nearest((curr_lat, curr_lon, curr_lat, curr_lon), 1))
        recommended_hangar = hangar_data[nearest[0]][2]
    else:
        status = "✅ Engine Healthy"
        priority_rank = "Stable"
        recommended_hangar = "Stay on Route"

    return jsonify({
        "status": status,
        "score": score,
        "priority": priority_rank,        
        "hangar": recommended_hangar,     
        "history_version": version_count, 
        "processed_at": [curr_lat, curr_lon] 
    })

@app.route("/report")
def report_page():
    sorted_queue = sorted(maintenance_queue) 
    
    return render_template("report.html", 
                           history=history_vault, 
                           queue=sorted_queue)

if __name__ == "__main__":
    app.run(debug=True)