# ✈️ QCAMP: AI + Quantum Computing Aircraft Maintenance Prediction

**QCAMP** is an intelligent aircraft engine monitoring system that leverages **Quantum Machine Learning (QML)** to predict potential engine failures and recommend the nearest maintenance hangars in real-time.

By combining Quantum Neural Networks with spatial indexing and priority queuing, QCAMP simulates a next-generation aviation safety platform for preventive maintenance.

---

## 🚀 Key Features

* **🔮 Quantum Failure Prediction:** Uses a 4-qubit Variational Quantum Circuit (VQC) built with **PennyLane** to analyze engine health.
* **📡 Real-Time Sensor Processing:** Processes critical sensor inputs (S11, S12, S13, S15) to calculate failure probabilities.
* **🛠 Maintenance Priority System:** High-risk engines are automatically prioritized using a **Max-Heap** data structure.
* **🗺 Smart Hangar Recommendation:** Utilizes **R-Tree spatial indexing** to find the nearest MRO (Maintenance, Repair, and Overhaul) facility.
* **📜 Engine History Vault:** Tracks prediction history per Engine ID for long-term health monitoring.

---

## 🧠 System Architecture

The system flows from raw sensor data to quantum inference, ending with actionable maintenance logistics:

1. **Data Input:** Sensor values & aircraft coordinates via Flask Web UI.
2. **Preprocessing:** Data scaling using `Scikit-Learn`.
3. **Quantum Inference:** 4-qubit QNode processes data through RY rotations and CNOT entanglement.
4. **Decision Engine:** - ✅ **Healthy:** Continue flight monitoring.
    - ⚠️ **High Risk:** Trigger Priority Queue + R-Tree Hangar Search.



---

## 🔬 Quantum Circuit Design

The model utilizes a variational quantum circuit:
* **State Preparation:** Input features encoded using **RY rotations**.
* **Entanglement:** CNOT gates to create quantum correlations between sensors.
* **Measurement:** Expectation value of **Pauli-Z** operators to determine the risk score.

---

## 🛠 Technologies Used

| Category | Tools |
| :--- | :--- |
| **Backend** | Python, Flask, NumPy, Pickle |
| **Quantum ML** | PennyLane, Quantum Neural Networks |
| **Data Structures** | Max-Heap (Priority Queue), R-Tree (Spatial Index) |
| **Frontend** | HTML5, CSS3, JavaScript |

---

## 📂 Project Structure

QCAM/
├── app.py                # Main Flask Application
├── quantum_weights.pkl   # Trained QNN parameters
├── scaler.pkl            # Saved Sklearn scaler
├── templates/            # UI Components
│   ├── index.html
│   ├── predict.html
│   └── report.html
├── static/               # Assets
│   ├── style.css
│   └── script.js
└── README.md

## 📊 Example Output
* **Status:** ⚠️ High Failure Risk
* **Failure Score:** 0.74
* **Priority Rank:** 2
* **Recommended Hangar:** Mumbai CSIA Hangar
* **Processed Location:** [18.5204, 73.8567]

## 👨‍💻 Author
**Girish Nalkar** Specializing in AI, Quantum Computing, and Aviation Safety Systems.
