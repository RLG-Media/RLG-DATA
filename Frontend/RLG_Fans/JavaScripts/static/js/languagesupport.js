// Language Support Module
class LanguageSupport {
    constructor(config) {
      /**
       * Initialize the LanguageSupport module.
       *
       * @param {Object} config - Configuration for language support.
       * @param {string} config.defaultLanguage - The default language code (e.g., "en").
       * @param {Array} config.availableLanguages - List of available language codes and names.
       * @param {string} config.languageSelector - DOM selector for the language dropdown.
       * @param {string} config.translationEndpoint - API endpoint for fetching translations.
       */
      this.defaultLanguage = config.defaultLanguage || 'en';
      this.availableLanguages = config.availableLanguages || [];
      this.languageSelector = document.querySelector(config.languageSelector);
      this.translationEndpoint = config.translationEndpoint;
      this.currentLanguage = this.defaultLanguage;
  
      if (!this.languageSelector) {
        throw new Error(`Invalid selector for language dropdown: ${config.languageSelector}`);
      }
  
      this.initialize();
    }
  
    initialize() {
      /**
       * Initialize the module by populating the language dropdown
       * and setting event listeners.
       */
      this.populateLanguageDropdown();
      this.addEventListeners();
      this.setLanguage(this.defaultLanguage);
    }
  
    populateLanguageDropdown() {
      /**
       * Populate the language selector dropdown with available languages.
       */
      this.availableLanguages.forEach(({ code, name }) => {
        const option = document.createElement('option');
        option.value = code;
        option.textContent = name;
        this.languageSelector.appendChild(option);
      });
    }
  
    addEventListeners() {
      /**
       * Add event listener to handle language change.
       */
      this.languageSelector.addEventListener('change', async (event) => {
        const selectedLanguage = event.target.value;
        await this.setLanguage(selectedLanguage);
      });
    }
  
    async setLanguage(languageCode) {
      /**
       * Set the language for the application.
       *
       * @param {string} languageCode - The language code to switch to.
       */
      try {
        const translations = await this.fetchTranslations(languageCode);
        this.applyTranslations(translations);
        this.adjustDirectionality(languageCode);
        this.currentLanguage = languageCode;
        console.log(`Language switched to: ${languageCode}`);
      } catch (error) {
        console.error(`Failed to set language: ${error.message}`);
        alert('Error loading language. Please try again.');
      }
    }
  
    async fetchTranslations(languageCode) {
      /**
       * Fetch translations for the specified language from the API.
       *
       * @param {string} languageCode - The language code to fetch translations for.
       * @returns {Object} An object containing translation key-value pairs.
       */
      const response = await fetch(`${this.translationEndpoint}?lang=${languageCode}`);
      if (!response.ok) {
        throw new Error('Failed to fetch translations.');
      }
      return await response.json();
    }
  
    applyTranslations(translations) {
      /**
       * Apply translations to UI elements.
       *
       * @param {Object} translations - An object containing translation key-value pairs.
       */
      document.querySelectorAll('[data-translate]').forEach((element) => {
        const key = element.getAttribute('data-translate');
        if (translations[key]) {
          element.textContent = translations[key];
        }
      });
    }
  
    adjustDirectionality(languageCode) {
      /**
       * Adjust the document's directionality based on the language.
       *
       * @param {string} languageCode - The language code to determine directionality.
       */
      const rtlLanguages = ['ar', 'he', 'fa', 'ur'];
      document.documentElement.dir = rtlLanguages.includes(languageCode) ? 'rtl' : 'ltr';
    }
  }
  
  // Example Usage
  document.addEventListener('DOMContentLoaded', () => {
    const languageSupport = new LanguageSupport({
      defaultLanguage: 'en',
      availableLanguages: [
        { code: 'en', name: 'English' },
        { code: 'es', name: 'Spanish' },
        { code: 'fr', name: 'French' },
        { code: 'de', name: 'German' },
        { code: 'zh', name: 'Chinese (Simplified)' },
        { code: 'ar', name: 'Arabic' },
        { code: 'hi', name: 'Hindi' },
        { code: 'ru', name: 'Russian' },
        { code: 'ja', name: 'Japanese' },
        { code: 'ko', name: 'Korean' },
      ],
      languageSelector: '#languageSelector',
      translationEndpoint: '/api/translations',
    });
  });
  
  export default LanguageSupport;
  