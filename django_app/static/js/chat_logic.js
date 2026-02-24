document.addEventListener('DOMContentLoaded', () => {
    const authOverlay = document.getElementById('auth-overlay');
    const loginForm = document.getElementById('login-form');
    const passcodeIn = document.getElementById('auth-passcode');
    const loginError = document.getElementById('login-error');
    
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const sendBtn = document.getElementById('send-btn');
    const spinner = document.getElementById('loading-spinner');

    const currentToken = sessionStorage.getItem('jwt_token');
    if (currentToken) {
        authOverlay.classList.add('hidden');
    }

    // Execution Flow 1: Handle Login & JWT Issuance
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const passcode = passcodeIn.value.trim();
        
        try {
            const response = await fetch('/api/login/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ passcode: passcode })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Store token securely in Session Storage
                sessionStorage.setItem('jwt_token', data.token);
                
                // Unlock the interface gracefully
                authOverlay.classList.add('opacity-0');
                setTimeout(() => authOverlay.classList.add('hidden'), 500);
            } else {
                loginError.textContent = data.error || "Authentication failed. Please verify your passcode.";
                loginError.classList.remove('hidden');
            }
        } catch (error) {
            loginError.textContent = "Server connection error. Please try again later.";
            loginError.classList.remove('hidden');
        }
    });

    // Helper function to render chat messages
    function appendMessage(sender, text, isUser, isError=false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = isUser ? "flex items-start justify-end" : "flex items-start";
        
        let bubbleClass = isUser 
            ? "bg-slate-800 text-white p-4 rounded-lg rounded-tr-none max-w-[80%] shadow-sm"
            : "bg-blue-100 text-blue-900 p-4 rounded-lg rounded-tl-none max-w-[80%] shadow-sm";
            
        if (isError) {
            bubbleClass = "bg-red-100 text-red-800 p-4 rounded-lg rounded-tl-none max-w-[80%] shadow-sm border border-red-300";
        }
        
        const bubble = document.createElement('div');
        bubble.className = bubbleClass;
        bubble.innerHTML = `<p class="font-bold mb-1">${sender}</p><p class="whitespace-pre-wrap">${text}</p>`;
        
        msgDiv.appendChild(bubble);
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Execution flow 2: Handle chat requests with bearer authentication
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const question = userInput.value.trim();
        const token = sessionStorage.getItem('jwt_token');

        if (!question) return;
        if (!token) {
            alert("Security Error: JWT Token not found. Please refresh the page and authenticate.");
            return;
        }

        appendMessage("You", question, true);
        userInput.value = '';
        
        sendBtn.disabled = true;
        spinner.classList.remove('hidden');

        try {
            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ question: question })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                appendMessage("Agent", data.answer, false);
            } else {
                appendMessage("System Alert", data.error, false, true);
                if (response.status === 401) {
                    sessionStorage.removeItem('jwt_token');
                    setTimeout(() => window.location.reload(), 2000);
                }
            }
        } catch (error) {
            appendMessage("System Error", "Could not connect to the processing server.", false, true);
        } finally {
            sendBtn.disabled = false;
            spinner.classList.add('hidden');
        }
    });
});