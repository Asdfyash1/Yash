// api.js - API Integration Module

const API_CONFIG = {
  invoke_url: "https://integrate.api.nvidia.com/v1/chat/completions",
  // WARNING: Do NOT hardcode API keys in production. Use a backend proxy.
  api_key: "",
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

/**
 * Sends a message to the NVIDIA AI API and returns the response
 * @param {string} message - The user's message
 * @param {string} model - The AI model to use
 * @param {Object} params - Additional parameters for the API
 * @param {string} apiKey - Optional API key to use instead of the configured one
 * @returns {Promise<string>} - The AI's response
 */
async function sendMessageToAI(message, model = API_CONFIG.default_model, params = {}, apiKey = null) {
  const keyToUse = apiKey || API_CONFIG.api_key;

  if (!keyToUse) {
    throw new Error("API Key is missing. Please enter your NVIDIA API Key in the settings.");
  }

  const headers = {
    "Authorization": `Bearer ${keyToUse}`,
    "Content-Type": "application/json",
    "Accept": params.stream ? "text/event-stream" : "application/json"
  };

  const payload = {
    model: model,
    messages: [
      { role: "user", content: message }
    ],
    max_tokens: params.max_tokens ?? API_CONFIG.default_params.max_tokens,
    temperature: params.temperature ?? API_CONFIG.default_params.temperature,
    top_p: params.top_p ?? API_CONFIG.default_params.top_p,
    frequency_penalty: params.frequency_penalty ?? API_CONFIG.default_params.frequency_penalty,
    presence_penalty: params.presence_penalty ?? API_CONFIG.default_params.presence_penalty,
    stream: params.stream ?? API_CONFIG.default_params.stream
  };

  try {
    const response = await fetch(API_CONFIG.invoke_url, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`API error: ${response.status} ${response.statusText} - ${text}`);
    }

    // Streaming not implemented in this basic function
    const data = await response.json();
    const content = data?.choices?.[0]?.message?.content ?? "";
    return content;
  } catch (error) {
    console.error("Error calling NVIDIA AI API:", error);
    throw error;
  }
}

export { sendMessageToAI, API_CONFIG };
