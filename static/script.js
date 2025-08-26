document.addEventListener('DOMContentLoaded', function() {
    const chatBox = document.getElementById('chat-box');
    const textInput = document.getElementById('text-input');
    const textSend = document.getElementById('text-send');
    const voiceButton = document.getElementById('voice-button');
    
    // Function to add message to chat
    function addMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');
        
        const messageP = document.createElement('p');
        messageP.textContent = message;
        
        messageDiv.appendChild(messageP);
        chatBox.appendChild(messageDiv);
        
        // Scroll to bottom
        chatBox.scrollTop = chatBox.scrollHeight;
    }
    
    // Function to send text command
    function sendTextCommand() {
        const command = textInput.value.trim();
        if (!command) return;
        
        addMessage(command, true);
        textInput.value = '';
        
        fetch('/text_command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: command })
        })
        .then(response => response.json())
        .then(data => {
            addMessage(data.response);
            
            // Speak the response
            fetch('/speak', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: data.response })
            });
            
            if (data.exit) {
                setTimeout(() => {
                    alert('Conversation ended. Refresh the page to start again.');
                }, 1000);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage('Sorry, there was an error processing your request.');
        });
    }
    
    // Event listener for text send button
    textSend.addEventListener('click', sendTextCommand);
    
    // Event listener for Enter key in text input
    textInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendTextCommand();
        }
    });
    
    // Event listener for voice button
    voiceButton.addEventListener('click', function() {
        voiceButton.classList.add('listening');
        voiceButton.textContent = 'Listening...';
        
        fetch('/voice_command', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            voiceButton.classList.remove('listening');
            voiceButton.textContent = '🎤 Speak';
            
            if (data.response) {
                addMessage(data.response);
                
                // Speak the response
                fetch('/speak', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ text: data.response })
                });
                
                if (data.exit) {
                    setTimeout(() => {
                        alert('Conversation ended. Refresh the page to start again.');
                    }, 1000);
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            voiceButton.classList.remove('listening');
            voiceButton.textContent = '🎤 Speak';
            addMessage('Sorry, there was an error with voice recognition.');
        });
    });
});