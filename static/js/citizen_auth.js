// --- Toggle between Login/Register forms ---
const loginToggle = document.getElementById('loginToggle');
const registerToggle = document.getElementById('registerToggle');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const messageDiv = document.getElementById('message');

loginToggle.onclick = () => switchForm('login');
registerToggle.onclick = () => switchForm('register');

function switchForm(form) {
    if (form === 'login') {
        loginForm.classList.add('active');
        registerForm.classList.remove('active');
        loginToggle.classList.add('active');
        registerToggle.classList.remove('active');
        loginForm.style.display = 'flex';
        registerForm.style.display = 'none';
        messageDiv.style.display = "none";
    } else {
        loginForm.classList.remove('active');
        registerForm.classList.add('active');
        loginToggle.classList.remove('active');
        registerToggle.classList.add('active');
        loginForm.style.display = 'none';
        registerForm.style.display = 'flex';
        messageDiv.style.display = "none";
    }
}

// --- Show Message ---
function showMessage(msg, type = "success") {
    messageDiv.textContent = msg;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = "block";
}

// --- Client-side Validation for Register ---
registerForm.onsubmit = function(e) {
    // Only validate client-side; let Django handle actual registration!
    const username = document.getElementById('regUsername').value.trim();
    const password = document.getElementById('regPassword').value;
    const phone = document.getElementById('regPhone').value.trim();
    const place = document.getElementById('regPlace').value.trim();

    if (username.length < 3) {
        showMessage("Username must be at least 3 characters.", "error");
        e.preventDefault();
        return false;
    }
    if (password.length < 6) {
        showMessage("Password must be at least 6 characters.", "error");
        e.preventDefault();
        return false;
    }
    if (!/^[6-9]\d{9}$/.test(phone)) {
        showMessage("Enter a valid 10-digit phone number starting with 6-9.", "error");
        e.preventDefault();
        return false;
    }
    if (place.length < 2) {
        showMessage("Place must be at least 2 characters.", "error");
        e.preventDefault();
        return false;
    }
    // Allow form to submit (Django will process)
};

// --- Client-side Validation for Login ---
loginForm.onsubmit = function(e) {
    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;
    if (username.length < 3 || password.length < 6) {
        showMessage("Enter valid username and password.", "error");
        e.preventDefault();
        return false;
    }
    // Allow form to submit (Django will process)
};

// --- Hide message on input ---
document.querySelectorAll('input').forEach(input => {
    input.addEventListener('input', () => {
        messageDiv.style.display = "none";
    });
});

// --- On page load, show login form by default ---
switchForm('login');
