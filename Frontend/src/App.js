import axios from 'axios';

// Subscription Action Types
export const SUBSCRIBE_SUCCESS = 'SUBSCRIBE_SUCCESS';
export const SUBSCRIBE_FAIL = 'SUBSCRIBE_FAIL';
export const CANCEL_SUBSCRIPTION_SUCCESS = 'CANCEL_SUBSCRIPTION_SUCCESS';
export const CANCEL_SUBSCRIPTION_FAIL = 'CANCEL_SUBSCRIPTION_FAIL';

// Subscribe User
export const subscribeUser = (priceId) => async (dispatch) => {
  try {
    const token = localStorage.getItem('token');
    const headers = {
      Authorization: `Bearer ${token}`,
    };

    const response = await axios.post(
      '/api/subscription',
      { price_id: priceId },
      { headers }
    );

    dispatch({
      type: SUBSCRIBE_SUCCESS,
      payload: response.data,
    });
  } catch (error) {
    console.error('Subscription failed:', error);
    dispatch({
      type: SUBSCRIBE_FAIL,
      payload: error.response?.data || 'Subscription failed',
    });
  }
};

// Cancel Subscription
export const cancelSubscription = () => async (dispatch) => {
  try {
    const token = localStorage.getItem('token');
    const headers = {
      Authorization: `Bearer ${token}`,
    };

    await axios.delete('/api/subscription', { headers });

    dispatch({
      type: CANCEL_SUBSCRIPTION_SUCCESS,
    });
  } catch (error) {
    console.error('Subscription cancellation failed:', error);
    dispatch({
      type: CANCEL_SUBSCRIPTION_FAIL,
      payload: error.response?.data || 'Cancellation failed',
    });
  }
};
