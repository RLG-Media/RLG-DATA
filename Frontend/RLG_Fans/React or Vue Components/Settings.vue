<template>
  <div class="settings">
    <div class="settings-header">
      <h2>Settings</h2>
      <p>Manage your preferences and account settings below.</p>
    </div>

    <!-- Tabs for Different Setting Categories -->
    <div class="settings-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.name"
        :class="{ active: currentTab === tab.name }"
        @click="switchTab(tab.name)"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Settings Content -->
    <div class="settings-content">
      <!-- Account Settings -->
      <div v-if="currentTab === 'account'">
        <h3>Account Settings</h3>
        <div class="form-group">
          <label for="username">Username</label>
          <input
            type="text"
            id="username"
            v-model="settings.account.username"
          />
        </div>
        <div class="form-group">
          <label for="email">Email</label>
          <input
            type="email"
            id="email"
            v-model="settings.account.email"
          />
        </div>
        <button class="btn save-btn" @click="saveAccountSettings">
          Save Changes
        </button>
      </div>

      <!-- Privacy Settings -->
      <div v-if="currentTab === 'privacy'">
        <h3>Privacy Settings</h3>
        <div class="form-group">
          <label>
            <input
              type="checkbox"
              v-model="settings.privacy.showProfile"
            />
            Show profile publicly
          </label>
        </div>
        <div class="form-group">
          <label>
            <input
              type="checkbox"
              v-model="settings.privacy.receiveEmails"
            />
            Receive email notifications
          </label>
        </div>
        <button class="btn save-btn" @click="savePrivacySettings">
          Save Changes
        </button>
      </div>

      <!-- Notifications Settings -->
      <div v-if="currentTab === 'notifications'">
        <h3>Notifications</h3>
        <div class="form-group">
          <label>
            <input
              type="checkbox"
              v-model="settings.notifications.appNotifications"
            />
            Enable app notifications
          </label>
        </div>
        <div class="form-group">
          <label>
            <input
              type="checkbox"
              v-model="settings.notifications.emailNotifications"
            />
            Enable email notifications
          </label>
        </div>
        <button class="btn save-btn" @click="saveNotificationSettings">
          Save Changes
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Settings",
  data() {
    return {
      currentTab: "account", // Default tab
      tabs: [
        { name: "account", label: "Account" },
        { name: "privacy", label: "Privacy" },
        { name: "notifications", label: "Notifications" },
      ],
      settings: {
        account: {
          username: "JohnDoe",
          email: "john.doe@example.com",
        },
        privacy: {
          showProfile: true,
          receiveEmails: false,
        },
        notifications: {
          appNotifications: true,
          emailNotifications: true,
        },
      },
    };
  },
  methods: {
    switchTab(tabName) {
      this.currentTab = tabName;
    },
    saveAccountSettings() {
      // Save logic for account settings (e.g., API call)
      console.log("Account settings saved:", this.settings.account);
    },
    savePrivacySettings() {
      // Save logic for privacy settings (e.g., API call)
      console.log("Privacy settings saved:", this.settings.privacy);
    },
    saveNotificationSettings() {
      // Save logic for notification settings (e.g., API call)
      console.log("Notification settings saved:", this.settings.notifications);
    },
  },
};
</script>

<style scoped>
.settings {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.settings-header {
  text-align: center;
  margin-bottom: 20px;
}

.settings-tabs {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
}

.settings-tabs button {
  padding: 10px 20px;
  border: none;
  background: #f8f9fa;
  color: #343a40;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.settings-tabs button.active {
  background: #007bff;
  color: white;
}

.settings-tabs button:hover {
  background: #e2e6ea;
}

.settings-content {
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
}

input[type="text"],
input[type="email"],
button {
  width: 100%;
  padding: 10px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1rem;
}

button {
  background: #007bff;
  color: white;
  border: none;
  cursor: pointer;
  transition: background 0.3s;
}

button:hover {
  background: #0056b3;
}

button.save-btn {
  margin-top: 10px;
}
</style>
