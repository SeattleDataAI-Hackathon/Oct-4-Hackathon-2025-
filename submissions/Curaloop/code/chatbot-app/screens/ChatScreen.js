import { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import { styles } from '../styles';
import { sendMessageToClaude, isApiKeyConfigured } from '../services/anthropicService';

export default function ChatScreen({ navigation }) {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const flatListRef = useRef(null);

  // Hide the default navigation header
  useEffect(() => {
    navigation.setOptions({
      headerShown: false,
    });
  }, [navigation]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messages.length > 0) {
      flatListRef.current?.scrollToEnd({ animated: true });
    }
  }, [messages]);

  const sendMessage = async () => {
    if (inputText.trim() === '') return;

    // Check if API key is configured
    if (!isApiKeyConfigured()) {
      Alert.alert(
        'API Key Required',
        'Please set your ANTHROPIC_API_KEY environment variable to use the chat feature.',
        [{ text: 'OK' }]
      );
      return;
    }

    const userMessageText = inputText.trim();
    const userMessage = {
      id: Date.now().toString(),
      text: userMessageText,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      // Call Anthropic API
      const responseText = await sendMessageToClaude(messages, userMessageText);

      const aiMessage = {
        id: (Date.now() + 1).toString(),
        text: responseText,
        sender: 'ai',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiMessage]);
      setIsLoading(false);
    } catch (error) {
      console.error('Error sending message:', error);
      setIsLoading(false);

      // Show error to user
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        text: `Sorry, I encountered an error: ${error.message}`,
        sender: 'ai',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  const renderMessage = ({ item }) => (
    <View
      style={
        item.sender === 'user'
          ? styles.figmaChatUserMessageContainer
          : styles.figmaChatAiMessageContainer
      }
    >
      <View
        style={
          item.sender === 'user'
            ? styles.figmaChatUserMessage
            : styles.figmaChatAiMessage
        }
      >
        <Text
          style={
            item.sender === 'user'
              ? styles.figmaChatUserMessageText
              : styles.figmaChatAiMessageText
          }
        >
          {item.text}
        </Text>
        <Text
          style={
            item.sender === 'user'
              ? styles.figmaChatUserTimestamp
              : styles.figmaChatAiTimestamp
          }
        >
          {item.timestamp.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </Text>
      </View>
    </View>
  );

  return (
    <View style={styles.figmaChatContainer}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
        keyboardVerticalOffset={0}
      >
        {/* Custom Header */}
        <View style={styles.figmaChatHeader}>
          <View style={styles.figmaChatHeaderContent}>
            <View style={styles.figmaChatAvatar}>
              <Text style={styles.figmaChatAvatarText}>👤</Text>
            </View>
            <View style={styles.figmaChatHeaderText}>
              <Text style={styles.figmaChatTitle}>Chat Companion</Text>
              <Text style={styles.figmaChatSubtitle}>Your AI care assistant</Text>
            </View>
          </View>
        </View>

        {/* Messages Area */}
        <View style={styles.figmaChatMessagesArea}>
          <FlatList
            ref={flatListRef}
            data={messages}
            renderItem={renderMessage}
            keyExtractor={(item) => item.id}
            contentContainerStyle={styles.figmaChatMessagesList}
            showsVerticalScrollIndicator={false}
            ListEmptyComponent={
              <View style={styles.figmaChatEmptyContainer}>
                <Text style={styles.figmaChatEmptyText}>Start chatting with AI!</Text>
              </View>
            }
          />

          {isLoading && (
            <View style={styles.figmaChatLoadingContainer}>
              <Text style={styles.figmaChatLoadingText}>AI is typing...</Text>
            </View>
          )}
        </View>

        {/* Input Area */}
        <View style={styles.figmaChatInputContainer}>
          <View style={styles.figmaChatInputRow}>
            <TextInput
              style={styles.figmaChatInput}
              value={inputText}
              onChangeText={setInputText}
              placeholder="Type your message..."
              placeholderTextColor="#6b7280"
              maxLength={1000}
              onSubmitEditing={sendMessage}
              returnKeyType="send"
            />
            <TouchableOpacity
              style={[
                styles.figmaChatSendButton,
                (!inputText.trim() || isLoading) && styles.figmaChatSendButtonDisabled,
              ]}
              onPress={sendMessage}
              disabled={!inputText.trim() || isLoading}
            >
              <Text style={styles.figmaChatSendIcon}>✈️</Text>
            </TouchableOpacity>
          </View>
        </View>
      </KeyboardAvoidingView>
    </View>
  );
}
