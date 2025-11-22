window.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const message = urlParams.get('message');
    
    if (message) {
        const alertDiv = document.getElementById('messageAlert');
        const messageText = document.getElementById('messageText');
        
        let alertClass = 'alert-info';
        let messageContent = '';
        
        switch(message) {
            case 'verified':
                alertClass = 'alert-success';
                messageContent = 'Email verified successfully! You can now login.';
                break;
            case 'already_verified':
                alertClass = 'alert-info';
                messageContent = 'Your email is already verified. Please login.';
                break;
            case 'expired':
                alertClass = 'alert-warning';
                messageContent = 'Verification link has expired. Please request a new one.';
                break;
            case 'invalid':
                alertClass = 'alert-danger';
                messageContent = 'Invalid verification link.';
                break;
            case 'not_found':
                alertClass = 'alert-danger';
                messageContent = 'User not found.';
                break;
            case 'error':
                alertClass = 'alert-danger';
                messageContent = 'An error occurred during verification.';
                break;
            default:
                return;
        }
        
        alertDiv.className = `alert ${alertClass} alert-dismissible fade show`;
        messageText.textContent = messageContent;
        alertDiv.classList.remove('d-none');
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
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            
            if (data.user) {
                localStorage.setItem('user', JSON.stringify(data.user));
            }
            
            const alertDiv = document.getElementById('messageAlert');
            const messageText = document.getElementById('messageText');
            alertDiv.className = 'alert alert-success alert-dismissible fade show';
            messageText.textContent = 'Login successful! Redirecting...';
            alertDiv.classList.remove('d-none');
            
            setTimeout(() => {
                window.location.href = '/dashboard/';
            }, 1000);
            
        } else {
            const alertDiv = document.getElementById('messageAlert');
            const messageText = document.getElementById('messageText');
            alertDiv.className = 'alert alert-danger alert-dismissible fade show';
            messageText.textContent = data.error || 'Login failed. Please check your credentials.';
            alertDiv.classList.remove('d-none');
            
            submitBtn.disabled = false;
            submitBtn.textContent = 'Login';
        }
    } catch (error) {
        console.error('Error:', error);
        
        const alertDiv = document.getElementById('messageAlert');
        const messageText = document.getElementById('messageText');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        messageText.textContent = 'An error occurred. Please try again.';
        alertDiv.classList.remove('d-none');
        
        submitBtn.disabled = false;
        submitBtn.textContent = 'Login';
    }
});