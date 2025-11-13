document.querySelector('form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const email = document.getElementById('emailInput').value;
    const password = document.getElementById('passwordInput').value;
    const submitBtn = document.getElementById('loginBtn');

    submitBtn.disabled = true;
    submitBtn.textContent = 'Logging in...';
    
    try {
        const response = await fetch('/users/api/token/', {
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
            
            const alertDiv = document.getElementById('messageAlert');
            const messageText = document.getElementById('messageText');
            alertDiv.className = 'alert alert-success alert-dismissible fade show';
            messageText.textContent = 'Login successful! Redirecting...';
            alertDiv.classList.remove('d-none');
            
            setTimeout(() => {
                window.location.href = '/users/dashboard/';
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