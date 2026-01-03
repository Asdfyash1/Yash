document.addEventListener('DOMContentLoaded', () => {
    const settingsBtn = document.getElementById('settings-btn');
    const settingsModal = document.getElementById('settings-modal');
    const closeSettings = document.getElementById('close-settings');
    const saveSettings = document.getElementById('save-settings');
    const apiKeyInput = document.getElementById('api-key');
    const modelSelect = document.getElementById('model-select');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const messagesDiv = document.getElementById('messages');

    // Load settings from localStorage
    const savedApiKey = localStorage.getItem('nvidia_api_key');
    const savedModel = localStorage.getItem('nvidia_model');

    if (savedApiKey) {
        apiKeyInput.value = savedApiKey;
    }
    if (savedModel) {
        modelSelect.value = savedModel;
    } else {
        modelSelect.value = "meta/llama3-70b-instruct"; // Default
    }

    // Modal Handling
    settingsBtn.onclick = () => settingsModal.classList.remove('hidden');
    closeSettings.onclick = () => settingsModal.classList.add('hidden');
    window.onclick = (event) => {
        if (event.target == settingsModal) {
            settingsModal.classList.add('hidden');
        }
    };

    saveSettings.onclick = () => {
        const key = apiKeyInput.value.trim();
        const model = modelSelect.value;

        if (key) {
            localStorage.setItem('nvidia_api_key', key);
        } else {
            localStorage.removeItem('nvidia_api_key');
        }
        localStorage.setItem('nvidia_model', model);

        settingsModal.classList.add('hidden');
        addSystemMessage("Settings saved.");
    };

    // Auto-resize textarea
    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // Send Message Handling
    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        const apiKey = localStorage.getItem('nvidia_api_key');
        if (!apiKey) {
            addSystemMessage("Please set your NVIDIA API Key in settings first.");
            settingsModal.classList.remove('hidden');
            return;
        }

        const model = localStorage.getItem('nvidia_model') || "meta/llama3-70b-instruct";

        // Add user message
        addUserMessage(text);
        userInput.value = '';
        userInput.style.height = 'auto';

        // Show typing indicator or placeholder
        const botMsgDiv = addBotMessage("Thinking...");

        try {
            // "No security" implementation: Direct client-side call
            const response = await fetch('https://integrate.api.nvidia.com/v1/chat/completions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${apiKey}`
                },
                body: JSON.stringify({
                    model: model,
                    messages: [{role: "user", content: text}],
                    temperature: 0.5,
                    top_p: 1,
                    max_tokens: 1024,
                    stream: false
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || errorData.message || `API Error: ${response.status}`);
            }

            const data = await response.json();
            const reply = data.choices[0].message.content;

            // Update bot message
            botMsgDiv.textContent = reply; // Basic text content. For markdown, a library like marked.js would be needed.

        } catch (error) {
            botMsgDiv.classList.add('error');
            botMsgDiv.textContent = `Error: ${error.message}`;
        }
    }

    sendBtn.onclick = sendMessage;
    userInput.onkeydown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    function addUserMessage(text) {
        const div = document.createElement('div');
        div.className = 'message user';
        div.textContent = text;
        messagesDiv.appendChild(div);
        scrollToBottom();
    }

    function addBotMessage(text) {
        const div = document.createElement('div');
        div.className = 'message bot';
        div.textContent = text;
        messagesDiv.appendChild(div);
        scrollToBottom();
        return div;
    }

    function addSystemMessage(text) {
        const div = document.createElement('div');
        div.className = 'message system';
        div.textContent = text;
        messagesDiv.appendChild(div);
        scrollToBottom();
    }

    function scrollToBottom() {
        const chatContainer = document.getElementById('chat-container');
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
});
