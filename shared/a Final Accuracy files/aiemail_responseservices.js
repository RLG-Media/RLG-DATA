// JavaScript file for AI Email Response Service

// DOM Elements
const emailPromptInput = document.getElementById('email-prompt');
const emailResponseForm = document.getElementById('email-response-form');
const responseOutput = document.getElementById('response-text');
const historyList = document.getElementById('history-list');

// Event Listener for Form Submission
emailResponseForm.addEventListener('submit', async function (event) {
    event.preventDefault();

    const prompt = emailPromptInput.value.trim();

    if (!prompt) {
        alert('Please enter a prompt.');
        return;
    }

    responseOutput.textContent = 'Generating response...';

    try {
        const response = await fetch('/generate-response', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt })
        });

        if (!response.ok) {
            throw new Error('Failed to generate response.');
        }

        const data = await response.json();
        const generatedResponse = data.response || 'No response generated.';

        // Update the response output
        responseOutput.textContent = generatedResponse;

        // Add to history
        const historyItem = document.createElement('li');
        historyItem.textContent = generatedResponse;
        historyList.appendChild(historyItem);
    } catch (error) {
        responseOutput.textContent = 'Error: Unable to generate response.';
        console.error('Error:', error);
    }
});
