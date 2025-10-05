// main.js - Main Application Logic

import { sendMessageToAI, sendMessageWithHistory, getAvailableModels, API_CONFIG } from './api.js';

document.addEventListener('DOMContentLoaded', function() {
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
  let isProcessing = false;
  
  // Initialize the application
  initializeApp();
  
  async function initializeApp() {
    // Load available models
    await loadAvailableModels();
    
    // Initialize sliders
    initializeSliders();
    
    // Set up event listeners
    setupEventListeners();
    
    // Load chat history from localStorage
    loadChatHistory();
    
    // Add welcome message
    addMessage("Hello! I'm NVIDIA's AI assistant. How can I help you today?", 'bot');
  }
  
  async function loadAvailableModels() {
    try {
      const models = await getAvailableModels();
      if (models.length > 0) {
        // Clear existing options except the first one
        modelSelect.innerHTML = '';
        
        // Add default models
        const defaultModels = [
          { id: 'qwen/qwen3-next-80b-a3b-thinking', name: 'Qwen3 Next 80B' },
          { id: 'meta/llama3-70b-instruct', name: 'Llama3 70B Instruct' },
          { id: 'anthropic/claude-3-opus', name: 'Claude 3 Opus' }
        ];
        
        defaultModels.forEach(model => {
          const option = document.createElement('option');
          option.value = model.id;
          option.textContent = model.name;
          if (model.id === API_CONFIG.default_model) {
            option.selected = true;
          }
          modelSelect.appendChild(option);
        });
      }
    } catch (error) {
      console.error('Error loading models:', error);
    }
  }
  
  function initializeSliders() {
    // Update setting values display
    const updateSettingValue = (slider) => {
      const valueDisplay = slider.parentElement.querySelector('.setting-value');
      if (valueDisplay) {
        valueDisplay.textContent = slider.value;
      }
    };
    
    // Initialize sliders
    temperatureSlider.addEventListener('input', () => updateSettingValue(temperatureSlider));
    maxTokensSlider.addEventListener('input', () => updateSettingValue(maxTokensSlider));
    topPSlider.addEventListener('input', () => updateSettingValue(topPSlider));
    
    // Set initial values
    updateSettingValue(temperatureSlider);
    updateSettingValue(maxTokensSlider);
    updateSettingValue(topPSlider);
  }
  
  function setupEventListeners() {
    // Send message events
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
    
    // New chat button
    newChatBtn.addEventListener('click', startNewChat);
    
    // Prevent form submission
    userInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && e.shiftKey) {
        // Allow shift+enter for new lines
        return;
      }
    });
  }
  
  function loadChatHistory() {
    try {
      const savedHistory = localStorage.getItem('nvidia-ai-chat-history');
      if (savedHistory) {
        chatHistory = JSON.parse(savedHistory);
        // Optionally display previous messages
        // For now, we'll just load the history for context
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
      chatHistory = [];
    }
  }
  
  function saveChatHistory() {
    try {
      localStorage.setItem('nvidia-ai-chat-history', JSON.stringify(chatHistory));
    } catch (error) {
      console.error('Error saving chat history:', error);
    }
  }
  
  function startNewChat() {
    chatMessages.innerHTML = '';
    chatHistory = [];
    saveChatHistory();
    addMessage("Hello! I'm NVIDIA's AI assistant. How can I help you today?", 'bot');
  }
  
  // Add message to chat
  function addMessage(content, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    // Format message content (basic markdown support)
    const formattedContent = formatMessage(content);
    
    messageDiv.innerHTML = `<div class="message-content">${formattedContent}</div>`;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Add to chat history
    chatHistory.push({ role: sender === 'user' ? 'user' : 'assistant', content });
    
    // Save to localStorage
    saveChatHistory();
  }
  
  function formatMessage(content) {
    // Basic markdown formatting
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>')
      .replace(/\n/g, '<br>');
  }
  
  // Show typing indicator
  function showTypingIndicator() {
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
  }
  
  // Send message function
  async function sendMessage() {
    if (isProcessing) return;
    
    const message = userInput.value.trim();
    if (!message) return;
    
    isProcessing = true;
    sendButton.disabled = true;
    userInput.disabled = true;
    
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
      
      // Call API with conversation history
      const response = await sendMessageWithHistory(chatHistory, modelSelect.value, params);
      
      // Remove typing indicator
      chatMessages.removeChild(typingIndicator);
      
      // Add bot response
      addMessage(response, 'bot');
      
    } catch (error) {
      console.error('Error:', error);
      
      // Remove typing indicator
      if (chatMessages.contains(typingIndicator)) {
        chatMessages.removeChild(typingIndicator);
      }
      
      // Show error message
      let errorMessage = 'Sorry, I encountered an error. Please try again.';
      
      if (error.message.includes('API error: 401')) {
        errorMessage = 'Authentication error. Please check the API key.';
      } else if (error.message.includes('API error: 429')) {
        errorMessage = 'Rate limit exceeded. Please wait a moment and try again.';
      } else if (error.message.includes('API error: 500')) {
        errorMessage = 'Server error. Please try again later.';
      } else if (error.message.includes('NetworkError') || error.message.includes('Failed to fetch')) {
        errorMessage = 'Network error. Please check your connection and try again.';
      }
      
      addMessage(errorMessage, 'bot');
    } finally {
      isProcessing = false;
      sendButton.disabled = false;
      userInput.disabled = false;
      userInput.focus();
    }
  }
  
  // Auto-resize textarea (if we switch to textarea)
  function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
  }
  
  // Handle window resize
  window.addEventListener('resize', () => {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  });
  
  // Handle visibility change (when user switches tabs)
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  });
});