// main.js - Main Application Logic

import { sendMessageToAI, streamMessageFromAI, API_CONFIG } from './api.js';

document.addEventListener('DOMContentLoaded', function() {
  const chatMessages = document.getElementById('chat-messages');
  const userInput = document.getElementById('user-input');
  const sendButton = document.querySelector('.send-btn');
  const modelSelect = document.getElementById('model-select');
  const temperatureSlider = document.getElementById('temperature');
  const maxTokensSlider = document.getElementById('max-tokens');
  const topPSlider = document.getElementById('top-p');
  const newChatBtn = document.querySelector('.new-chat-btn');
  const streamToggle = document.getElementById('stream-toggle');

  let chatHistory = [];

  const updateSettingValue = (slider) => {
    const valueDisplay = slider.parentElement.querySelector('.setting-value');
    valueDisplay.textContent = slider.value;
  };

  [temperatureSlider, maxTokensSlider, topPSlider].forEach(updateSettingValue);
  temperatureSlider.addEventListener('input', () => updateSettingValue(temperatureSlider));
  maxTokensSlider.addEventListener('input', () => updateSettingValue(maxTokensSlider));
  topPSlider.addEventListener('input', () => updateSettingValue(topPSlider));

  const addMessage = (content, sender) => {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    messageDiv.innerHTML = `<div class="message-content">${escapeHtml(content)}</div>`;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    chatHistory.push({ role: sender === 'user' ? 'user' : 'assistant', content });
    return messageDiv;
  };

  const showTypingIndicator = () => {
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'message bot-message typing-indicator-container';
    typingIndicator.innerHTML = `
      <div class="message-content typing-indicator">
        <span></span>
        <span></span>
        <span></span>
      </div>
    `;
    chatMessages.appendChild(typingIndicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return typingIndicator;
  };

  const escapeHtml = (unsafe) => {
    return unsafe
      .replaceAll(/&/g, "&amp;")
      .replaceAll(/</g, "&lt;")
      .replaceAll(/>/g, "&gt;")
      .replaceAll(/"/g, "&quot;")
      .replaceAll(/'/g, "&#039;");
  };

  const sendMessage = async () => {
    const message = userInput.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    userInput.value = '';

    const typingIndicator = showTypingIndicator();

    try {
      const params = {
        temperature: parseFloat(temperatureSlider.value),
        max_tokens: parseInt(maxTokensSlider.value, 10),
        top_p: parseFloat(topPSlider.value)
      };

      if (streamToggle && streamToggle.checked) {
        const botDiv = addMessage('', 'bot');
        await streamMessageFromAI(message, {
          model: modelSelect.value || API_CONFIG.default_model,
          params: { ...params, stream: true },
          onDelta: (delta) => {
            const contentEl = botDiv.querySelector('.message-content');
            contentEl.textContent += delta;
            chatMessages.scrollTop = chatMessages.scrollHeight;
          }
        });
        chatMessages.removeChild(typingIndicator);
        return;
      }

      const response = await sendMessageToAI(message, modelSelect.value || API_CONFIG.default_model, params);

      chatMessages.removeChild(typingIndicator);
      addMessage(response, 'bot');
    } catch (error) {
      console.error('Error:', error);
      chatMessages.removeChild(typingIndicator);
      addMessage('Sorry, I encountered an error. Please configure your API key and try again.', 'bot');
    }
  };

  sendButton.addEventListener('click', sendMessage);
  userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  });

  newChatBtn.addEventListener('click', () => {
    chatMessages.innerHTML = '';
    chatHistory = [];
  });

  addMessage("Hello! I'm NVIDIA's AI assistant. How can I help you today?", 'bot');
});
