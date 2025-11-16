if (!requireAuth()) {
    throw new Error("Authentication required");
}

let allPosts = [];
let myPosts = [];
let allSkills = [];
let skillsSelectInstance = null;
let editSkillsSelectInstance = null;

const elements = {
    myPostsContainer: document.getElementById('myPostsContainer'),
    postsContainer: document.getElementById('postsContainer'),
    createPostForm: document.getElementById('createPostForm'),
    editPostForm: document.getElementById('editPostForm'),
    submitPostBtn: document.getElementById('submitPostBtn'),
    saveEditBtn: document.getElementById('saveEditBtn'),
    clearFilters: document.getElementById('clearFilters'),
    filterProjectType: document.getElementById('filterProjectType'),
    loadingSpinner: document.getElementById('loadingSpinner')
};

function showLoading() {
    elements.loadingSpinner.style.display = 'block';
}

function hideLoading() {
    elements.loadingSpinner.style.display = 'none';
}

function showError(message) {
    alert(message || 'An error occurred. Please try again.');
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function createPostCard(post, isOwner = false) {
    const skills = post.skills.map(skill => `<span class="badge bg-secondary me-1">${skill.name}</span>`).join('');     
    const projectTypeBadge = post.project_type === 'hackathon'
        ? '<span class="badge bg-warning text-dark">Hackathon</span>'
        : '<span class="badge bg-info text-dark">Group Project</span>';
    const deadlineDate = formatDate(post.last_date);

    const editBtnId = `edit-btn-${post.slug}`;
    const deleteBtnId = `delete-btn-${post.slug}`;

    const buttonsHTML = isOwner
        ? `
          <div class="d-flex justify-content-between align-items-center">
            <a href="/collaborate/post/${post.slug}/" class="btn btn-primary-custom btn-sm px-3">
              <i class="bi bi-eye"></i> View
            </a>
            <div>
              <button class="btn btn-warning btn-sm text-white me-1" id="${editBtnId}">
                <i class="bi bi-pencil-fill"></i>
              </button>
              <button class="btn btn-danger btn-sm" id="${deleteBtnId}">
                <i class="bi bi-trash-fill"></i>
              </button>
            </div>
          </div>
        `
        : `
          <div class="d-grid">
            <a href="/collaborate/post/${post.slug}/" class="btn btn-primary-custom btn-custom btn-sm">
              <i class="bi bi-eye"></i> View Details
            </a>
          </div>
        `;

    return `
        <div class="col-md-6 col-lg-4 mb-4" data-post-slug="${post.slug}">
          <div class="feature-card h-100 p-3">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <h5 class="card-title">${post.title}</h5>
              ${projectTypeBadge}
            </div>
            <p class="text-muted small">${post.description.substring(0, 100)}${post.description.length > 100 ? '...' : ''}</p>
            <div class="mb-2">
              <small class="text-muted">Required Skills:</small><br>
              ${skills || '<span class="text-muted">No specific skills</span>'}
            </div>
            <div class="mb-2"><small class="text-muted">Team Size: ${post.people_required}</small></div>
            <div class="mb-2"><small class="text-muted">Applications: ${post.applications_count || 0}</small></div>
            <div class="mb-3"><small class="text-muted">Deadline: ${deadlineDate}</small></div>
            ${buttonsHTML}
          </div>
        </div>
    `;
}

async function fetchSkills() {
    try {
        const response = await authenticatedFetch('/api/skills/');
        if (response.ok) {
            allSkills = await response.json();
            return allSkills;
        }
    } catch (error) {
        console.error('Error fetching skills:', error);
    }
    return [];
}

async function fetchPosts(projectType = '') {
    showLoading();
    try {
        let url = '/api/posts/';
        if (projectType) {
            url += `?project_type=${projectType}`;
        }
        
        const response = await authenticatedFetch(url);
        if (response.ok) {
            allPosts = await response.json();
            return allPosts;
        } else {
            showError('Failed to fetch posts');
        }
    } catch (error) {
        console.error('Error fetching posts:', error);
        showError('Error loading posts');
    } finally {
        hideLoading();
    }
    return [];
}

async function fetchMyPosts() {
    try {
        const response = await authenticatedFetch('/api/posts/my_posts/');
        if (response.ok) {
            myPosts = await response.json();
            return myPosts;
        }
    } catch (error) {
        console.error('Error fetching my posts:', error);
    }
    return [];
}

async function createPost() {
    if (!elements.createPostForm.checkValidity()) {
        elements.createPostForm.reportValidity();
        return;
    }

    const selectedSkills = skillsSelectInstance.getValue();
    
    const skillIds = selectedSkills.filter(skillId => allSkills.find(skill => skill.id === skillId));       
    
    const newSkills = selectedSkills.filter(skillId => !allSkills.find(skill => skill.id === skillId));         
    if (newSkills.length > 0) {
        showError('Please select only existing skills from the list. Creating new skills is not allowed.');
        return;
    }

    const postData = {
        title: document.getElementById('postTitle').value,
        description: document.getElementById('postDescription').value,
        project_type: document.getElementById('postProjectType').value,
        people_required: parseInt(document.getElementById('postPeopleRequired').value),
        last_date: document.getElementById('postLastDate').value,
        event_start_date: document.getElementById('postEventStart').value,
        event_last_date: document.getElementById('postEventEnd').value,
        skill_ids: skillIds
    };

    try {
        const response = await authenticatedFetch('/api/posts/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(postData)
        });

        if (response.ok) {
            bootstrap.Modal.getInstance(document.getElementById('createPostModal')).hide();
            elements.createPostForm.reset();
            skillsSelectInstance.clear();
            await loadAllData();
        } else {
            const error = await response.json();
            showError(error.detail || error.skill_ids?.[0] || 'Failed to create post');
        }
    } catch (error) {
        console.error('Error creating post:', error);
        showError('Error creating post');
    }
}

async function deletePost(slug) {
    if (!confirm('Are you sure you want to delete this post?')) {
        return;
    }

    try {
        const response = await authenticatedFetch(`/api/posts/${slug}/`, {
            method: 'DELETE'
        });

        if (response.ok || response.status === 204) {
            await loadAllData();
        } else {
            const error = await response.json().catch(() => ({ detail: 'Failed to delete post' }));
            showError(error.detail || error.error || 'Failed to delete post');
        }
    } catch (error) {
        console.error('Error deleting post:', error);
        showError('Error deleting post');
    }
}

async function openEditModal(slug) {
    const post = myPosts.find(post => post.slug === slug);
    if (!post) {
        console.error('Post not found with slug:', slug);
        return;
    }

    document.getElementById('editPostId').value = post.slug;
    document.getElementById('editPostTitle').value = post.title;
    document.getElementById('editPostDescription').value = post.description;
    document.getElementById('editPostProjectType').value = post.project_type;
    document.getElementById('editPostPeopleRequired').value = post.people_required;

    if (editSkillsSelectInstance) {
        editSkillsSelectInstance.destroy();
    }

    const select = document.getElementById('editSkillsSelect');
    select.innerHTML = '';
    
    allSkills.forEach(skill => {
        const opt = document.createElement('option');
        opt.value = skill.id;
        opt.text = skill.name;
        if (post.skills.some(skillObj => skillObj.id === skill.id)) { 
            opt.selected = true;
        }
        select.appendChild(opt);
    });

    editSkillsSelectInstance = new TomSelect("#editSkillsSelect", {
        plugins: ['remove_button'],
        maxItems: 10,
        create: false,
        createOnBlur: false,
        placeholder: "Select skills from the list...",
        onItemAdd: function(value, item) {
            const isValid = allSkills.some(skill => skill.id === value);
            if (!isValid) {
                this.removeItem(value, true);
                showError('Please select only existing skills from the dropdown list.');
            }
        }
    });

    new bootstrap.Modal(document.getElementById('editPostModal')).show();
}

async function saveEdit() {
    const slug = document.getElementById('editPostId').value;
    const selectedSkills = editSkillsSelectInstance.getValue();
    
    const skillIds = selectedSkills.filter(skillId => allSkills.some(skill => skill.id === skillId));   ////

    const postData = {
        title: document.getElementById('editPostTitle').value,
        description: document.getElementById('editPostDescription').value,
        project_type: document.getElementById('editPostProjectType').value,
        people_required: parseInt(document.getElementById('editPostPeopleRequired').value),
        skill_ids: skillIds
    };

    try {
        const response = await authenticatedFetch(`/api/posts/${slug}/`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(postData)
        });

        if (response.ok) {
            bootstrap.Modal.getInstance(document.getElementById('editPostModal')).hide();
            await loadAllData();
        } else {
            const error = await response.json();
            showError(error.detail || error.skill_ids?.[0] || 'Failed to update post');
        }
    } catch (error) {
        console.error('Error updating post:', error);
        showError('Error updating post');
    }
}

function attachButtonHandlers() {
    document.querySelectorAll('[id^="edit-btn-"]').forEach(btn => {
        const slug = btn.id.replace('edit-btn-', '');
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            openEditModal(slug);
        });
    });

    document.querySelectorAll('[id^="delete-btn-"]').forEach(btn => {
        const slug = btn.id.replace('delete-btn-', '');
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            deletePost(slug);
        });
    });
}

function renderPosts() {
    const otherPosts = allPosts.filter(post => !post.is_owner);      
    if (otherPosts.length === 0) {
        elements.postsContainer.innerHTML = '<p class="text-muted text-center col-12">No posts available.</p>';
        return;
    }
    elements.postsContainer.innerHTML = otherPosts.map(post => createPostCard(post, false)).join('');
    attachButtonHandlers();
}

function renderMyPosts() {
    if (myPosts.length === 0) {
        elements.myPostsContainer.innerHTML = '<p class="text-muted text-center col-12">You haven\'t created any posts yet.</p>';
        return;
    }
    elements.myPostsContainer.innerHTML = myPosts.map(post => createPostCard(post, true)).join('');
    attachButtonHandlers();
}

async function filterPosts() {
    const type = elements.filterProjectType.value;
    await fetchPosts(type);
    await fetchMyPosts();
    renderPosts();
    renderMyPosts();
}

function clearFilters() {
    elements.filterProjectType.value = '';
    filterPosts();
}

async function loadAllData() {
    await fetchSkills();
    await fetchPosts();
    await fetchMyPosts();
    renderPosts();
    renderMyPosts();
}

function setupEventListeners() {
    elements.submitPostBtn.addEventListener('click', createPost);
    elements.saveEditBtn.addEventListener('click', saveEdit);
    elements.clearFilters.addEventListener('click', clearFilters);
    elements.filterProjectType.addEventListener('change', filterPosts);
}

async function init() {
    showLoading();
    
    await loadAllData();
    
    skillsSelectInstance = new TomSelect("#skillsSelect", {
        plugins: ['remove_button'],
        maxItems: 10,
        create: false,
        createOnBlur: false,
        addPrecedence: false,
        placeholder: "Select skills from the list...",
        options: allSkills.map(skill => ({ value: skill.id, text: skill.name })),
        valueField: 'value',
        labelField: 'text',
        searchField: 'text',
        onItemAdd: function(value, item) {
            const isValid = allSkills.some(skill => skill.id === value);
            if (!isValid) {
                this.removeItem(value, true);
                showError('Please select only existing skills from the dropdown list.');
            }
        }
    });
    
    setupEventListeners();
    hideLoading();
}

window.addEventListener('DOMContentLoaded', init);