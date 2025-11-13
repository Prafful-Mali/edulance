document.getElementById('registerForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const password_confirm = document.getElementById('password_confirm').value;
    const submitBtn = document.getElementById('submitBtn');
    
    if (password !== password_confirm) {
        alert('Passwords do not match!');
        return;
    }
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Registering...';
    
    try {
        const response = await fetch('/users/api/register/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password,
                password_confirm: password_confirm
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert(data.message || 'Registration successful! Please check your email to verify your account.');
            window.location.href = '/users/login/';
        } else {
            let errorMessage = 'Registration failed:\n';
            if (typeof data === 'object') {
                for (let key in data) {
                    errorMessage += `${key}: ${data[key]}\n`;
                }
            } else {
                errorMessage = data.error || 'Registration failed';
            }
            alert(errorMessage);
            
            submitBtn.disabled = false;
            submitBtn.textContent = 'Register';
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Register';
    }
});