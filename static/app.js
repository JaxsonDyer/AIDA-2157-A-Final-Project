document.addEventListener("DOMContentLoaded", () => {
    const randomizeBtn = document.getElementById("randomize-btn");
    const briefingList = document.getElementById("briefing-list");
    const emptyState = document.querySelector(".empty-state");
    const loadingIndicator = document.getElementById("loading-indicator");
    const sensorForm = document.getElementById("sensor-form");
    const sortFeedSelect = document.getElementById("sort-feed");
    
    let currentBriefings = []; // store the fetched briefings

    function randomizeData() {
        document.getElementById("lat").value = (33.0 + Math.random() * 9.0).toFixed(4);
        document.getElementById("lon").value = (-124.0 + Math.random() * 10.0).toFixed(4);
        document.getElementById("temp_c").value = (10 + Math.random() * 35).toFixed(1);
        document.getElementById("humidity_pct").value = (5 + Math.random() * 95).toFixed(1);
        document.getElementById("wind_kmh").value = (0 + Math.random() * 100).toFixed(1);
        document.getElementById("precip_mm").value = (Math.random() > 0.8 ? (1 + Math.random() * 50) : 0).toFixed(1);
        document.getElementById("lightning_ka").value = (Math.random() > 0.7 ? (10 + Math.random() * 140) : 0).toFixed(1);
        document.getElementById("soil_moisture").value = (5 + Math.random() * 55).toFixed(1);
        document.getElementById("slope_pct").value = (0 + Math.random() * 45).toFixed(1);
        document.getElementById("aqi_level").value = Math.floor(10 + Math.random() * 200);
        
        let fireChance = Math.random();
        let fireIgnited = fireChance > 0.6 ? 1 : 0;
        document.getElementById("fire_ignited").value = fireIgnited;

        document.getElementById("fire_size").value = fireIgnited ? (1 + Math.random() * 1000).toFixed(1) : 0;
        document.getElementById("fuel_type").value = Math.floor(Math.random() * 4);
        
        // Trigger update after randomization
        runAnalysis();
    }

    randomizeBtn.addEventListener("click", randomizeData);

    let debounceTimer;

    // Listen to changes on the form
    sensorForm.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(runAnalysis, 300);
    });
    
    // Listen to changes on the sort dropdown
    sortFeedSelect.addEventListener("change", () => {
        renderCurrentBriefings();
    });

    async function runAnalysis() {
        loadingIndicator.style.display = 'inline-block';
        
        const payload = {
            lat: parseFloat(document.getElementById("lat").value) || 0,
            lon: parseFloat(document.getElementById("lon").value) || 0,
            Temp_C: parseFloat(document.getElementById("temp_c").value) || 0,
            Humidity_Pct: parseFloat(document.getElementById("humidity_pct").value) || 0,
            Wind_Kmh: parseFloat(document.getElementById("wind_kmh").value) || 0,
            Precipitation_mm: parseFloat(document.getElementById("precip_mm").value) || 0,
            Lightning_Strike_kA: parseFloat(document.getElementById("lightning_ka").value) || 0,
            Soil_Moisture_Pct: parseFloat(document.getElementById("soil_moisture").value) || 0,
            Slope_Pct: parseFloat(document.getElementById("slope_pct").value) || 0,
            AQI_Level: parseInt(document.getElementById("aqi_level").value) || 0,
            Fire_Ignited: parseInt(document.getElementById("fire_ignited").value) || 0,
            Fire_Size_Hectares: parseFloat(document.getElementById("fire_size").value) || 0,
            Fuel_Type_Code: parseInt(document.getElementById("fuel_type").value) || 0
        };

        try {
            const res = await fetch("/api/briefing", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            
            if (!res.ok) throw new Error("API Error");
            currentBriefings = await res.json();
            
            if (emptyState) {
                emptyState.style.display = 'none';
            }

            renderCurrentBriefings();
            
        } catch (err) {
            console.error(err);
        } finally {
            loadingIndicator.style.display = 'none';
        }
    }
    
    function renderCurrentBriefings() {
        briefingList.innerHTML = ''; 
        
        const sortValue = sortFeedSelect.value;
        const severityRank = {
            'critical': 4,
            'warning': 3,
            'info': 2,
            'success': 1
        };
        
        // clone array to sort without mutating original fetched order just in case
        let sorted = [...currentBriefings];
        
        if (sortValue === 'critical') {
            sorted.sort((a, b) => severityRank[b.level] - severityRank[a.level]);
        } else if (sortValue === 'good') {
            sorted.sort((a, b) => severityRank[a.level] - severityRank[b.level]);
        } else if (sortValue === 'aza') {
            sorted.sort((a, b) => a.title.localeCompare(b.title));
        }

        sorted.forEach(data => renderBriefingCard(data));
    }

    function renderBriefingCard(data) {
        const card = document.createElement('div');
        card.classList.add('briefing-card');
        card.classList.add(`level-${data.level}`);

        let detailsHtml = '';
        if (data.details) {
            detailsHtml = '<div class="card-details">';
            for (const [key, val] of Object.entries(data.details)) {
                detailsHtml += `<div class="detail-item"><span class="detail-label">${key}:</span> <span class="detail-value">${val}</span></div>`;
            }
            detailsHtml += '</div>';
        }

        card.innerHTML = `
            <div class="card-header">
                <h3 class="card-title">${data.title}</h3>
                <span class="card-coords">[ ${data.lat}, ${data.lon} ]</span>
            </div>
            <div class="card-body">
                <p class="card-message">${data.message}</p>
                ${detailsHtml}
            </div>
            <div class="card-footer">
                <span class="action-label">ACTION RECOMMENDED:</span>
                <span class="action-text">${data.action}</span>
            </div>
        `;

        briefingList.appendChild(card);
    }
    
    // Initial load
    runAnalysis();
});
