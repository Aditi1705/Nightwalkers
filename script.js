document.getElementById('user_input').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        let userMessage = event.target.value;

        // Input validation
        if (userMessage.trim() === '') {
            return; // Do nothing if the message is empty
        }

        event.target.value = ''; // Clear the input field after submission

        // Display user message on the chatbox
        displayMessage("Alpha: " + userMessage, 'user-message');

        // Generate a unique user ID (for example, using a timestamp or random number)
        const userId = 'user_' + Date.now();  // Simple unique ID based on timestamp

        // Send user message to Flask backend and handle bot response
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_id: userId, message: userMessage })
        })
        .then(response => response.json())
        .then(data => {
            // Check if there's a valid response
            if (data && data.response) {
                // Display bot response
                displayMessage("Elder Kalix: " + data.response, 'bot-message');
            } else {
                console.error('No response from bot');  // Debugging line
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }
});

// Function to display messages in the chatbox
function displayMessage(message, className) {
    const messagesDiv = document.getElementById('messages');
    const messageElem = document.createElement('div');
    messageElem.className = className;
    messageElem.textContent = message;
    messagesDiv.appendChild(messageElem);
    messagesDiv.scrollTop = messagesDiv.scrollHeight; // Auto-scroll to the bottom
}
