// UserSettings Class
class UserSettings {
    constructor(config) {
      /**
       * Initialize the UserSettings class.
       *
       * @param {Object} config - Configuration object for user settings.
       * @param {string} config.selector - DOM selector for the settings form.
       * @param {string} config.apiEndpoint - API endpoint for saving user settings.
       * @param {Object} config.defaults - Default settings values.
       */
      this.selector = config.selector;
      this.apiEndpoint = config.apiEndpoint;
      this.defaults = config.defaults || {};
      this.form = document.querySelector(this.selector);
  
      if (!this.form) {
        throw new Error(`Invalid selector: ${this.selector}`);
      }
  
      this.initialize();
    }
  
    initialize() {
      /**
       * Initialize the settings form with event listeners and default values.
       */
      this.loadSettings();
      this.addEventListeners();
    }
  
    async loadSettings() {
      /**
       * Load user settings from the API or use defaults.
       */
      try {
        const response = await fetch(`${this.apiEndpoint}/get`);
        if (!response.ok) {
          throw new Error('Failed to fetch user settings.');
        }
        const settings = await response.json();
        this.populateForm(settings);
      } catch (error) {
        console.error(error);
        this.populateForm(this.defaults); // Fallback to defaults
      }
    }
  
    populateForm(settings) {
      /**
       * Populate the form with settings values.
       *
       * @param {Object} settings - User settings data.
       */
      for (const [key, value] of Object.entries(settings)) {
        const input = this.form.querySelector(`[name="${key}"]`);
        if (input) {
          input.type === 'checkbox' ? (input.checked = !!value) : (input.value = value);
        }
      }
    }
  
    async saveSettings(data) {
      /**
       * Save user settings via the API.
       *
       * @param {Object} data - Settings data to be saved.
       */
      try {
        const response = await fetch(`${this.apiEndpoint}/save`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });
  
        if (!response.ok) {
          throw new Error('Failed to save user settings.');
        }
  
        alert('Settings saved successfully!');
      } catch (error) {
        console.error(error);
        alert('Failed to save settings. Please try again.');
      }
    }
  
    getFormData() {
      /**
       * Retrieve data from the form.
       *
       * @returns {Object} Form data as key-value pairs.
       */
      const formData = {};
      const inputs = this.form.querySelectorAll('input, select, textarea');
  
      inputs.forEach(input => {
        if (input.type === 'checkbox') {
          formData[input.name] = input.checked;
        } else {
          formData[input.name] = input.value;
        }
      });
  
      return formData;
    }
  
    validateForm(data) {
      /**
       * Validate the form data.
       *
       * @param {Object} data - Form data to validate.
       * @returns {boolean} True if the form is valid, false otherwise.
       */
      let isValid = true;
  
      Object.entries(data).forEach(([key, value]) => {
        const input = this.form.querySelector(`[name="${key}"]`);
        if (input && input.required && !value) {
          isValid = false;
          input.classList.add('invalid');
          input.addEventListener('input', () => input.classList.remove('invalid'));
        }
      });
  
      return isValid;
    }
  
    addEventListeners() {
      /**
       * Add event listeners for the form actions.
       */
      this.form.addEventListener('submit', async event => {
        event.preventDefault();
        const formData = this.getFormData();
  
        if (this.validateForm(formData)) {
          await this.saveSettings(formData);
        } else {
          alert('Please fill out all required fields.');
        }
      });
  
      // Reset to defaults
      const resetButton = this.form.querySelector('[data-action="reset"]');
      if (resetButton) {
        resetButton.addEventListener('click', event => {
          event.preventDefault();
          this.populateForm(this.defaults);
        });
      }
    }
  }
  
  // Example Usage
  document.addEventListener('DOMContentLoaded', () => {
    const userSettings = new UserSettings({
      selector: '#userSettingsForm',
      apiEndpoint: '/api/user/settings',
      defaults: {
        theme: 'light',
        notifications: true,
        emailUpdates: false,
      },
    });
  });
  
  export default UserSettings;
  