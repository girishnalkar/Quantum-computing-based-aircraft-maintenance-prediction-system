✈️ QCAMP
AI + Quantum Computing based Aircraft Maintenance Prediction System
QCAMP is an intelligent aircraft engine monitoring system that predicts potential engine failures using Quantum Machine Learning and recommends the nearest maintenance hangar in real time.

The system combines:
Quantum Neural Network (Pennylane)
Flask Web Application
Spatial Search using R-Tree
Maintenance Priority Queue
Sensor Data Analysis

It simulates a next-generation aviation safety platform that airlines could use to monitor engines during flight and take preventive maintenance actions.

🚀 Features
🔮 Quantum Failure Prediction
Uses a 4-qubit quantum neural network built with Pennylane to predict engine health based on sensor values.

📡 Real-Time Sensor Processing
Accepts engine sensor inputs such as:
S11
S12
S13
S15
and predicts failure probability.

🛠 Maintenance Priority System
Engines predicted with high risk are automatically pushed into a priority maintenance queue using a max-heap.

🗺 Smart Hangar Recommendation
Uses R-Tree spatial indexing to find the nearest aircraft maintenance hangar.

Example hangars include:
Pune International Airport
Mumbai CSIA
HAL Nashik
Goa Dabolim Hangar
Nagpur MIHAN MRO Facility

📜 Engine History Vault
Stores prediction history for each engine ID to simulate predictive maintenance tracking.

📊 Maintenance Report Dashboard
Displays:
Engine prediction history
Maintenance priority queue
Hangar recommendations

🧠 System Architecture
Aircraft Sensors
       │
       ▼
Sensor Data Input (Web UI)
       │
       ▼
Data Scaling (Sklearn Scaler)
       │
       ▼
Quantum Neural Network
(Pennylane QNode)
       │
       ▼
Failure Risk Score
       │
       ├── Healthy → Continue Flight
       │
       └── High Risk
             │
             ▼
Maintenance Priority Queue
             │
             ▼
Nearest Hangar Recommendation
(R-Tree Spatial Search)

🖥 Web Interface
The application provides multiple pages:

Home Page
Landing page for the monitoring system.

Prediction Page
User enters:
Engine ID
Sensor values
Aircraft location
The model predicts engine health instantly.

Maintenance Report
Displays:
Engine prediction history
Priority maintenance queue
Recommended hangars

📂 Project Structure
QCAM
│
├── app.py
├── quantum_weights.pkl
├── scaler.pkl
│
├── templates
│   ├── index.html
│   ├── predict.html
│   └── report.html
│
├── static
|   ├── images
|        └── aircraft.jpeg
│   ├── style.css
│   └── script.js
│
└── README.md

#Note: preprocess.py, quantum_model.py and testing_script.py this files was used for training Quantum ML model

⚙️ Technologies Used
Backend:
Python
Flask
NumPy
Pickle

Quantum Machine Learning:
Pennylane
Quantum Neural Networks

Data Structures:
Heap Queue (Priority Queue)
R-Tree Spatial Index

Frontend:
HTML
CSS
JavaScript

🔬 Quantum Circuit
The model uses a 4-qubit variational quantum circuit:
Input encoded using RY rotations
Entanglement using CNOT gates
Trainable parameters using Rot gates

Output is measured using:
Expectation value of Pauli-Z

This value determines engine failure risk.

📊 Example Prediction Output
Status: ⚠ High Failure Risk
Failure Score: 0.74
Priority Rank: 2
Recommended Hangar: Mumbai CSIA Hangar
History Version: 5
Processed Location: [18.5204, 73.8567]

✈️ Real World Applications
This system can be used in:
Aircraft Predictive Maintenance
Airline Fleet Monitoring
Military Aviation Systems
Smart Airports
Autonomous Aircraft Diagnostics

🔮 Future Improvements
Real aircraft sensor dataset integration
Deep Quantum Neural Networks
Live aircraft tracking integration
Dashboard visualization
Cloud deployment
Edge AI for aircraft systems

👨‍💻 Author
Girish Nalkar
AI • Quantum Computing • Aviation Safety Systems
