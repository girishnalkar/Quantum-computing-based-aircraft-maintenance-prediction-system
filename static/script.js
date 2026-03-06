function goPredict(){
    window.location.href="/predict-page"
}

// COMBINED FUNCTION: Fetches location then triggers prediction
function runPrediction() {
    let resBox = document.getElementById("result");
    resBox.style.display = "block";
    resBox.innerHTML = "<h2>Fetching Location & Processing...</h2>";

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                // Success: Use real coordinates
                executePrediction(position.coords.latitude, position.coords.longitude);
            },
            (error) => {
                // Error: Fallback to default Pune coordinates
                console.warn("Location access denied. Using Pune as default.");
                executePrediction(18.5204, 73.8567);
            }
        );
    } else {
        // Browser doesn't support Geolocation
        executePrediction(18.5204, 73.8567);
    }
}

// CORE LOGIC: Sends data to Flask
function executePrediction(lat, lon) {
    let s11 = document.getElementById("s11").value;
    let s12 = document.getElementById("s12").value;
    let s13 = document.getElementById("s13").value;
    let s15 = document.getElementById("s15").value;
    let engine_id = document.getElementById("engine_id") ? document.getElementById("engine_id").value : "ENG-777";

    fetch("/predict", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            engine_id: engine_id,
            s11: s11,
            s12: s12,
            s13: s13,
            s15: s15,
            lat: lat, // REAL Latitude sent to R-tree
            lon: lon  // REAL Longitude sent to R-tree
        })
    })
    .then(res => res.json())
    .then(data => {
        let resBox = document.getElementById("result");
        
        // Apply CSS risk classes
        resBox.className = data.score > 0 ? "result-box risk-danger" : "result-box risk-healthy";

        resBox.innerHTML = `
            <h2 style="margin-bottom:15px;">${data.status}</h2>
            <div class="ds-grid">
                <div class="ds-card ds-priority">
                    <small>Maintenance Priority (Unit 2)</small>
                    <span>${data.priority}</span>
                </div>
                <div class="ds-card ds-spatial">
                    <small>Nearest Hangar (Unit 5)</small>
                    <span>${data.hangar}</span>
                </div>
                <div class="ds-card ds-history">
                    <small>Log Version (Unit 6)</small>
                    <span>v${data.history_version}</span>
                </div>
                <div class="ds-card ds-score">
                    <small>Quantum Score</small>
                    <span>${data.score.toFixed(4)}</span>
                </div>
            </div>
            <p style="font-size: 12px; margin-top: 10px; color: #94a3b8;">
                Analyzing from: ${lat.toFixed(4)}, ${lon.toFixed(4)}
            </p>
        `;
    })
    .catch(err => {
        console.error("Error:", err);
        document.getElementById("result").innerHTML = "<h2>Error Connecting to Server</h2>";
    });
}