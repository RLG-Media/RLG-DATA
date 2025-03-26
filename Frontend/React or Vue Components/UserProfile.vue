<template>
  <div class="user-profile">
    <!-- Header Section -->
    <div class="profile-header">
      <h2>User Profile</h2>
      <button class="btn edit-btn" @click="editProfile">
        Edit Profile
      </button>
    </div>

    <!-- Profile Picture -->
    <div class="profile-picture">
      <img :src="user.avatar || defaultAvatar" alt="Profile Picture" />
      <input
        type="file"
        ref="fileInput"
        accept="image/*"
        @change="uploadAvatar"
        style="display: none;"
      />
      <button class="btn upload-btn" @click="triggerFileInput">
        Upload New Picture
      </button>
    </div>

    <!-- User Information -->
    <div class="profile-info">
      <div class="info-item">
        <span class="label">Name:</span>
        <span class="value">{{ user.name }}</span>
      </div>
      <div class="info-item">
        <span class="label">Email:</span>
        <span class="value">{{ user.email }}</span>
      </div>
      <div class="info-item">
        <span class="label">Role:</span>
        <span class="value">{{ user.role }}</span>
      </div>
    </div>

    <!-- Save Changes Button -->
    <div v-if="isEditing" class="save-changes">
      <button class="btn save-btn" @click="saveProfile">Save Changes</button>
      <button class="btn cancel-btn" @click="cancelEdit">Cancel</button>
    </div>
  </div>
</template>

<script>
export default {
  name: "UserProfile",
  data() {
    return {
      user: {
        name: "John Doe",
        email: "john.doe@example.com",
        role: "Admin",
        avatar: null,
      },
      defaultAvatar: "/assets/default-avatar.png",
      isEditing: false,
    };
  },
  methods: {
    editProfile() {
      this.isEditing = true;
    },
    cancelEdit() {
      this.isEditing = false;
    },
    saveProfile() {
      // Add your save logic here (API call to save user profile data)
      console.log("Saving user profile data:", this.user);
      this.isEditing = false;
    },
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    uploadAvatar(event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.user.avatar = e.target.result;
          // Optionally, send the file to the server here
        };
        reader.readAsDataURL(file);
      }
    },
  },
};
</script>

<style scoped>
.user-profile {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  background: #ffffff;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profile-picture {
  text-align: center;
  margin: 20px 0;
}

.profile-picture img {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  border: 2px solid #ddd;
}

.profile-info {
  margin: 20px 0;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin: 10px 0;
}

.label {
  font-weight: bold;
}

.value {
  color: #555;
}

.save-changes {
  display: flex;
  justify-content: space-between;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.edit-btn {
  background-color: #007bff;
  color: white;
}

.upload-btn {
  background-color: #28a745;
  color: white;
}

.save-btn {
  background-color: #28a745;
  color: white;
}

.cancel-btn {
  background-color: #dc3545;
  color: white;
}
</style>
