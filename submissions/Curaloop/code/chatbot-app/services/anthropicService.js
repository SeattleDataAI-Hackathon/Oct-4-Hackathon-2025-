import Anthropic from '@anthropic-ai/sdk';

// Initialize Anthropic client
// For web deployment, the API key should be set in environment variables
const getAnthropicClient = () => {
  const apiKey = process.env.ANTHROPIC_API_KEY || 'your-api-key-here';

  return new Anthropic({
    apiKey: apiKey,
    // For web/browser usage, we need to use dangerouslyAllowBrowser
    dangerouslyAllowBrowser: true,
  });
};

/**
 * Send a message to Claude and get a response
 * @param {Array} conversationHistory - Array of previous messages
 * @param {string} userMessage - The new user message
 * @returns {Promise<string>} - Claude's response
 */
export const sendMessageToClaude = async (conversationHistory, userMessage) => {
  try {
    const client = getAnthropicClient();

    // Format conversation history for Anthropic API
    const messages = [
      ...conversationHistory.map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: msg.text,
      })),
      {
        role: 'user',
        content: userMessage,
      },
    ];

    // Make API call to Claude
    const response = await client.messages.create({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 1024,
      system: 'You are a caring and empathetic AI companion for CuraLoop, designed to support individuals with Alzheimer\'s disease. Your role is to:\n\n1. Engage in warm, patient conversations\n2. Help with daily check-ins about mood, memory, and activities\n3. Provide gentle cognitive exercises and memory prompts\n4. Offer encouragement and emotional support\n5. Monitor for signs of confusion, distress, or behavioral changes\n\nAlways be kind, understanding, and use simple, clear language. If you notice concerning patterns, gently encourage the person to share with their caregiver or doctor.',
      messages: messages,
    });

    // Extract and return the response text
    const responseText = response.content[0].text;
    return responseText;

  } catch (error) {
    console.error('Anthropic API Error:', error);

    // Provide user-friendly error messages
    if (error.status === 401) {
      throw new Error('API authentication failed. Please check your API key.');
    } else if (error.status === 429) {
      throw new Error('Rate limit exceeded. Please wait a moment and try again.');
    } else if (error.status === 500) {
      throw new Error('Anthropic service is temporarily unavailable. Please try again later.');
    } else {
      throw new Error('Failed to get AI response. Please check your connection and try again.');
    }
  }
};

/**
 * Check if API key is configured
 * @returns {boolean}
 */
export const isApiKeyConfigured = () => {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  return apiKey && apiKey !== 'your-api-key-here';
};
