import { API } from './apiEndpoints.js';

if (!requireAuth()) {
    throw new Error("Authentication required");
}

const UserRole = {
    ADMIN: 'admin',
    USER: 'user'
};

let allUsers = [];
let allPosts = [];
let selectedUserId = null;
let selectedPostSlug = null;

async function checkAdminRole() {
    try {
        const response = await authenticatedFetch(API.USERS.ME);
        if (response.ok) {
            const user = await response.json();
            if (user.role !== UserRole.ADMIN) {
                alert('Access denied. Admin privileges required.');
                window.location.href = '/dashboard/';
                return false;
            }
            return true;
        } else {
            console.error('Failed to fetch user info:', response.status);
            window.location.href = '/dashboard/';
            return false;
        }
    } catch (error) {
        console.error('Error checking admin role:', error);
        window.location.href = '/dashboard/';
        return false;
    }
}

async function fetchUsers() {
    try {
        const response = await authenticatedFetch(API.USERS.LIST);
        
        if (response.ok) {
            allUsers = await response.json();
            renderUsers();
            updateStats();
        } else {
            const errorData = await response.text();
            console.error('Error response:', errorData);
            showError('usersTableBody', 'Failed to load users. Please check console for details.');
        }
    } catch (error) {
        console.error('Error fetching users:', error);
        showError('usersTableBody', 'Error loading users: ' + error.message);
    }
}

async function fetchPosts() {
    try {
        const response = await authenticatedFetch(API.POSTS.LIST);
        
        if (response.ok) {
            allPosts = await response.json();
            renderPosts();
            updateStats();
        } else {
            const errorData = await response.text();
            console.error('Error response:', errorData);
            showError('postsTableBody', 'Failed to load posts. Please check console for details.');
        }
    } catch (error) {
        console.error('Error fetching posts:', error);
        showError('postsTableBody', 'Error loading posts: ' + error.message);
    }
}

function showError(tableBodyId, message) {
    const tbody = document.getElementById(tableBodyId);
    const colSpan = tableBodyId === 'usersTableBody' ? 5 : 6;
    tbody.innerHTML = `<tr><td colspan="${colSpan}" class="text-center text-danger">${message}</td></tr>`;
}

function updateStats() {
    document.getElementById('totalUsers').textContent = allUsers.length;
    document.getElementById('totalPosts').textContent = allPosts.length;
}

function renderUsers() {
    const tbody = document.getElementById('usersTableBody');
    
    if (allUsers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No users found</td></tr>';
        return;
    }
    
    tbody.innerHTML = allUsers.map(user => `
        <tr>
            <td>${escapeHtml(user.username)}</td>
            <td>${escapeHtml(user.email)}</td>
            <td>
                <span class="badge ${user.role === UserRole.ADMIN ? 'bg-danger' : 'bg-primary'}">
                    ${escapeHtml(user.role)}
                </span>
            </td>
            <td>${new Date(user.created_at).toLocaleDateString()}</td>
            <td class="table-actions">
                <button class="btn btn-sm btn-danger" onclick="openDeleteUserModal('${user.id}', '${escapeHtml(user.username)}')">
                    <i class="bi bi-trash-fill"></i> Delete
                </button>
            </td>
        </tr>
    `).join('');
}

function renderPosts() {
    const tbody = document.getElementById('postsTableBody');
    
    if (allPosts.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No posts found</td></tr>';
        return;
    }
    
    tbody.innerHTML = allPosts.map(post => `
        <tr>
            <td>
                <a href="/collaborate/post/${post.slug}/" target="_blank">
                    ${escapeHtml(post.title)}
                </a>
            </td>
            <td>${escapeHtml(post.user.username)}</td>
            <td>
                <span class="badge ${post.project_type === 'hackathon' ? 'bg-warning text-dark' : 'bg-info text-dark'}">
                    ${post.project_type === 'hackathon' ? 'Hackathon' : 'Group Project'}
                </span>
            </td>
            <td>${post.applications_count}</td>
            <td>${new Date(post.created_at).toLocaleDateString()}</td>
            <td class="table-actions">
                <button class="btn btn-sm btn-danger" onclick="openDeletePostModal('${post.slug}', '${escapeHtml(post.title)}')">
                    <i class="bi bi-trash-fill"></i> Delete
                </button>
            </td>
        </tr>
    `).join('');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function openDeleteUserModal(userId, username) {
    selectedUserId = userId;
    document.getElementById('deleteUserName').textContent = username;
    const modal = new bootstrap.Modal(document.getElementById('deleteUserModal'));
    modal.show();
}

function openDeletePostModal(slug, title) {
    selectedPostSlug = slug;
    document.getElementById('deletePostTitle').textContent = title;
    const modal = new bootstrap.Modal(document.getElementById('deletePostModal'));
    modal.show();
}

async function deleteUser() {
    if (!selectedUserId) return;
    
    const btn = document.getElementById('confirmDeleteUserBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Deleting...';
    
    try {
        const response = await authenticatedFetch(API.USERS.DELETE(selectedUserId), {
            method: 'DELETE'
        });
        
        if (response.ok || response.status === 204) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('deleteUserModal'));
            modal.hide();
            await fetchUsers();
            alert('User deleted successfully');
        } else {
            const error = await response.json().catch(() => ({ error: 'Failed to delete user' }));
            alert('Error: ' + (error.error || error.detail || 'Failed to delete user'));
        }
    } catch (error) {
        console.error('Error deleting user:', error);
        alert('An error occurred while deleting the user');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Delete User';
    }
}

async function deletePost() {
    if (!selectedPostSlug) return;
    
    const btn = document.getElementById('confirmDeletePostBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Deleting...';
    
    try {
        const response = await authenticatedFetch(API.POSTS.DELETE(selectedPostSlug), {
            method: 'DELETE'
        });
        
        if (response.ok || response.status === 204) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('deletePostModal'));
            modal.hide();
            await fetchPosts();
            alert('Post deleted successfully');
        } else {
            const error = await response.json().catch(() => ({ error: 'Failed to delete post' }));
            alert('Error: ' + (error.error || error.detail || 'Failed to delete post'));
        }
    } catch (error) {
        console.error('Error deleting post:', error);
        alert('An error occurred while deleting the post');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Delete Post';
    }
}

function showLoading() {
    document.getElementById('loadingSpinner').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loadingSpinner').style.display = 'none';
}

async function init() {
    showLoading();
    const isAdmin = await checkAdminRole();
    if (isAdmin) {
        await Promise.all([fetchUsers(), fetchPosts()]);
    }
    hideLoading();
}

document.getElementById('confirmDeleteUserBtn').addEventListener('click', deleteUser);
document.getElementById('confirmDeletePostBtn').addEventListener('click', deletePost);

window.openDeleteUserModal = openDeleteUserModal;
window.openDeletePostModal = openDeletePostModal;

window.addEventListener('DOMContentLoaded', init);