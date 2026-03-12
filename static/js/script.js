const FAQS = {
    'reward': "Earn reward points (10 for reporting waste, 20 for pickups) by disposing sorted waste. Points can be redeemed for eco-friendly products!",
    'location': "Use the 'Find Bins Near Me' button or the map in the 'Bin Locations' section to see your closest recycle bins.",
    'types': "We support Plastic, Paper, Metal, E-waste, and Organic waste. Different bins are color-coded for each type.",
    'report': "To report waste, log in as a citizen, click 'Report Waste', and mark the location on the map.",
    'full': "If a bin is marked as 'Full', please use another bin nearby. Our smart sensors will notify the collection company!",
    'pickup': "You can request a door-to-door waste pickup from your preferred company through your dashboard.",
    'points': "Your total points are displayed on your Citizen Dashboard. You can see how many you've earned from reports and pickups.",
};

function scrollToBinMap() {
    const section = document.getElementById('bin-locations');
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}


document.addEventListener('DOMContentLoaded', function() {
    // FAQ Assistant
    let faqForm = document.getElementById('faq-form');
    if (faqForm) {
        faqForm.onsubmit = function(e) {
            e.preventDefault();
            const q = document.getElementById('faq-input').value.trim();
            if (!q) return;

            let chat = document.getElementById('faq-chat');
            let typing = document.getElementById('ai-typing');

            // Add user message
            chat.innerHTML += `<div class="mb-2 text-end"><span class="bg-primary text-white p-2 rounded-3 d-inline-block small" style="max-width:80%">${q}</span></div>`;
            chat.scrollTop = chat.scrollHeight;
            document.getElementById('faq-input').value = '';

            // Show typing indicator
            typing.classList.remove('d-none');

            setTimeout(() => {
                let answer = "I'm not exactly sure about that. Try asking about points, bins, types, or reports!";
                for (const key in FAQS) {
                    if (q.toLowerCase().includes(key)) {
                        answer = FAQS[key];
                        break;
                    }
                }

                typing.classList.add('d-none');
                chat.innerHTML += `<div class="mb-2"><span class="bg-light p-2 rounded-3 d-inline-block border small" style="max-width:80%"><b>EcoBot:</b> ${answer}</span></div>`;
                chat.scrollTop = chat.scrollHeight;
            }, 800);
        }
    }

    window.clearChat = function() {
        let chat = document.getElementById('faq-chat');
        if (chat) chat.innerHTML = '<div class="text-muted small text-center my-3">Chat cleared</div>';
    }

    window.toggleAssistant = function() {
        const card = document.getElementById('assistantCard');
        if (card) {
            card.classList.toggle('active');
            let chat = document.getElementById('faq-chat');
            if (card.classList.contains('active') && (chat.innerHTML.trim() === '' || chat.innerHTML.includes('Check bin types'))) {
                 chat.innerHTML = `<div class="mb-2"><span class="bg-light p-2 rounded-3 d-inline-block border small" style="max-width:80%"><b>EcoBot:</b> Hello! I'm your EcoWaste assistant. How can I help you today? 🌱</span></div>`;
            }
        }
    }

    // ---- Fetch and show nearby bins and stats on LOAD (NOT the map) ----
    if (typeof BIN_JSON_URL !== "undefined") {
        fetch(BIN_JSON_URL)
            .then(response => response.json())
            .then(bins => {
                // Nearby Bins
                const container = document.getElementById('nearby-bins');
                if (container) {
                    if (!bins.length) {
                        container.innerHTML = '<div class="text-center text-muted">No bins found.</div>';
                    } else {
                      let html = '';
bins.forEach(bin => {
    let statusColor = bin.status == 'Full' ? 'warning' : 'success';
    html += `
    <div class="card bin-card-premium mb-3 border-${statusColor} shadow-sm px-2">
        <div class="card-body py-3">
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <h6 class="mb-1 fw-bold text-dark">
                        <i class="fas fa-map-marker-alt me-2 text-${statusColor}"></i>${bin.name}
                    </h6>
                    <div class="text-muted small mb-2" style="font-size: 0.8rem;">
                        <i class="fas fa-location-arrow me-1"></i>${bin.address}
                    </div>
                    <div class="d-flex flex-wrap gap-1">
                        ${bin.types.split(',').map(t =>
                            `<span class="badge bg-light text-dark border bin-type-tag">${t.trim()}</span>`
                        ).join('')}
                    </div>
                </div>
                <div class="d-flex flex-column align-items-end gap-2">
                    <span class="badge bg-${statusColor} rounded-pill px-3" style="font-size: 0.65rem;">${bin.status}</span>
                    ${bin.status === 'Available' ? 
                        `<button class="btn btn-outline-warning btn-sm py-0 px-2" style="font-size: 0.65rem;" onclick="reportBinFull(${bin.id})">Report Full</button>` 
                        : ''}
                </div>
            </div>
        </div>
    </div>
    `;
});
container.innerHTML = html;

                    }
                }
                // Statistics
                if (document.getElementById('stat-total-bins')) {
                    document.getElementById('stat-total-bins').textContent = bins.length;
                    document.getElementById('stat-full-bins').textContent = bins.filter(b => b.status == 'Full').length;
                    document.getElementById('stat-empty-bins').textContent = bins.filter(b => b.status == 'Available').length;
                }
            })
            .catch(err => {
                const container = document.getElementById('nearby-bins');
                if (container) container.innerHTML = '<div class="text-danger">Error loading bins.</div>';
            });
    } else {
        console.error("BIN_JSON_URL is not defined.");
    }

    // ---- Map triggers ONLY on button click ----
    function showBinLocations() {
        const mapDiv = document.getElementById('bin-map');
        mapDiv.style.display = 'block';
        // Prevent re-creating the map every click
        if (mapDiv.getAttribute('data-loaded') === 'true') return;

        fetch(BIN_JSON_URL)
          .then(response => response.json())
          .then(bins => {
              let center = bins.length ? [bins[0].latitude, bins[0].longitude] : [20.5937, 78.9629];
              let map = L.map('bin-map').setView(center, bins.length ? 14 : 5);
              L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                  attribution: '&copy; OpenStreetMap contributors'
              }).addTo(map);
              bins.forEach(bin => {
    let statusColor = bin.status == 'Full' ? 'warning' : 'success';
    let popupContent = `
        <div class="p-2">
            <strong>${bin.name}</strong><br>
            <small class="text-muted d-block mb-2">${bin.address}</small>
            <div class="d-flex justify-content-between align-items-center">
                <span class="badge bg-${statusColor}">${bin.status}</span>
                ${bin.status === 'Available' ? 
                    `<button class="btn btn-warning btn-sm py-1 px-2" style="font-size: 0.7rem;" onclick="reportBinFull(${bin.id})">Report Full</button>` 
                    : ''}
            </div>
        </div>
    `;
    L.marker([bin.latitude, bin.longitude]).addTo(map)
        .bindPopup(popupContent);
});
              mapDiv.setAttribute('data-loaded', 'true');
          })
          .catch(() => {
              mapDiv.innerHTML = '<div class="text-danger text-center py-5">Error loading bins.</div>';
          });
    }

    // Attach the function to the button
    const btn = document.getElementById('view-bins-btn');
    if (btn) {
        btn.addEventListener('click', showBinLocations);
    }

    // ---- Login modal logic ----
    window.showLoginModal = function() {
        const modal = new bootstrap.Modal(document.getElementById('loginModal'));
        modal.show();
    }
    window.loginAs = function(userType) {
        alert('Logged in as: ' + userType);
        bootstrap.Modal.getInstance(document.getElementById('loginModal')).hide();
    }
    window.selectUserType = function(userType) {
        loginAs(userType);
    }
    // CSRF helper
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    window.reportBinFull = function(binId) {
        if (!confirm("Are you sure you want to report this bin as full? This helps our collection team!🌱")) return;

        fetch(`${REPORT_BIN_URL}${binId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(async response => {
            const data = await response.json();
            if (response.ok) {
                alert("✅ " + data.message);
                location.reload(); 
            } else {
                alert("❌ " + (data.message || "Failed to submit report. Please login as a citizen."));
            }
        })
        .catch(err => {
            alert("❌ Please login as a citizen to report bins!");
        });
    }
});


function company() {
  
    window.location.href = "{% url 'company_login' %}";
}
