/**
 * privacy_compliance.js
 * Comprehensive module for managing privacy compliance features
 * for RLG Data and RLG Fans.
 */

// Utility for managing cookies
const CookieManager = {
    setCookie(name, value, days) {
        const expires = new Date();
        expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
        document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Strict;Secure`;
    },
    getCookie(name) {
        const nameEQ = `${name}=`;
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.indexOf(nameEQ) === 0) {
                return cookie.substring(nameEQ.length, cookie.length);
            }
        }
        return null;
    },
    deleteCookie(name) {
        document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;SameSite=Strict;Secure`;
    },
};

// Consent Management
const ConsentManager = {
    consentGiven: false,

    initConsentBanner() {
        if (!CookieManager.getCookie('userConsent')) {
            this.showConsentBanner();
        }
    },

    showConsentBanner() {
        const banner = document.createElement('div');
        banner.id = 'consent-banner';
        banner.innerHTML = `
            <div class="consent-banner-content">
                <p>We use cookies to ensure you get the best experience on our website. By using our services, you agree to our 
                <a href="/privacy-policy.html" target="_blank">Privacy Policy</a>.</p>
                <button id="accept-consent" class="btn btn-primary">Accept</button>
                <button id="decline-consent" class="btn btn-secondary">Decline</button>
            </div>
        `;
        document.body.appendChild(banner);

        document.getElementById('accept-consent').addEventListener('click', () => {
            this.setUserConsent(true);
        });

        document.getElementById('decline-consent').addEventListener('click', () => {
            this.setUserConsent(false);
        });
    },

    setUserConsent(consent) {
        this.consentGiven = consent;
        CookieManager.setCookie('userConsent', consent, 365);
        document.getElementById('consent-banner').remove();

        if (consent) {
            console.log('User consent granted.');
        } else {
            console.log('User consent declined.');
        }
    },
};

// Data Access Requests
const DataAccessManager = {
    requestData(endpoint) {
        return fetch(endpoint, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${localStorage.getItem('userToken')}`,
            },
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`Request failed with status ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                console.log('Data Access Request:', data);
                return data;
            })
            .catch((error) => {
                console.error('Data Access Error:', error);
            });
    },

    deleteData(endpoint) {
        return fetch(endpoint, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${localStorage.getItem('userToken')}`,
            },
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`Request failed with status ${response.status}`);
                }
                console.log('User data deletion successful.');
            })
            .catch((error) => {
                console.error('Data Deletion Error:', error);
            });
    },
};

// Privacy Policy Update Notifications
const PrivacyPolicyNotifier = {
    initNotification() {
        const latestPolicyVersion = '1.2.0'; // Example version
        const userVersion = localStorage.getItem('policyVersion');

        if (!userVersion || userVersion !== latestPolicyVersion) {
            this.notifyPolicyUpdate(latestPolicyVersion);
        }
    },

    notifyPolicyUpdate(version) {
        const notification = document.createElement('div');
        notification.id = 'policy-notification';
        notification.innerHTML = `
            <div class="policy-notification-content">
                <p>We have updated our 
                <a href="/privacy-policy.html" target="_blank">Privacy Policy</a>. Please review the changes.</p>
                <button id="acknowledge-policy" class="btn btn-primary">Acknowledge</button>
            </div>
        `;
        document.body.appendChild(notification);

        document.getElementById('acknowledge-policy').addEventListener('click', () => {
            this.acknowledgePolicyUpdate(version);
        });
    },

    acknowledgePolicyUpdate(version) {
        localStorage.setItem('policyVersion', version);
        document.getElementById('policy-notification').remove();
        console.log('Privacy policy update acknowledged.');
    },
};

// Initialize Privacy Compliance
document.addEventListener('DOMContentLoaded', () => {
    ConsentManager.initConsentBanner();
    PrivacyPolicyNotifier.initNotification();
});
