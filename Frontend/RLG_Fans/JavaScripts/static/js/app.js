// app.js

import axios from 'axios';
import io from 'socket.io-client';

// WebSocket connection setup
const socket = io(window.location.origin);

// Subscription actions
export const subscribeUser = (priceId) => async (dispatch) => {
  try {
    const response = await axios.post('/api/subscription', { price_id: priceId }, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
    });
    dispatch({
      type: 'SUBSCRIBE_SUCCESS',
      payload: response.data,
    });
  } catch (error) {
    dispatch({
      type: 'SUBSCRIBE_FAIL',
    });
  }
};

export const cancelSubscription = () => async (dispatch) => {
  try {
    await axios.delete('/api/subscription', {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
    });
    dispatch({
      type: 'CANCEL_SUBSCRIPTION_SUCCESS',
    });
  } catch (error) {
    dispatch({
      type: 'CANCEL_SUBSCRIPTION_FAIL',
    });
  }
};

// Function to handle notifications
export const handleNotifications = () => (dispatch) => {
  socket.on('notification', (notification) => {
    dispatch({
      type: 'NEW_NOTIFICATION',
      payload: notification,
    });
  });
};

// Real-time data updates
export const handleRealTimeUpdates = () => (dispatch) => {
  socket.on('real_time_update', (update) => {
    dispatch({
      type: 'REAL_TIME_UPDATE',
      payload: update,
    });
  });
};

// Fetching platform analytics data
export const fetchPlatformAnalytics = (platform) => async (dispatch) => {
  try {
    const response = await axios.get(`/api/analytics/${platform}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
    });
    dispatch({
      type: 'FETCH_ANALYTICS_SUCCESS',
      payload: response.data,
    });
  } catch (error) {
    dispatch({
      type: 'FETCH_ANALYTICS_FAIL',
    });
  }
};

// Utility function to validate URLs
export const isValidUrl = (url) => {
  const urlRegex = /^(https?|ftp):\/\/[^\s/$.?#].[^\s]*$/i;
  return urlRegex.test(url);
};

// Function to handle project creation
export const createProject = (projectData) => async (dispatch) => {
  try {
    const response = await axios.post('/api/projects', projectData, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
    });
    dispatch({
      type: 'CREATE_PROJECT_SUCCESS',
      payload: response.data,
    });
  } catch (error) {
    dispatch({
      type: 'CREATE_PROJECT_FAIL',
    });
  }
};

// Trigger a scraping task
export const startScraping = (url) => async (dispatch) => {
  if (!isValidUrl(url)) {
    alert('Please enter a valid URL.');
    return;
  }

  try {
    const response = await axios.post('/api/scrape', { url }, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
    });
    dispatch({
      type: 'SCRAPE_START_SUCCESS',
      payload: response.data,
    });
  } catch (error) {
    dispatch({
      type: 'SCRAPE_START_FAIL',
    });
  }
};

// Initialize notifications and real-time updates when the app starts
export const initializeApp = () => (dispatch) => {
  handleNotifications()(dispatch);
  handleRealTimeUpdates()(dispatch);
};

// Event listener for WebSocket connection status
socket.on('connect', () => console.log('Connected to WebSocket'));
socket.on('disconnect', () => console.log('Disconnected from WebSocket'));
