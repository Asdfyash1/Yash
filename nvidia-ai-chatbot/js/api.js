// api.js - API Integration Module

const API_CONFIG = {
  invoke_url: "https://integrate.api.nvidia.com/v1/chat/completions",
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

async function resolveApiKey() {
  if (typeof window !== 'undefined' && window.NVIDIA_API_KEY) {
    return window.NVIDIA_API_KEY;
  }
  try {
    const mod = await import('./config.js');
    if (mod && mod.API_KEY) return mod.API_KEY;
  } catch (e) {
    // config.js not present; fall through
  }
  return null;
}

/**
 * Sends a message to the NVIDIA AI API and returns the response text.
 * @param {string} message - The user's message
 * @param {string} model - The AI model to use
 * @param {Object} params - Additional parameters for the API
 * @returns {Promise<string>} - The AI's response text
 */
async function sendMessageToAI(message, model = API_CONFIG.default_model, params = {}) {
  const apiKey = await resolveApiKey();
  if (!apiKey) {
    throw new Error('Missing NVIDIA API key. Create js/config.js exporting API_KEY or set window.NVIDIA_API_KEY.');
  }

  const headers = {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json',
    'Accept': params.stream ? 'text/event-stream' : 'application/json'
  };

  const payload = {
    model,
    messages: [
      { role: 'user', content: message }
    ],
    max_tokens: typeof params.max_tokens === 'number' ? params.max_tokens : API_CONFIG.default_params.max_tokens,
    temperature: typeof params.temperature === 'number' ? params.temperature : API_CONFIG.default_params.temperature,
    top_p: typeof params.top_p === 'number' ? params.top_p : API_CONFIG.default_params.top_p,
    frequency_penalty: typeof params.frequency_penalty === 'number' ? params.frequency_penalty : API_CONFIG.default_params.frequency_penalty,
    presence_penalty: typeof params.presence_penalty === 'number' ? params.presence_penalty : API_CONFIG.default_params.presence_penalty,
    stream: !!(typeof params.stream === 'boolean' ? params.stream : API_CONFIG.default_params.stream)
  };

  if (payload.stream) {
    throw new Error('Streaming not supported by sendMessageToAI. Use streamMessageFromAI instead.');
  }

  const response = await fetch(API_CONFIG.invoke_url, {
    method: 'POST',
    headers,
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    let errText;
    try { errText = await response.text(); } catch (_) {}
    throw new Error(`API error: ${response.status} ${response.statusText}${errText ? ` - ${errText}` : ''}`);
  }

  const data = await response.json();
  return data?.choices?.[0]?.message?.content ?? '';
}

/**
 * Streams a message response from the NVIDIA AI API via SSE.
 * Calls onDelta with incremental text tokens.
 * @param {string} message
 * @param {{ model?: string, params?: Object, onDelta?: (text: string) => void }} options
 */
async function streamMessageFromAI(message, { model = API_CONFIG.default_model, params = {}, onDelta } = {}) {
  const apiKey = await resolveApiKey();
  if (!apiKey) {
    throw new Error('Missing NVIDIA API key. Create js/config.js exporting API_KEY or set window.NVIDIA_API_KEY.');
  }

  const headers = {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json',
    'Accept': 'text/event-stream'
  };

  const payload = {
    model,
    messages: [{ role: 'user', content: message }],
    max_tokens: typeof params.max_tokens === 'number' ? params.max_tokens : API_CONFIG.default_params.max_tokens,
    temperature: typeof params.temperature === 'number' ? params.temperature : API_CONFIG.default_params.temperature,
    top_p: typeof params.top_p === 'number' ? params.top_p : API_CONFIG.default_params.top_p,
    frequency_penalty: typeof params.frequency_penalty === 'number' ? params.frequency_penalty : API_CONFIG.default_params.frequency_penalty,
    presence_penalty: typeof params.presence_penalty === 'number' ? params.presence_penalty : API_CONFIG.default_params.presence_penalty,
    stream: true
  };

  const response = await fetch(API_CONFIG.invoke_url, {
    method: 'POST',
    headers,
    body: JSON.stringify(payload)
  });

  if (!response.ok || !response.body) {
    let errText;
    try { errText = await response.text(); } catch (_) {}
    throw new Error(`API error: ${response.status} ${response.statusText}${errText ? ` - ${errText}` : ''}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let done = false;
  let buffered = '';

  while (!done) {
    const { value, done: readerDone } = await reader.read();
    done = readerDone;
    buffered += decoder.decode(value || new Uint8Array(), { stream: !done });

    const lines = buffered.split(/\r?\n/);
    buffered = lines.pop() || '';

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith(':')) continue;
      if (trimmed.startsWith('data: ')) {
        const dataStr = trimmed.slice(6).trim();
        if (dataStr === '[DONE]') {
          return;
        }
        try {
          const json = JSON.parse(dataStr);
          const delta = json?.choices?.[0]?.delta?.content ?? '';
          if (delta && typeof onDelta === 'function') onDelta(delta);
        } catch (_) {
          // ignore
        }
      }
    }
  }
}

export { sendMessageToAI, streamMessageFromAI, API_CONFIG };
