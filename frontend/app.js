document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const fileInput = document.getElementById('file-input');
    const uploadBtn = document.getElementById('upload-btn');
    const dropArea = document.getElementById('drop-area');
    const fileInfo = document.getElementById('file-info');
    const uploadProgress = document.getElementById('upload-progress');
    const progressBar = document.getElementById('progress-bar');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const chatMessages = document.getElementById('chat-messages');
    const sessionStatus = document.getElementById('session-status');

    let sessionId = null;
    const API_BASE_URL = 'http://localhost:8000';

    // Event Listeners
    uploadBtn.addEventListener('click', () => fileInput.click());
    
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });

    dropArea.addEventListener('drop', handleDrop, false);
    
    chatForm.addEventListener('submit', handleChatSubmit);

    // Functions
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight() {
        dropArea.classList.add('border-blue-500', 'bg-blue-50');
    }

    function unhighlight() {
        dropArea.classList.remove('border-blue-500', 'bg-blue-50');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length) {
            fileInput.files = files;
            handleFileSelect({ target: fileInput });
        }
    }

    async function handleFileSelect(event) {
        const file = event.target.files[0];
        if (!file) return;

        if (file.type !== 'application/pdf') {
            showMessage('Please upload a PDF file', 'error');
            return;
        }

        fileInfo.textContent = `Selected: ${file.name} (${formatFileSize(file.size)})`;
        uploadProgress.classList.remove('hidden');
        
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${API_BASE_URL}/upload`, {
                method: 'PUT',
                body: formData,
                // Progress handling
                onUploadProgress: (progressEvent) => {
                    const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    progressBar.style.width = `${percentCompleted}%`;
                }
            });

            const data = await response.json();
            
            if (data.success) {
                sessionId = data.data.session_id;
                sessionStatus.textContent = 'Document uploaded successfully! You can now ask questions.';
                sessionStatus.className = 'text-sm text-green-600';
                userInput.disabled = false;
                sendBtn.disabled = false;
                showMessage('Document uploaded successfully!', 'success');
                addMessage('assistant', 'I\'ve processed your document. What would you like to know?');
            } else {
                throw new Error(data.message || 'Failed to upload file');
            }
        } catch (error) {
            console.error('Upload error:', error);
            showMessage(`Error: ${error.message}`, 'error');
        } finally {
            uploadProgress.classList.add('hidden');
            progressBar.style.width = '0%';
        }
    }

    async function handleChatSubmit(e) {
        e.preventDefault();
        
        const message = userInput.value.trim();
        if (!message || !sessionId) return;

        // Add user message to chat
        addMessage('user', message);
        userInput.value = '';
        
        // Disable input while waiting for response
        userInput.disabled = true;
        sendBtn.disabled = true;
        
        // Show typing indicator
        const typingId = 'typing-' + Date.now();
        addMessage('assistant', '', typingId);
        
        try {
            const response = await fetch(`${API_BASE_URL}/prompt`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    prompt: message
                })
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            const typingElement = document.getElementById(typingId);
            if (typingElement) {
                typingElement.remove();
            }
            
            if (data.success) {
                addMessage('assistant', data.data.answer);
            } else {
                throw new Error(data.message || 'Failed to get response');
            }
        } catch (error) {
            console.error('Chat error:', error);
            addMessage('assistant', `Sorry, I encountered an error: ${error.message}`);
        } finally {
            // Re-enable input
            userInput.disabled = false;
            sendBtn.disabled = false;
            userInput.focus();
        }
    }

    function addMessage(role, content, messageId = '') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'}`;
        messageDiv.id = messageId;
        
        const bubble = document.createElement('div');
        bubble.className = `max-w-3/4 p-3 rounded-lg ${
            role === 'user' 
                ? 'bg-blue-500 text-white rounded-br-none' 
                : 'bg-gray-100 text-gray-800 rounded-bl-none'
        }`;
        
        if (content) {
            bubble.textContent = content;
        } else {
            bubble.className += ' typing-indicator';
            bubble.textContent = 'Thinking';
        }
        
        messageDiv.appendChild(bubble);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showMessage(message, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `p-3 mb-4 rounded-lg ${
            type === 'error' ? 'bg-red-100 text-red-700' : 
            type === 'success' ? 'bg-green-100 text-green-700' : 
            'bg-blue-100 text-blue-700'
        }`;
        messageDiv.textContent = message;
        
        // Insert after the upload section
        const uploadSection = document.querySelector('.bg-white.rounded-lg.shadow-md');
        uploadSection.parentNode.insertBefore(messageDiv, uploadSection.nextSibling);
        
        // Remove after 5 seconds
        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
});
