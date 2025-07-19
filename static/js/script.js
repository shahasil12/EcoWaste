const FAQS = {
    'reward': "Earn reward points by depositing sorted waste in our smart bins. Points can be redeemed for eco-friendly products!",
    'location': "Use the 'Find Bins Near Me' button or map to see your closest recycle bins.",
    'types': "We support Plastic, Paper, Metal, E-waste, and Organic waste. Check bin types in the 'Bin Locations' section.",
    'report': "To report waste, click the 'Report Waste' button and fill out the form with location details.",
    'full': "If a bin is marked as 'Full', please use another bin nearby or report it for priority servicing.",
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
            chat.innerHTML += `<div><b>You:</b> ${q}</div>`;
            let answer = "Sorry, I don't understand that question! Try keywords like reward, location, types, report, full.";
            for (const key in FAQS) {
                if (q.toLowerCase().includes(key)) {
                    answer = FAQS[key]; break;
                }
            }
            chat.innerHTML += `<div><b>EcoWasteBot:</b> ${answer}</div>`;
            chat.scrollTop = chat.scrollHeight;
            document.getElementById('faq-input').value = '';
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
    // Pick badge color for status
    let statusColor = bin.status == 'Full' ? 'warning' : 'success';
    html += `
    <div class="card mb-3 border-${statusColor} shadow-sm">
        <div class="card-body py-2">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-0 text-${statusColor}">
                        <i class="fas fa-map-marker-alt me-1"></i>${bin.name}
                    </h6>
                    <small class="text-muted">${bin.address}</small>
                </div>
                <span class="badge bg-${statusColor}">${bin.status}</span>
            </div>
            <div class="mt-2">
                ${bin.types.split(',').map(t =>
                    `<span class="badge bg-secondary me-1">${t.trim()}</span>`
                ).join('')}
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
                  L.marker([bin.latitude, bin.longitude]).addTo(map)
                    .bindPopup(
                      `<strong>${bin.name}</strong><br>
                      ${bin.address}<br>
                      Status: <span class="badge bg-${bin.status == 'Full' ? 'warning' : 'success'}">${bin.status}</span><br>
                      Types: ${bin.types}`
                    );
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
});

document.addEventListener('DOMContentLoaded', function() {
    let chat = document.getElementById('faq-chat');
    if (chat) {
        chat.innerHTML += `<div class="text-success small"><b>EcoWasteBot:</b> Please ask any questions if you have a doubt.</div>`;
    }
    let faqForm = document.getElementById('faq-form');
  
});

function company() {
  
    window.location.href = "{% url 'company_login' %}";
}
