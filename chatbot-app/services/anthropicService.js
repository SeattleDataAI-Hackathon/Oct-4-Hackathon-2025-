import Anthropic from '@anthropic-ai/sdk';

// Mock responses for demo mode
const mockResponses = [
  "Hello! I'm here to support you today. How are you feeling?",
  "Thank you for sharing that with me. It's wonderful that you're taking care of yourself. How has your day been so far?",
  "That's great to hear! Remember, it's important to take things one step at a time. Is there anything specific you'd like to talk about?",
  "I understand. It can be challenging sometimes. Would you like to do a gentle memory exercise together? It might help you feel more focused.",
  "You're doing wonderfully! Keep up the great work with your daily activities. Have you had a chance to take your medication today?",
  "I'm here to listen and support you. If you ever feel confused or need help, don't hesitate to reach out to your caregiver. What would make you feel better right now?",
  "That sounds lovely! Staying active and engaged is so important. Tell me more about what you've been up to.",
  "I appreciate you sharing your thoughts with me. Remember, every day is a new opportunity. How about we work on something fun together?",
];

let mockResponseIndex = 0;

/**
 * Generate a mock AI response for demo purposes
 * @param {string} userMessage - The user's message
 * @returns {string} - Mock response
 */
const getMockResponse = (userMessage) => {
  const message = userMessage.toLowerCase();

  // Context-aware responses
  if (message.includes('hello') || message.includes('hi')) {
    return "Hello! I'm your CuraLoop AI companion. I'm here to support you and chat whenever you need. How are you feeling today?";
  }
  if (message.includes('help') || message.includes('confused')) {
    return "I'm here to help you. Take a deep breath - everything is okay. Would you like to talk about what's on your mind? Remember, you can always reach out to your caregiver if you need additional support.";
  }
  if (message.includes('memory') || message.includes('remember') || message.includes('forgot')) {
    return "It's completely normal to have moments where memory feels challenging. Let's take this step by step together. Can you tell me what you're trying to remember? We can work through it together.";
  }
  if (message.includes('medicine') || message.includes('medication')) {
    return "Thank you for mentioning your medication! It's wonderful that you're staying on top of your health. Have you taken your medicine today? If you're unsure, it might be good to check with your caregiver.";
  }

  // Rotate through general responses
  const response = mockResponses[mockResponseIndex];
  mockResponseIndex = (mockResponseIndex + 1) % mockResponses.length;
  return response;
};

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
 * @returns {Promise<{text: string, isMock: boolean}>} - Response object with text and mock flag
 */
export const sendMessageToClaude = async (conversationHistory, userMessage) => {
  // First, try the real API if configured
  const apiKey = process.env.ANTHROPIC_API_KEY;
  const hasValidKey = apiKey && apiKey !== 'your-api-key-here' && apiKey.startsWith('sk-');

  if (hasValidKey) {
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
      return { text: responseText, isMock: false };

    } catch (error) {
      console.warn('Anthropic API failed, falling back to mock:', error);
      // Fall through to mock response
    }
  }

  // Fallback to mock response
  const mockText = getMockResponse(userMessage);
  return { text: mockText, isMock: true };
};

/**
 * Check if API key is configured
 * @returns {boolean}
 */
export const isApiKeyConfigured = () => {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  return apiKey && apiKey !== 'your-api-key-here';
};
