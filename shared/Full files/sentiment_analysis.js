// sentiment_analysis.js

// Import required dependencies
import axios from "axios";

/**
 * SentimentAnalysis class to handle all logic and integrations for sentiment analysis.
 */
class SentimentAnalysis {
  constructor(apiEndpoint) {
    this.apiEndpoint = apiEndpoint || "/api/sentiment-analysis";
    this.textArea = document.getElementById("user-text");
    this.analyzeButton = document.getElementById("analyze-button");
    this.resetButton = document.getElementById("reset-button");
    this.resultsSection = document.getElementById("results-section");
    this.sentimentResult = document.getElementById("sentiment-result");
    this.confidenceScore = document.getElementById("confidence-score");
    this.loadingIndicator = null;
    this.init();
  }

  /**
   * Initialize the sentiment analysis functionality.
   */
  init() {
    // Attach event listeners to buttons
    if (this.analyzeButton) {
      this.analyzeButton.addEventListener("click", (e) => this.handleAnalyze(e));
    }
    if (this.resetButton) {
      this.resetButton.addEventListener("click", () => this.resetForm());
    }

    // Add loading indicator dynamically
    this.addLoadingIndicator();
  }

  /**
   * Add a loading indicator to enhance user experience.
   */
  addLoadingIndicator() {
    this.loadingIndicator = document.createElement("div");
    this.loadingIndicator.id = "loading-indicator";
    this.loadingIndicator.classList.add("hidden");
    this.loadingIndicator.innerHTML = `
      <div class="spinner"></div>
      <p>Analyzing sentiment, please wait...</p>
    `;
    document.body.appendChild(this.loadingIndicator);
  }

  /**
   * Handle the Analyze button click event.
   * @param {Event} e - The event object.
   */
  async handleAnalyze(e) {
    e.preventDefault();

    const userText = this.textArea?.value.trim();
    if (!userText) {
      alert("Please enter some text for analysis.");
      return;
    }

    try {
      // Show loading indicator
      this.toggleLoading(true);

      // Send the input text to the backend API
      const response = await axios.post(this.apiEndpoint, { text: userText });

      // Parse response and display results
      if (response?.data) {
        const { sentiment, confidence } = response.data;
        this.displayResults(sentiment, confidence);
      } else {
        throw new Error("Invalid response from server.");
      }
    } catch (error) {
      console.error("Error during sentiment analysis:", error);
      alert("Something went wrong. Please try again later.");
    } finally {
      // Hide loading indicator
      this.toggleLoading(false);
    }
  }

  /**
   * Display the sentiment analysis results.
   * @param {string} sentiment - The predicted sentiment.
   * @param {number} confidence - The confidence score.
   */
  displayResults(sentiment, confidence) {
    this.sentimentResult.textContent = sentiment || "Unknown";
    this.confidenceScore.textContent = `${(confidence * 100).toFixed(2)}%` || "N/A";
    this.resultsSection.classList.remove("hidden");
    this.textArea.parentElement.classList.add("hidden");
  }

  /**
   * Reset the form to its initial state.
   */
  resetForm() {
    this.textArea.value = "";
    this.textArea.parentElement.classList.remove("hidden");
    this.resultsSection.classList.add("hidden");
  }

  /**
   * Toggle the visibility of the loading indicator.
   * @param {boolean} show - Whether to show or hide the loading indicator.
   */
  toggleLoading(show) {
    if (this.loadingIndicator) {
      this.loadingIndicator.classList.toggle("hidden", !show);
    }
  }
}

// Initialize the SentimentAnalysis class on page load
document.addEventListener("DOMContentLoaded", () => {
  new SentimentAnalysis();
});
