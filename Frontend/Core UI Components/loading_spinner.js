// loading_spinner.js

import React from 'react';
import './loading_spinner.css'; // Import CSS for spinner styling

const LoadingSpinner = ({ isVisible = false, message = "Loading..." }) => {
    if (!isVisible) return null;

    return (
        <div className="loading-spinner-overlay">
            <div className="loading-spinner-container">
                <div className="spinner">
                    <div className="double-bounce1"></div>
                    <div className="double-bounce2"></div>
                </div>
                <p className="loading-message">{message}</p>
            </div>
        </div>
    );
};

export default LoadingSpinner;
