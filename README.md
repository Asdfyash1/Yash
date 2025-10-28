# NVIDIA AI Chatbot Website

A modern, responsive AI chatbot interface powered by NVIDIA's AI API. This web application provides an intuitive chat interface with customizable AI model parameters and a sleek NVIDIA-themed design.

## Features

- 🤖 **AI-Powered Chat**: Interact with NVIDIA's advanced AI models
- 🎨 **Modern UI**: Sleek, dark-themed interface with NVIDIA branding
- ⚙️ **Customizable Parameters**: Adjust temperature, max tokens, and top-p settings
- 🔄 **Multiple Models**: Switch between different AI models
- 📱 **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- 💬 **Real-time Chat**: Instant responses with typing indicators
- 🎯 **Clean Architecture**: Modular JavaScript code with separate API and UI logic

## Project Structure

```
nvidia-ai-chatbot/
├── index.html          # Main HTML structure
├── css/
│   └── styles.css      # All styling and responsive design
├── js/
│   ├── main.js         # Main application logic
│   └── api.js          # NVIDIA API integration
├── assets/
│   └── nvidia-logo.svg # NVIDIA logo
└── README.md          # Project documentation
```

## Technologies Used

- **HTML5**: Semantic markup structure
- **CSS3**: Modern styling with CSS Grid, Flexbox, and animations
- **Vanilla JavaScript**: No framework dependencies, pure ES6+ modules
- **NVIDIA AI API**: Backend AI processing

## Setup Instructions

### Prerequisites

- A modern web browser (Chrome, Firefox, Safari, or Edge)
- A local web server (required for ES6 modules)

### Installation

1. **Clone or download this repository**

2. **Start a local web server**

   Choose one of the following methods:

   **Using Python (Python 3):**
   ```bash
   python -m http.server 8000
   ```

   **Using Python (Python 2):**
   ```bash
   python -m SimpleHTTPServer 8000
   ```

   **Using Node.js (with http-server):**
   ```bash
   npx http-server -p 8000
   ```

   **Using PHP:**
   ```bash
   php -S localhost:8000
   ```

3. **Open your browser**

   Navigate to: `http://localhost:8000`

## Usage

### Starting a Conversation

1. Type your message in the input field at the bottom of the chat interface
2. Press Enter or click the send button
3. Wait for the AI to respond (you'll see a typing indicator)
4. Continue the conversation naturally

### Customizing Settings

**Model Selection:**
- Use the dropdown in the sidebar to select different AI models
- Available models include Qwen3 Next 80B, Llama3 70B Instruct, and Claude 3 Opus

**Temperature (0.0 - 2.0):**
- Lower values (0.0-0.5): More focused and deterministic responses
- Medium values (0.5-1.0): Balanced creativity and coherence
- Higher values (1.0-2.0): More creative and varied responses

**Max Tokens (64 - 4096):**
- Controls the maximum length of the AI's response
- Higher values allow for longer, more detailed responses

**Top P (0.0 - 1.0):**
- Controls diversity via nucleus sampling
- Lower values make responses more focused
- Higher values increase response diversity

### Starting a New Chat

Click the "New Chat" button in the sidebar to clear the conversation and start fresh.

## API Configuration

The application is pre-configured with NVIDIA's AI API. The configuration is located in `js/api.js`:

```javascript
const API_CONFIG = {
  invoke_url: "https://integrate.api.nvidia.com/v1/chat/completions",
  api_key: "nvapi-...", // API key included
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

## Security Considerations

⚠️ **Important**: The API key is currently hardcoded in the JavaScript file for demonstration purposes.

For production deployment, consider:

1. **Backend Proxy**: Implement a backend server to handle API calls
2. **Environment Variables**: Store sensitive credentials securely
3. **Rate Limiting**: Implement request throttling
4. **CORS Configuration**: Properly configure CORS headers
5. **API Key Rotation**: Regularly rotate API keys

## Features in Detail

### Responsive Design
- **Desktop**: Full sidebar with settings visible
- **Tablet**: Adapted layout for medium screens
- **Mobile**: Stacked layout with optimized touch controls

### Real-time Feedback
- Typing indicators show when the AI is processing
- Smooth animations for messages appearing
- Scroll automatically follows new messages

### Error Handling
- Network error detection
- User-friendly error messages
- Graceful degradation when API is unavailable

## Future Enhancements

Potential improvements for future versions:

1. **Streaming Responses**: Display AI responses as they're generated
2. **Chat History Persistence**: Save conversations to localStorage or database
3. **Multi-turn Context**: Pass conversation history to the API for better context
4. **Export Conversations**: Download chat history as text or PDF
5. **Theme Customization**: Light/dark mode toggle
6. **Voice Input**: Speech-to-text functionality
7. **Code Syntax Highlighting**: Better display of code in responses
8. **Markdown Support**: Render formatted text in messages

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

This project is provided as-is for demonstration purposes.

## Acknowledgments

- Built with NVIDIA AI API
- Design inspired by modern chat interfaces
- Icons from inline SVG

## Support

For issues or questions:
1. Check the browser console for error messages
2. Verify your internet connection
3. Ensure the API key is valid
4. Try refreshing the page

---

Built with ❤️ using NVIDIA AI technology