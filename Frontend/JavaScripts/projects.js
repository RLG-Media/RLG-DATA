// Select DOM elements
const projectList = document.getElementById('projectList');
const projectModal = document.getElementById('projectModal');
const newProjectBtn = document.getElementById('newProjectBtn');
const closeModal = document.getElementById('closeModal');
const cancelModal = document.getElementById('cancelModal');
const projectForm = document.getElementById('projectForm');
const modalTitle = document.getElementById('modalTitle');
const projectIdField = document.getElementById('projectId');

// Global project data (Mockup for dynamic rendering; replace with API calls)
let projects = [];

// Event Listeners
newProjectBtn.addEventListener('click', () => openModal('Create New Project'));
closeModal.addEventListener('click', closeProjectModal);
cancelModal.addEventListener('click', closeProjectModal);
projectForm.addEventListener('submit', handleFormSubmit);

// Functions
/**
 * Fetches project data from the backend.
 */
async function fetchProjects() {
    try {
        const response = await fetch('/api/projects'); // Update with actual endpoint
        if (!response.ok) throw new Error('Failed to fetch projects');
        projects = await response.json();
        renderProjects();
    } catch (error) {
        console.error('Error fetching projects:', error);
        displayMessage('Failed to load projects. Please try again.', 'error');
    }
}

/**
 * Renders the project cards on the page.
 */
function renderProjects() {
    projectList.innerHTML = '';
    if (projects.length === 0) {
        projectList.innerHTML = '<p class="empty-state">No projects found. Create your first project!</p>';
        return;
    }

    projects.forEach((project) => {
        const projectCard = document.createElement('div');
        projectCard.classList.add('project-card');
        projectCard.innerHTML = `
            <h3>${project.name}</h3>
            <p>${project.description}</p>
            <div class="project-meta">
                <span>Start: ${formatDate(project.start_date)}</span>
                <span>End: ${formatDate(project.end_date)}</span>
            </div>
            <div class="project-actions">
                <button class="btn-edit" onclick="editProject(${project.id})">Edit</button>
                <button class="btn-delete" onclick="deleteProject(${project.id})">Delete</button>
            </div>
        `;
        projectList.appendChild(projectCard);
    });
}

/**
 * Opens the modal for creating or editing a project.
 * @param {string} title - Modal title (Create or Edit).
 * @param {Object} [project] - Optional project data for editing.
 */
function openModal(title, project = null) {
    modalTitle.textContent = title;
    if (project) {
        projectIdField.value = project.id;
        projectForm.projectName.value = project.name;
        projectForm.projectDescription.value = project.description;
        projectForm.startDate.value = project.start_date;
        projectForm.endDate.value = project.end_date;
    } else {
        projectIdField.value = '';
        projectForm.reset();
    }
    projectModal.style.display = 'block';
}

/**
 * Closes the project modal.
 */
function closeProjectModal() {
    projectModal.style.display = 'none';
    projectForm.reset();
}

/**
 * Handles form submission for creating or updating a project.
 * @param {Event} event - The form submit event.
 */
async function handleFormSubmit(event) {
    event.preventDefault();
    const projectData = {
        name: projectForm.projectName.value,
        description: projectForm.projectDescription.value,
        start_date: projectForm.startDate.value,
        end_date: projectForm.endDate.value,
    };

    try {
        const isEdit = projectIdField.value;
        const url = isEdit ? `/api/projects/${projectIdField.value}` : '/api/projects';
        const method = isEdit ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(projectData),
        });

        if (!response.ok) throw new Error('Failed to save project');
        displayMessage(`Project ${isEdit ? 'updated' : 'created'} successfully!`, 'success');
        closeProjectModal();
        fetchProjects();
    } catch (error) {
        console.error('Error saving project:', error);
        displayMessage('Failed to save project. Please try again.', 'error');
    }
}

/**
 * Edits a project by opening the modal with pre-filled data.
 * @param {number} id - Project ID.
 */
function editProject(id) {
    const project = projects.find((proj) => proj.id === id);
    if (project) openModal('Edit Project', project);
}

/**
 * Deletes a project.
 * @param {number} id - Project ID.
 */
async function deleteProject(id) {
    if (!confirm('Are you sure you want to delete this project?')) return;

    try {
        const response = await fetch(`/api/projects/${id}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Failed to delete project');
        displayMessage('Project deleted successfully!', 'success');
        fetchProjects();
    } catch (error) {
        console.error('Error deleting project:', error);
        displayMessage('Failed to delete project. Please try again.', 'error');
    }
}

/**
 * Displays a message to the user.
 * @param {string} message - Message to display.
 * @param {string} type - Message type (success or error).
 */
function displayMessage(message, type) {
    const messageBox = document.createElement('div');
    messageBox.className = `message-box ${type}`;
    messageBox.textContent = message;
    document.body.appendChild(messageBox);
    setTimeout(() => messageBox.remove(), 3000);
}

/**
 * Formats a date for display.
 * @param {string} dateString - ISO date string.
 * @returns {string} Formatted date string.
 */
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

// Initial fetch to populate projects
fetchProjects();
