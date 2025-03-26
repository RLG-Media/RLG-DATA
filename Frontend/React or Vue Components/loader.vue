<template>
  <div v-if="isLoading" class="loader-container">
    <div class="spinner">
      <div class="double-bounce1"></div>
      <div class="double-bounce2"></div>
    </div>
    <p class="loading-text">{{ message }}</p>
  </div>
</template>

<script>
export default {
  name: "Loader",
  props: {
    isLoading: {
      type: Boolean,
      required: true,
    },
    message: {
      type: String,
      default: "Loading, please wait...",
    },
  },
};
</script>

<style scoped>
.loader-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 9999;
}

.spinner {
  width: 40px;
  height: 40px;
  position: relative;
}

.double-bounce1,
.double-bounce2 {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background-color: #007bff;
  opacity: 0.6;
  position: absolute;
  animation: bounce 2s infinite ease-in-out;
}

.double-bounce2 {
  animation-delay: -1s;
}

@keyframes bounce {
  0%, 100% {
    transform: scale(0);
  }
  50% {
    transform: scale(1);
  }
}

.loading-text {
  margin-top: 15px;
  font-size: 1.2em;
  color: #343a40;
  font-weight: bold;
}
</style>
