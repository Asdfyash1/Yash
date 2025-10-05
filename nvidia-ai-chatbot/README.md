# NVIDIA AI Chatbot Website

A modern, responsive AI chatbot interface that integrates with NVIDIA's AI API to provide intelligent conversational capabilities.

## 🚀 Features

- **Modern UI/UX**: Clean, responsive design with NVIDIA branding
- **Real-time Chat**: Interactive chat interface with typing indicators
- **Model Selection**: Choose from multiple AI models (Qwen3, Llama3, Claude 3)
- **Customizable Settings**: Adjust temperature, max tokens, and top-p parameters
- **Chat History**: Persistent chat history during session
- **Mobile Responsive**: Fully responsive design for all devices
- **Typing Animations**: Smooth animations for better user experience

## 📋 Project Structure

```
nvidia-ai-chatbot/
├── index.html          # Main HTML file
├── css/
│   └── styles.css      # Complete styling and responsive design
├── js/
│   ├── main.js         # Main application logic
│   └── api.js          # NVIDIA API integration
├── assets/
│   └── nvidia-logo.svg # NVIDIA brand logo
└── README.md           # Project documentation
```

## 🛠️ Installation & Setup

1. **Clone or download** the project files to your local machine
2. **Open** `index.html` in a modern web browser
3. **No build process required** - runs directly in the browser

## 🔧 Configuration

### API Setup

The application uses NVIDIA's AI API with the following configuration in `js/api.js`:

```javascript
const API_CONFIG = {
  invoke_url: "https://integrate.api.nvidia.com/v1/chat/completions",
  api_key: "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",
  default_model: "qwen/qwen3-next-80b-a3b-thinking",
  default_params: {
    max_tokens: 512,
    temperature: 1.0,
    top_p: 1.0,
    frequency_penalty: 0.0,
    presence_penalty: 0.0,
    stream: false
  }
};
```

### ⚠️ Security Note

The API key is currently hardcoded for demonstration purposes. For production use, consider:

- Using environment variables
- Implementing a backend proxy
- Setting up proper CORS headers

## 🎯 Usage

1. **Open the application** in your browser
2. **Start chatting** - Type your message and press Enter or click Send
3. **Customize settings** using the sidebar controls:
   - Select different AI models
   - Adjust temperature (creativity/randomness)
   - Set maximum response length
   - Modify top-p sampling
4. **Start new chats** using the "New Chat" button
5. **View chat history** in the sidebar (session-based)

## 🔧 API Integration

### Supported Models

- **Qwen3 Next 80B** (default) - High-performance general model
- **Llama3 70B Instruct** - Meta's instruction-tuned model
- **Claude 3 Opus** - Anthropic's advanced conversational model

### Parameters

- **Temperature** (0.0-2.0): Controls response randomness
- **Max Tokens** (64-4096): Maximum response length
- **Top P** (0.0-1.0): Nucleus sampling parameter

## 🎨 Customization

### Styling

The application uses modern CSS with:
- NVIDIA brand colors (`#76b900` green theme)
- Responsive design for mobile and desktop
- Smooth animations and transitions
- Dark mode support

### Adding New Features

To extend the application:

1. **Add new models** in the HTML select element and API configuration
2. **Implement chat history persistence** using localStorage
3. **Add streaming responses** by setting `stream: true` in API calls
4. **Implement multi-turn conversations** by passing chat history to the API

## 🌐 Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## 📱 Responsive Design

- **Desktop**: Full sidebar with all controls visible
- **Tablet**: Collapsible sidebar, optimized layout
- **Mobile**: Stacked layout, touch-friendly controls

## 🚨 Error Handling

The application includes comprehensive error handling for:
- Network connectivity issues
- API rate limiting
- Invalid responses
- User input validation

## 🔮 Future Enhancements

- **Chat persistence** across browser sessions
- **Export chat history** functionality  
- **Voice input/output** capabilities
- **File upload** support for context
- **Multiple language** support
- **Advanced settings** panel
- **Chat sharing** functionality

## 📄 License

This project is for educational and demonstration purposes. NVIDIA and related trademarks belong to NVIDIA Corporation.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

---

**Built with ❤️ using NVIDIA AI technology**