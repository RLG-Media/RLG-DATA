<template>
  <div class="error-page">
    <div class="error-content">
      <h1>{{ errorCode }}</h1>
      <h2>{{ errorTitle }}</h2>
      <p>{{ errorMessage }}</p>
      <div class="actions">
        <button @click="goHome" class="btn btn-primary">Go to Homepage</button>
        <button @click="retryAction" v-if="showRetry" class="btn btn-secondary">Retry</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "ErrorPage",
  props: {
    errorCode: {
      type: String,
      default: "404",
    },
    errorTitle: {
      type: String,
      default: "Page Not Found",
    },
    errorMessage: {
      type: String,
      default: "The page you are looking for might have been removed, had its name changed, or is temporarily unavailable.",
    },
    showRetry: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    goHome() {
      this.$router.push("/");
    },
    retryAction() {
      this.$emit("retry");
    },
  },
};
</script>

<style scoped>
.error-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f8f9fa;
}

.error-content {
  text-align: center;
  padding: 20px;
  max-width: 600px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.error-content h1 {
  font-size: 6rem;
  color: #dc3545;
  margin: 0;
}

.error-content h2 {
  font-size: 2rem;
  color: #343a40;
  margin: 10px 0;
}

.error-content p {
  color: #6c757d;
  font-size: 1rem;
  margin-bottom: 20px;
}

.actions {
  margin-top: 20px;
}

.actions .btn {
  padding: 10px 20px;
  font-size: 1rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.actions .btn-primary {
  background-color: #007bff;
  color: #fff;
}

.actions .btn-primary:hover {
  background-color: #0056b3;
}

.actions .btn-secondary {
  background-color: #6c757d;
  color: #fff;
  margin-left: 10px;
}

.actions .btn-secondary:hover {
  background-color: #495057;
}
</style>
