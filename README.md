# NVIDIA AI Chatbot Website

A modern, responsive web application that provides an intuitive interface for interacting with NVIDIA's AI models through their API. Built with vanilla JavaScript, HTML5, and CSS3.

## Features

- **Multiple AI Models**: Support for various NVIDIA AI models including Qwen3 Next 80B, Llama3 70B Instruct, and Claude 3 Opus
- **Real-time Chat Interface**: Clean, modern chat interface with typing indicators and smooth animations
- **Customizable Parameters**: Adjust temperature, max tokens, and top-p values for fine-tuned responses
- **Responsive Design**: Fully responsive layout that works on desktop, tablet, and mobile devices
- **NVIDIA Branding**: Professional styling with NVIDIA's signature green color scheme
- **Chat History**: Persistent chat sessions with new chat functionality
- **Error Handling**: Robust error handling with user-friendly error messages

## Project Structure

```
nvidia-ai-chatbot/
├── index.html          # Main HTML file with chat interface
├── css/
│   └── styles.css      # Comprehensive styling with NVIDIA branding
├── js/
│   ├── main.js         # Main application logic and UI interactions
│   └── api.js          # NVIDIA AI API integration module
├── assets/
│   └── nvidia-logo.svg # NVIDIA logo for branding
└── README.md           # Project documentation
```

## Getting Started

### Prerequisites

- A modern web browser with JavaScript enabled
- Internet connection for API calls
- NVIDIA AI API access (API key included in the project)

### Installation

1. Clone or download this repository
2. Open `index.html` in your web browser
3. Start chatting with the AI!

### Local Development

For local development with a web server:

```bash
# Using Python 3
python -m http.server 8000

# Using Node.js (if you have http-server installed)
npx http-server

# Using PHP
php -S localhost:8000
```

Then navigate to `http://localhost:8000` in your browser.

## Usage

### Basic Chat

1. Type your message in the input field at the bottom
2. Press Enter or click the send button
3. Wait for the AI response to appear

### Customizing AI Parameters

Use the sidebar controls to adjust:

- **Model Selection**: Choose from available NVIDIA AI models
- **Temperature** (0-2): Controls randomness in responses
  - Lower values (0.1-0.7): More focused and deterministic
  - Higher values (0.8-2.0): More creative and varied
- **Max Tokens** (64-4096): Maximum length of AI responses
- **Top P** (0-1): Controls diversity of word selection
  - Lower values: More focused responses
  - Higher values: More diverse vocabulary

### Starting a New Chat

Click the "New Chat" button in the sidebar to clear the current conversation and start fresh.

## API Integration

The application integrates with the NVIDIA AI API using the following configuration:

- **Endpoint**: `https://integrate.api.nvidia.com/v1/chat/completions`
- **Authentication**: Bearer token authentication
- **Default Model**: `qwen/qwen3-next-80b-a3b-thinking`
- **Supported Models**:
  - Qwen3 Next 80B (Thinking)
  - Meta Llama3 70B Instruct
  - Anthropic Claude 3 Opus

### API Security Note

The API key is currently hardcoded in the `js/api.js` file for demonstration purposes. For production deployment, consider:

- Using environment variables
- Implementing a backend proxy server
- Setting up proper CORS headers
- Implementing rate limiting

## Technical Details

### Architecture

- **Frontend**: Vanilla JavaScript with ES6 modules
- **Styling**: CSS3 with custom properties and modern features
- **API**: RESTful integration with NVIDIA AI services
- **Build**: No build process required - runs directly in browser

### Browser Compatibility

- Chrome/Chromium 60+
- Firefox 60+
- Safari 12+
- Edge 79+

### Performance Features

- Efficient DOM manipulation
- Smooth animations with CSS transitions
- Responsive images and layouts
- Optimized API calls with error handling

## Customization

### Styling

The CSS uses CSS custom properties (variables) for easy theming:

```css
:root {
  --nvidia-green: #76b900;
  --nvidia-dark: #1a1a1a;
  --nvidia-gray: #2d2d2d;
  /* ... more variables */
}
```

### Adding New Models

To add new AI models, update the model selector in `index.html`:

```html
<select id="model-select">
  <option value="new-model-id">New Model Name</option>
</select>
```

### Extending Functionality

The modular structure makes it easy to add new features:

- **Chat History Persistence**: Implement localStorage or backend storage
- **Streaming Responses**: Enable real-time response streaming
- **File Uploads**: Add support for document/image uploads
- **Multi-turn Conversations**: Implement conversation context

## Troubleshooting

### Common Issues

1. **API Errors**: Check console for detailed error messages
2. **CORS Issues**: Use a local web server instead of opening HTML directly
3. **Slow Responses**: Try reducing max_tokens or changing models
4. **Mobile Issues**: Ensure viewport meta tag is present

### Error Messages

- "API error: 401": Invalid or expired API key
- "API error: 429": Rate limit exceeded
- "Network error": Check internet connection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is provided as-is for demonstration purposes. Please ensure compliance with NVIDIA's API terms of service.

## Acknowledgments

- NVIDIA for providing the AI API
- Modern web standards for enabling this functionality
- The open-source community for inspiration and best practices
