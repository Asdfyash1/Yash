# NVIDIA AI Chatbot Website

A modern, responsive web application that integrates with NVIDIA's AI API to provide an interactive chatbot experience. Built with vanilla JavaScript, HTML5, and CSS3.

## Features

- 🤖 **Multiple AI Models**: Support for Qwen3, Llama3, and Claude models
- 💬 **Real-time Chat**: Interactive conversation interface with typing indicators
- ⚙️ **Customizable Settings**: Adjust temperature, max tokens, and top-p parameters
- 📱 **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- 🎨 **NVIDIA Branding**: Modern UI with NVIDIA's signature green gradient
- 💾 **Chat History**: Persistent chat history using localStorage
- 🔄 **New Chat**: Start fresh conversations anytime

## Project Structure

```
nvidia-ai-chatbot/
├── index.html              # Main HTML file
├── css/
│   └── styles.css          # All styling and responsive design
├── js/
│   ├── main.js            # Main application logic
│   └── api.js             # NVIDIA AI API integration
├── assets/
│   └── nvidia-logo.svg    # NVIDIA logo
└── README.md              # This file
```

## Getting Started

### Prerequisites

- A modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection for API calls
- NVIDIA AI API key (included in the code)

### Installation

1. **Clone or download** this repository to your local machine
2. **Open** the `index.html` file in your web browser
3. **Start chatting** with the AI assistant!

### Local Development

For local development, you can use a simple HTTP server:

```bash
# Using Python 3
python -m http.server 8000

# Using Node.js (if you have http-server installed)
npx http-server

# Using PHP
php -S localhost:8000
```

Then open `http://localhost:8000` in your browser.

## API Configuration

The application is pre-configured with a working NVIDIA AI API key and endpoint:

```javascript
const API_CONFIG = {
  invoke_url: "https://integrate.api.nvidia.com/v1/chat/completions",
  api_key: "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",
  default_model: "qwen/qwen3-next-80b-a3b-thinking"
};
```

### Available Models

- **Qwen3 Next 80B**: Default model with advanced reasoning capabilities
- **Llama3 70B Instruct**: Meta's instruction-tuned model
- **Claude 3 Opus**: Anthropic's most capable model

### API Parameters

- **Temperature** (0-2): Controls randomness in responses
- **Max Tokens** (64-4096): Maximum length of AI responses
- **Top P** (0-1): Controls diversity of token selection

## Usage

### Basic Chat

1. Type your message in the input field
2. Press Enter or click the send button
3. Wait for the AI response
4. Continue the conversation

### Advanced Settings

1. **Change Model**: Select different AI models from the dropdown
2. **Adjust Parameters**: Use sliders to fine-tune AI behavior
3. **Start New Chat**: Click "New Chat" to begin fresh conversation

### Keyboard Shortcuts

- **Enter**: Send message
- **Shift + Enter**: New line (if using textarea)

## Customization

### Styling

Edit `css/styles.css` to customize:
- Colors and gradients
- Typography
- Layout and spacing
- Animations and transitions

### Functionality

Modify `js/main.js` to add:
- New features
- Different message formatting
- Additional UI interactions

### API Integration

Update `js/api.js` to:
- Change API endpoints
- Add new models
- Implement streaming responses
- Add error handling

## Browser Support

- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13+
- ✅ Edge 80+

## Security Considerations

⚠️ **Important**: The API key is currently hardcoded in the client-side code. For production use:

1. **Use Environment Variables**: Store API keys securely
2. **Implement Backend Proxy**: Create a server-side API handler
3. **Add Authentication**: Implement user authentication
4. **Rate Limiting**: Add client-side rate limiting
5. **CORS Configuration**: Properly configure CORS headers

## Troubleshooting

### Common Issues

**API Errors**
- Check internet connection
- Verify API key is valid
- Check browser console for detailed error messages

**UI Issues**
- Clear browser cache
- Check browser compatibility
- Disable browser extensions

**Performance**
- Close other tabs to free memory
- Check network speed
- Reduce max tokens if responses are slow

### Error Messages

- **Authentication Error**: API key is invalid or expired
- **Rate Limit Exceeded**: Too many requests, wait and try again
- **Network Error**: Check internet connection
- **Server Error**: API service is temporarily unavailable

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and demonstration purposes. Please respect NVIDIA's API terms of service.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review browser console for errors
3. Verify API key and network connection
4. Create an issue in the repository

## Future Enhancements

- [ ] Streaming responses
- [ ] File upload support
- [ ] Voice input/output
- [ ] Chat export functionality
- [ ] User authentication
- [ ] Multiple conversation threads
- [ ] Custom model training
- [ ] Plugin system

---

Built with ❤️ using NVIDIA AI technology