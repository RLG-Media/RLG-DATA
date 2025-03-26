// notification_component.js

import React, { useEffect, useState } from 'react';
import './notification_component.css';

const NotificationComponent = ({ message, type = 'info', duration = 5000, onClose }) => {
    const [isVisible, setIsVisible] = useState(true);

    useEffect(() => {
        const timer = setTimeout(() => {
            setIsVisible(false);
            if (onClose) onClose();
        }, duration);

        return () => clearTimeout(timer);
    }, [duration, onClose]);

    if (!isVisible || !message) return null;

    return (
        <div className={`notification ${type}`}>
            <p>{message}</p>
            <button className="close-button" onClick={() => setIsVisible(false)}>✖</button>
        </div>
    );
};

export default NotificationComponent;
