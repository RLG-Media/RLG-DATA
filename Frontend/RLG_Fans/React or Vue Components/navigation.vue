<template>
  <nav class="navbar">
    <div class="container">
      <!-- Logo -->
      <div class="navbar-brand">
        <router-link to="/" class="navbar-item">
          <img src="/assets/logo.png" alt="Logo" />
        </router-link>
        <!-- Mobile Menu Toggle -->
        <button
          class="navbar-burger"
          :class="{ 'is-active': isMenuOpen }"
          @click="toggleMenu"
          aria-label="menu"
          aria-expanded="false"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>
      </div>

      <!-- Links -->
      <div class="navbar-menu" :class="{ 'is-active': isMenuOpen }">
        <div class="navbar-start">
          <router-link to="/features" class="navbar-item">
            Features
          </router-link>
          <router-link to="/pricing" class="navbar-item">
            Pricing
          </router-link>
          <router-link to="/blog" class="navbar-item">
            Blog
          </router-link>
          <router-link to="/contact" class="navbar-item">
            Contact
          </router-link>
        </div>

        <!-- Authentication Links -->
        <div class="navbar-end">
          <router-link to="/login" class="navbar-item">
            Login
          </router-link>
          <router-link to="/signup" class="navbar-item button is-primary">
            Sign Up
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: "Navigation",
  data() {
    return {
      isMenuOpen: false,
    };
  },
  methods: {
    toggleMenu() {
      this.isMenuOpen = !this.isMenuOpen;
    },
  },
};
</script>

<style scoped>
/* General Navbar Styling */
.navbar {
  background-color: #ffffff;
  border-bottom: 1px solid #e5e5e5;
  padding: 0.5rem 1rem;
}

.navbar-item {
  font-size: 1rem;
  font-weight: 500;
  color: #4a4a4a;
}

.navbar-item:hover {
  color: #3273dc; /* Brand Primary Color */
}

.navbar-burger {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
}

/* Mobile Responsive Styles */
@media screen and (max-width: 768px) {
  .navbar-burger {
    display: block;
  }
  .navbar-menu {
    display: none;
  }
  .navbar-menu.is-active {
    display: block;
  }
  .navbar-item {
    display: block;
    padding: 0.75rem 1rem;
  }
}

/* Button Styles */
.button {
  font-weight: 600;
  border-radius: 4px;
}
.button.is-primary {
  background-color: #3273dc;
  color: white;
  border: none;
}
.button.is-primary:hover {
  background-color: #275aa8;
}
</style>
