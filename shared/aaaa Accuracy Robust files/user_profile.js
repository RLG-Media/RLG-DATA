document.addEventListener('DOMContentLoaded', () => {
    // Select elements from the DOM
    const editProfileButton = document.getElementById('edit-profile-btn');
    const saveProfileButton = document.getElementById('save-profile-btn');
    const cancelEditButton = document.getElementById('cancel-edit-btn');
    const profileForm = document.getElementById('profile-form');
    const userNameField = document.getElementById('user-name');
    const userEmailField = document.getElementById('user-email');
    const userPhoneField = document.getElementById('user-phone');
    const userAvatarField = document.getElementById('user-avatar');
    const userAvatarPreview = document.getElementById('avatar-preview');
    const errorMessage = document.getElementById('error-message');

    // Event listener to enable profile editing
    editProfileButton.addEventListener('click', () => {
        userNameField.removeAttribute('disabled');
        userEmailField.removeAttribute('disabled');
        userPhoneField.removeAttribute('disabled');
        userAvatarField.removeAttribute('disabled');
        saveProfileButton.style.display = 'inline-block';
        cancelEditButton.style.display = 'inline-block';
        editProfileButton.style.display = 'none';
    });

    // Event listener to cancel profile editing
    cancelEditButton.addEventListener('click', () => {
        location.reload(); // Reload the page to cancel editing
    });

    // Event listener to preview avatar image
    userAvatarField.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(event) {
                userAvatarPreview.src = event.target.result;
            };
            reader.readAsDataURL(file);
        }
    });

    // Event listener to handle form submission
    profileForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Collect form data
        const formData = new FormData(profileForm);
        const userData = {
            name: formData.get('name'),
            email: formData.get('email'),
            phone: formData.get('phone'),
            avatar: formData.get('avatar')
        };

        // Perform client-side validation
        if (!userData.name || !userData.email || !userData.phone) {
            errorMessage.textContent = 'All fields are required!';
            return;
        }

        // Sending data to the server
        fetch('/update-user-profile', {
            method: 'POST',
            body: JSON.stringify(userData),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Profile updated successfully!');
                location.reload(); // Refresh page to reflect changes
            } else {
                errorMessage.textContent = 'Error updating profile. Please try again.';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            errorMessage.textContent = 'Network error. Please try again later.';
        });
    });
});
