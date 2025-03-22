<template>
  <transition name="fade">
    <div v-if="isVisible" :class="['notification-banner', type]" @click="dismissNotification">
      <div class="notification-content">
        <span class="notification-icon">
          <i :class="iconClass"></i>
        </span>
        <div class="notification-message">
          <h4>{{ title }}</h4>
          <p>{{ message }}</p>
        </div>
      </div>
      <button v-if="dismissible" class="close-btn" @click.stop="dismissNotification">
        &times;
      </button>
    </div>
  </transition>
</template>

<script>
export default {
  name: "NotificationBanner",
  props: {
    type: {
      type: String,
      default: "info", // Options: 'info', 'success', 'error', 'warning'
    },
    title: {
      type: String,
      default: "Notification",
    },
    message: {
      type: String,
      required: true,
    },
    dismissible: {
      type: Boolean,
      default: true,
    },
    autoDismiss: {
      type: Boolean,
      default: false,
    },
    duration: {
      type: Number,
      default: 5000, // 5 seconds
    },
  },
  data() {
    return {
      isVisible: true,
    };
  },
  computed: {
    iconClass() {
      switch (this.type) {
        case "success":
          return "fas fa-check-circle";
        case "error":
          return "fas fa-times-circle";
        case "warning":
          return "fas fa-exclamation-triangle";
        default:
          return "fas fa-info-circle";
      }
    },
  },
  mounted() {
    if (this.autoDismiss) {
      setTimeout(() => {
        this.dismissNotification();
      }, this.duration);
    }
  },
  methods: {
    dismissNotification() {
      this.isVisible = false;
      this.$emit("dismiss");
    },
  },
};
</script>

<style scoped>
.notification-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  border-radius: 5px;
  margin: 10px 0;
  color: #fff;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease-in-out;
}

.notification-banner.info {
  background-color: #007bff;
}

.notification-banner.success {
  background-color: #28a745;
}

.notification-banner.error {
  background-color: #dc3545;
}

.notification-banner.warning {
  background-color: #ffc107;
  color: #343a40;
}

.notification-content {
  display: flex;
  align-items: center;
}

.notification-icon {
  margin-right: 15px;
  font-size: 1.5rem;
}

.notification-message h4 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: bold;
}

.notification-message p {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.5;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  color: inherit;
  cursor: pointer;
}

.close-btn:hover {
  color: #ccc;
}

/* Transition Effect */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
</style>
