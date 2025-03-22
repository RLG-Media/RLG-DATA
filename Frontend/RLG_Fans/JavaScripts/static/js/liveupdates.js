// Live Updates Module
class LiveUpdates {
    constructor(config) {
      /**
       * Initialize the Live Updates module.
       *
       * @param {Object} config - Configuration options for the live updates.
       * @param {string} config.websocketUrl - WebSocket URL for live updates.
       * @param {string} config.dataContainerSelector - Selector for the container where data is displayed.
       * @param {function} config.onDataReceived - Callback function for handling received data.
       * @param {number} config.reconnectInterval - Interval (ms) for reconnecting on WebSocket failure.
       */
      this.websocketUrl = config.websocketUrl;
      this.dataContainer = document.querySelector(config.dataContainerSelector);
      this.onDataReceived = config.onDataReceived || this.defaultDataHandler;
      this.reconnectInterval = config.reconnectInterval || 5000;
      this.websocket = null;
      this.retryTimeout = null;
  
      if (!this.dataContainer) {
        throw new Error(`Invalid container selector: ${config.dataContainerSelector}`);
      }
  
      this.init();
    }
  
    init() {
      /**
       * Initialize WebSocket connection and start listening for updates.
       */
      this.connectWebSocket();
    }
  
    connectWebSocket() {
      /**
       * Establish WebSocket connection.
       */
      console.log('Connecting to WebSocket...');
      this.websocket = new WebSocket(this.websocketUrl);
  
      this.websocket.onopen = () => {
        console.log('WebSocket connected.');
      };
  
      this.websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.onDataReceived(data);
      };
  
      this.websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
  
      this.websocket.onclose = (event) => {
        console.warn('WebSocket closed:', event.reason);
        this.retryConnection();
      };
    }
  
    retryConnection() {
      /**
       * Retry WebSocket connection after a delay.
       */
      if (this.retryTimeout) clearTimeout(this.retryTimeout);
  
      console.log(`Reconnecting in ${this.reconnectInterval / 1000} seconds...`);
      this.retryTimeout = setTimeout(() => this.connectWebSocket(), this.reconnectInterval);
    }
  
    sendMessage(message) {
      /**
       * Send a message through the WebSocket.
       *
       * @param {Object} message - The message object to send.
       */
      if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
        this.websocket.send(JSON.stringify(message));
      } else {
        console.warn('WebSocket is not connected. Message not sent:', message);
      }
    }
  
    defaultDataHandler(data) {
      /**
       * Default handler for incoming data.
       *
       * @param {Object} data - The data received through the WebSocket.
       */
      console.log('Received data:', data);
  
      // Example: Update the container with the latest data
      if (this.dataContainer) {
        this.dataContainer.innerHTML = `
          <div class="live-update">
            <h4>Live Data Update</h4>
            <pre>${JSON.stringify(data, null, 2)}</pre>
          </div>
        `;
      }
    }
  
    disconnect() {
      /**
       * Disconnect from the WebSocket and clear reconnection attempts.
       */
      if (this.websocket) {
        this.websocket.close();
        this.websocket = null;
      }
  
      if (this.retryTimeout) {
        clearTimeout(this.retryTimeout);
        this.retryTimeout = null;
      }
  
      console.log('WebSocket disconnected.');
    }
  }
  
  // Example Usage
  document.addEventListener('DOMContentLoaded', () => {
    const liveUpdates = new LiveUpdates({
      websocketUrl: 'wss://example.com/live-updates',
      dataContainerSelector: '#liveUpdatesContainer',
      reconnectInterval: 3000,
      onDataReceived: (data) => {
        console.log('Custom data received handler:', data);
  
        // Example: Update UI with the received data
        const container = document.querySelector('#liveUpdatesContainer');
        if (container) {
          container.innerHTML = `
            <div class="live-update">
              <h4>Latest Update</h4>
              <pre>${JSON.stringify(data, null, 2)}</pre>
            </div>
          `;
        }
      },
    });
  
    // Optional: Send a test message after 5 seconds
    setTimeout(() => {
      liveUpdates.sendMessage({ action: 'subscribe', topic: 'dashboard' });
    }, 5000);
  });
  
  export default LiveUpdates;
  