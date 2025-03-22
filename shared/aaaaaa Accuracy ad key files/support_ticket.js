/**
 * password_strength.js
 * 
 * This JavaScript file provides a mechanism to evaluate password strength 
 * and offers feedback to users based on various strength criteria.
 * 
 * For both RLG Data and RLG Fans, it ensures the password meets security standards.
 */

function getPasswordStrength(password) {
    let strength = 0;
    const feedback = {
      length: "Weak (must be at least 8 characters)",
      lowercase: "Weak (include at least one lowercase letter)",
      uppercase: "Weak (include at least one uppercase letter)",
      number: "Weak (include at least one number)",
      special: "Weak (include at least one special character)",
    };
  
    // Check password length
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    
    // Check for lowercase letters
    if (/[a-z]/.test(password)) strength++;
    
    // Check for uppercase letters
    if (/[A-Z]/.test(password)) strength++;
    
    // Check for numbers
    if (/[0-9]/.test(password)) strength++;
    
    // Check for special characters
    if (/[\W_]/.test(password)) strength++;
  
    return {
      strength,
      feedback: getFeedback(strength),
    };
  }
  
  function getFeedback(strength) {
    if (strength <= 1) {
      return "Weak";
    } else if (strength <= 3) {
      return "Moderate";
    } else if (strength <= 5) {
      return "Strong";
    } else {
      return "Very Strong";
    }
  }
  
  /**
   * Display password strength to the user.
   * 
   * @param {string} password - The password entered by the user.
   */
  function displayPasswordStrength(password) {
    const result = getPasswordStrength(password);
  
    console.log(`Password Strength: ${result.feedback}`);
    console.log(`Strength Level: ${result.strength}/5`);
  
    // You can customize additional UI feedback here.
    // E.g., color changes, progress bars, icons, etc.
  }
  
  // Example usage in real-time password input
  document.getElementById('passwordInput').addEventListener('input', function() {
    const password = this.value;
    displayPasswordStrength(password);
  });
  