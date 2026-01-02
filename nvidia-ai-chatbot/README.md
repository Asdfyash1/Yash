# NVIDIA AI Chatbot Website

A simple web UI that calls the NVIDIA Chat Completions API to provide an AI assistant experience.

## Project Structure

```
nvidia-ai-chatbot/
├── index.html
├── css/
│   └── styles.css
├── js/
│   ├── main.js
│   └── api.js
├── assets/
│   └── nvidia-logo.svg
└── README.md
```

## Running Locally

Open with any static server from the `nvidia-ai-chatbot` folder:

```bash
# Python 3
python -m http.server 5173 --directory nvidia-ai-chatbot
# or using Node
npx serve nvidia-ai-chatbot -l 5173
```

Then open `http://localhost:5173`.

## Configure API Key

Edit `js/api.js` and set your NVIDIA API key:

```js
const API_CONFIG = {
  api_key: "nvapi-REPLACE-WITH-YOUR-KEY",
  // ...
}
```

Important: Do not ship API keys in client code to production. Use a backend proxy.

## Notes

- The basic client sends only the latest user message. For multi-turn context, extend `sendMessageToAI` to include `chatHistory` messages.
- Streaming responses are not implemented yet. You can enable streaming by setting `stream: true` and using `response.body` with `TextDecoder` to progressively update the UI.
- Error handling includes status text; improve with retries and rate-limit detection for production.
