# NVIDIA AI Assistant (Frontend)

A minimal NVIDIA AI chatbot website built with vanilla HTML/CSS/JS.

## Features
- Simple chat UI with NVIDIA-styled theme
- Model selection and parameters (temperature, max tokens, top-p)
- Optional streaming responses over SSE
- Pluggable API key via `js/config.js` or `window.NVIDIA_API_KEY`

## Quick Start

1. Copy example config and set your key:

```bash
cp js/config.example.js js/config.js
# edit js/config.js and set API_KEY
```

2. Serve the folder with any static server (CORS-friendly):

```bash
# Option A: Python
python3 -m http.server -d . 5173
# then open http://localhost:5173/nvidia-ai-chatbot/

# Option B: Node (if installed)
npx serve -l 5173 .
```

3. Open `index.html` in your browser via the server URL.

## API Key Options
- Create `js/config.js` exporting `API_KEY`:

```js
export const API_KEY = "nvapi-...";
```

- Or set it at runtime in the console or a wrapper script:

```html
<script>
  window.NVIDIA_API_KEY = "nvapi-...";
</script>
```

## Streaming
- Toggle the Streaming switch in the sidebar to stream tokens.
- Uses `Accept: text/event-stream` and parses SSE `data:` lines, appending `delta` content.

## Security Notes
- Do not ship real secrets in frontend code. For production:
  - Use a backend proxy that injects the key server-side
  - Enforce origin/route-level auth and rate limits
  - Consider request signing or token exchange flow

## Multi-turn Conversations
- Current demo sends only the latest user message. For better context, pass `chatHistory` to the API (append `messages` with `user`/`assistant` turns) or manage this server-side.

## Folder Structure
```
nvidia-ai-chatbot/
├── index.html
├── css/
│   └── styles.css
├── js/
│   ├── api.js
│   ├── config.example.js
│   └── main.js
├── assets/
│   └── nvidia-logo.svg
└── README.md
```

## License
MIT
