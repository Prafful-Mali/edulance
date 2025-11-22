requireAuth();

let currentUserId = null;

function showAlert(message, type = 'success') {
  const alertContainer = document.getElementById('alertContainer');
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
  alertDiv.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;
  alertContainer.appendChild(alertDiv);
  
  setTimeout(() => {
    alertDiv.remove();
  }, 5000);
}

async function loadUserProfile() {
  try {
    const response = await authenticatedFetch('/api/users/');

    if (response.ok) {
      const data = await response.json();
      currentUserId = data.id;
      
      document.getElementById('userName').textContent = data.username || 'User';
      document.getElementById('userEmail').textContent = data.email || '';
      document.getElementById('userRole').textContent = data.role || 'User';
      
      document.getElementById('editUsername').value = data.username || '';
      document.getElementById('editUserEmail').value = data.email || '';
      document.getElementById('editUserBio').value = data.bio || '';
      
      const initial = data.username ? data.username.charAt(0).toUpperCase() : 'U';
      document.getElementById('userInitial').textContent = initial;
    } else {
      showAlert('Failed to load profile', 'danger');
    }
  } catch (error) {
    console.error('Error loading profile:', error);
    showAlert('Error loading profile', 'danger');
  }
}

document.getElementById('editProfileForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  
  const bio = document.getElementById('editUserBio').value;
  
  try {
    const response = await authenticatedFetch(`/api/users/${currentUserId}/`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ bio })
    });
    
    if (response.ok) {
      showAlert('Profile updated successfully', 'success');
      await loadUserProfile();
      bootstrap.Modal.getInstance(document.getElementById('editProfileModal')).hide();
    } else {
      const error = await response.json();
      showAlert(error.error || 'Failed to update profile', 'danger');
    }
  } catch (error) {
    console.error('Error updating profile:', error);
    showAlert('Error updating profile', 'danger');
  }
});

document.getElementById('changePasswordForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  
  const oldPassword = document.getElementById('oldPassword').value;
  const newPassword = document.getElementById('newPassword').value;
  const newPasswordConfirm = document.getElementById('newPasswordConfirm').value;
  
  if (newPassword !== newPasswordConfirm) {
    showAlert('New passwords do not match', 'danger');
    return;
  }
  
  try {
    const response = await authenticatedFetch('/api/users/change_password/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        old_password: oldPassword,
        new_password: newPassword,
        new_password_confirm: newPasswordConfirm
      })
    });
    
    if (response.ok) {
      showAlert('Password changed successfully', 'success');
      document.getElementById('changePasswordForm').reset();
      bootstrap.Modal.getInstance(document.getElementById('securityModal')).hide();
    } else {
      const error = await response.json();
      const errorMsg = Object.values(error).flat()[0]|| 'Failed to change password';
      showAlert(errorMsg, 'danger');
    }
  } catch (error) {
    console.error('Error changing password:', error);
    showAlert('Error changing password', 'danger');
  }
});

window.addEventListener('DOMContentLoaded', loadUserProfile);