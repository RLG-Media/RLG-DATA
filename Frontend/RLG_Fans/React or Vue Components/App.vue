<template>
  <div id="app">
    <!-- Header Section -->
    <Navbar />

    <!-- Sidebar Section -->
    <Sidebar v-if="isSidebarVisible" />

    <!-- Main Content -->
    <div class="main-content" :class="{ 'expanded': !isSidebarVisible }">
      <Loader v-if="loading" />
      <router-view v-else />
    </div>

    <!-- Footer -->
    <Footer />
  </div>
</template>

<script>
import Navbar from './Navbar.vue';
import Sidebar from './Sidebar.vue';
import Footer from './Footer.vue';
import Loader from './Loader.vue';
import { mapState } from 'vuex';

export default {
  components: {
    Navbar,
    Sidebar,
    Footer,
    Loader,
  },
  data() {
    return {
      loading: false, // Default loading state
    };
  },
  computed: {
    ...mapState({
      isSidebarVisible: (state) => state.ui.isSidebarVisible, // Example: Vuex state for sidebar visibility
      globalLoading: (state) => state.ui.globalLoading, // Example: Vuex state for global loading
    }),
  },
  watch: {
    globalLoading(newValue) {
      this.loading = newValue; // Sync Vuex global loading state
    },
    $route(to, from) {
      // Trigger loader on route change
      this.showLoader();
    },
  },
  methods: {
    showLoader() {
      this.loading = true;
      setTimeout(() => {
        this.loading = false; // Simulate loading completion
      }, 2000); // Adjust based on actual conditions
    },
  },
};
</script>

<style scoped>
/* Basic layout styling */
#app {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.main-content {
  flex-grow: 1;
  transition: margin-left 0.3s;
}

.main-content.expanded {
  margin-left: 0;
}

.main-content:not(.expanded) {
  margin-left: 240px; /* Sidebar width */
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
  }
}
</style>
