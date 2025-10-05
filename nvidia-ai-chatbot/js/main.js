// main.js - Main Application Logic

import { sendMessageToAI, API_CONFIG } from './api.js';

document.addEventListener('DOMContentLoaded', function () {
  // DOM Elements
  const chatMessages = document.getElementById('chat-messages');
  const userInput = document.getElementById('user-input');
  const sendButton = document.querySelector('.send-btn');
  const modelSelect = document.getElementById('model-select');
  const temperatureSlider = document.getElementById('temperature');
  const maxTokensSlider = document.getElementById('max-tokens');
  const topPSlider = document.getElementById('top-p');
  const newChatBtn = document.querySelector('.new-chat-btn');

  // Chat history
  let chatHistory = [];

  // Update setting values display
  const updateSettingValue = (slider) => {
    const valueDisplay = slider.parentElement.querySelector('.setting-value');
    valueDisplay.textContent = slider.value;
  };

  // Initialize sliders
  temperatureSlider.addEventListener('input', () => updateSettingValue(temperatureSlider));
  maxTokensSlider.addEventListener('input', () => updateSettingValue(maxTokensSlider));
  topPSlider.addEventListener('input', () => updateSettingValue(topPSlider));

  // Add message to chat
  const addMessage = (content, sender) => {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    messageDiv.innerHTML = `<div class="message-content">${content}</div>`;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Add to chat history
    chatHistory.push({ role: sender === 'user' ? 'user' : 'assistant', content });
  };

  // Show typing indicator
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

  // Send message function
  const sendMessage = async () => {
    const message = userInput.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessage(message, 'user');
    userInput.value = '';

    // Show typing indicator
    const typingIndicator = showTypingIndicator();

    try {
      // Get current settings
      const params = {
        temperature: parseFloat(temperatureSlider.value),
        max_tokens: parseInt(maxTokensSlider.value),
        top_p: parseFloat(topPSlider.value)
      };

      // Call API
      const response = await sendMessageToAI(message, modelSelect.value, params);

      // Remove typing indicator
      chatMessages.removeChild(typingIndicator);

      // Add bot response
      addMessage(response, 'bot');
    } catch (error) {
      console.error('Error:', error);
      chatMessages.removeChild(typingIndicator);
      addMessage('Sorry, I encountered an error. Please try again.', 'bot');
    }
  };

  // Event listeners
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

  // Initialize with welcome message
  addMessage("Hello! I'm NVIDIA's AI assistant. How can I help you today?", 'bot');
});
