document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const sendBtn = document.getElementById('send-btn');
    const spinner = document.getElementById('loading-spinner');

    function appendMessage(sender, text, isUser) {
        const msgDiv = document.createElement('div');
        msgDiv.className = isUser ? "flex items-start justify-end" : "flex items-start";
        
        const bubble = document.createElement('div');
        bubble.className = isUser 
            ? "bg-slate-800 text-white p-4 rounded-lg rounded-tr-none max-w-[80%] shadow-sm"
            : "bg-blue-100 text-blue-900 p-4 rounded-lg rounded-tl-none max-w-[80%] shadow-sm";
        
        bubble.innerHTML = `<p class="font-bold mb-1">${sender}</p><p class="whitespace-pre-wrap">${text}</p>`;
        msgDiv.appendChild(bubble);
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const question = userInput.value.trim();
        if (!question) return;

        // Add user message
        appendMessage("You", question, true);
        userInput.value = '';
        
        // UI Loading state
        sendBtn.disabled = true;
        spinner.classList.remove('hidden');

        try {
            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: question })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                appendMessage("Agent", data.answer, false);
            } else {
                appendMessage("Error", data.error || "Failed to get response.", false);
            }
        } catch (error) {
            console.error("Fetch error:", error);
            appendMessage("System Error", "Could not connect to the server.", false);
        } finally {
            sendBtn.disabled = false;
            spinner.classList.add('hidden');
        }
    });
});