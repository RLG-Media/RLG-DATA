<template>
  <transition name="fade">
    <div v-if="isVisible" class="modal-overlay" @click="closeOnOverlay">
      <div class="modal-container" @click.stop>
        <header class="modal-header">
          <h3 class="modal-title">{{ title }}</h3>
          <button class="modal-close" @click="closeModal">&times;</button>
        </header>
        <div class="modal-body">
          <slot></slot>
        </div>
        <footer v-if="showFooter" class="modal-footer">
          <slot name="footer">
            <button class="btn btn-primary" @click="confirmModal">Confirm</button>
            <button class="btn btn-secondary" @click="closeModal">Cancel</button>
          </slot>
        </footer>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: "Modal",
  props: {
    isVisible: {
      type: Boolean,
      required: true,
    },
    title: {
      type: String,
      default: "Modal Title",
    },
    showFooter: {
      type: Boolean,
      default: true,
    },
    closeOnOverlayClick: {
      type: Boolean,
      default: true,
    },
  },
  methods: {
    closeModal() {
      this.$emit("close");
    },
    confirmModal() {
      this.$emit("confirm");
    },
    closeOnOverlay() {
      if (this.closeOnOverlayClick) {
        this.closeModal();
      }
    },
  },
};
</script>

<style scoped>
/* Modal Overlay */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

/* Modal Container */
.modal-container {
  background: #fff;
  border-radius: 8px;
  max-width: 600px;
  width: 90%;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  animation: slideIn 0.3s ease-out;
}

/* Modal Header */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 500;
  margin: 0;
}

.modal-close {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  color: #6c757d;
  cursor: pointer;
  transition: color 0.2s ease-in-out;
}

.modal-close:hover {
  color: #343a40;
}

/* Modal Body */
.modal-body {
  padding: 20px;
  font-size: 1rem;
  line-height: 1.5;
  color: #212529;
}

/* Modal Footer */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 15px;
  background-color: #f8f9fa;
  border-top: 1px solid #dee2e6;
}

.btn {
  padding: 8px 15px;
  margin: 0 5px;
  border-radius: 4px;
  font-size: 0.875rem;
  cursor: pointer;
}

.btn-primary {
  background-color: #007bff;
  color: #fff;
  border: none;
  transition: background-color 0.3s ease;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #6c757d;
  color: #fff;
  border: none;
  transition: background-color 0.3s ease;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

/* Animations */
@keyframes slideIn {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
</style>
