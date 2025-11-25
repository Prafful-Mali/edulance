window.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const message = urlParams.get('message');
    
    if (message) {
        const alertDiv = document.getElementById('messageAlert');
        const messageText = document.getElementById('messageText');
        
        const messages = {
            verified: ['alert-success', 'Email verified successfully! You can now login.'],
            already_verified: ['alert-info', 'Your email is already verified. Please login.'],
            expired: ['alert-warning', 'Verification link has expired. Please request a new one.'],
            invalid: ['alert-danger', 'Invalid verification link.'],
            not_found: ['alert-danger', 'User not found.'],
            error: ['alert-danger', 'An error occurred during verification.']
        };

        if (messages[message]) {
            alertDiv.className = `alert ${messages[message][0]} alert-dismissible fade show`;
            messageText.textContent = messages[message][1];
            alertDiv.classList.remove('d-none');
        }

        window.history.replaceState({}, document.title, window.location.pathname);
    }
});


document.querySelector('form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const email = document.getElementById('emailInput').value;
    const password = document.getElementById('passwordInput').value;
    const submitBtn = document.getElementById('loginBtn');

    submitBtn.disabled = true;
    submitBtn.textContent = 'Logging in...';
    
    try {
        const response = await fetch('/api/login/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            if (data.user) localStorage.setItem('user', JSON.stringify(data.user));
            
            showLoginAlert('Login successful! Redirecting...', 'success');

            setTimeout(() => window.location.href = '/dashboard/', 1000);
        } else {
            showLoginAlert(data.error || 'Login failed. Please check your credentials.', 'danger');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Login';
        }
    } catch (error) {
        showLoginAlert('An error occurred. Please try again.', 'danger');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Login';
    }
});

function showLoginAlert(message, type) {
    const alertDiv = document.getElementById('messageAlert');
    const messageText = document.getElementById('messageText');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    messageText.textContent = message;
    alertDiv.classList.remove('d-none');
}

const sendResetEmailBtn = document.getElementById("sendResetEmailBtn");
const forgotEmailInput = document.getElementById("forgotEmailInput");
const forgotAlert = document.getElementById("forgotAlert");
const forgotAlertText = document.getElementById("forgotAlertText");

sendResetEmailBtn.addEventListener("click", async () => {
    const email = forgotEmailInput.value.trim();

    if (!email) {
        showForgotAlert("Please enter your email.", "danger", true);
        return;
    }

    sendResetEmailBtn.disabled = true;
    sendResetEmailBtn.innerHTML = `
        <span class="spinner-border spinner-border-sm"></span> Sending...
    `;

    try {
        const response = await fetch("/api/forget-password/", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ email }),
        });

        const data = await response.json();

        showForgotAlert(data.message || "Temporary password sent.", "success");

        if (response.ok) {
            forgotEmailInput.value = "";

            setTimeout(() => {
                const modal = bootstrap.Modal.getInstance(
                    document.getElementById("forgotPasswordModal")
                );
                modal?.hide();
            }, 2000);
        }
    } catch (error) {
        showForgotAlert("Something went wrong. Try again later.", "danger");
    } finally {
        sendResetEmailBtn.disabled = false;
        sendResetEmailBtn.textContent = "Send Temporary Password";
    }
});

function showForgotAlert(message, type, sticky = false) {
    forgotAlert.classList.remove("d-none");
    forgotAlert.className = `alert alert-${type} alert-dismissible fade show`;
    forgotAlertText.textContent = message;

    if (!sticky) {
        setTimeout(() => {
            forgotAlert.classList.add("d-none");
        }, 3000);
    }
}


document.getElementById("forgotPasswordModal")
    .addEventListener("hidden.bs.modal", () => {
        forgotAlert.classList.add("d-none");
        forgotEmailInput.value = "";
    });
