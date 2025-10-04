# AI Chatbot React Native App

A simple React Native chatbot interface built with Expo that can be deployed on iOS.

## Features

- Clean chat interface with message bubbles
- User and AI message differentiation
- Auto-scroll to latest messages
- Typing indicator
- iOS-optimized keyboard handling
- Ready for AI API integration

## Setup

1. Navigate to the project directory:
```bash
cd chatbot-app
```

2. Install dependencies (if needed):
```bash
npm install
```

## Running on iOS

### Method 1: Using Expo Go (Easiest for Preview)

1. Install Expo Go on your iPhone from the App Store

2. Start the development server:
```bash
npm start
```

3. Scan the QR code with your iPhone camera
4. The app will open in Expo Go

### Method 2: Using iOS Simulator (Requires Mac)

1. Install Xcode from the Mac App Store

2. Install iOS Simulator command line tools:
```bash
xcode-select --install
```

3. Run on iOS simulator:
```bash
npm run ios
```

### Method 3: Build for Physical Device (Advanced)

1. Install EAS CLI:
```bash
npm install -g eas-cli
```

2. Login to Expo:
```bash
eas login
```

3. Configure your project:
```bash
eas build:configure
```

4. Build for iOS:
```bash
eas build --platform ios --profile preview
```

## Connecting Your AI Service

The app currently has a placeholder AI response. To connect a real AI service:

1. Open `App.js`
2. Find the `sendMessage` function (around line 27)
3. Replace the `setTimeout` mock with your actual API call
4. Example code for common AI services is provided in comments

Example services you can integrate:
- OpenAI GPT API
- Anthropic Claude API
- Google Gemini API
- Custom AI endpoints

## Project Structure

```
chatbot-app/
├── App.js          # Main application component
├── package.json    # Dependencies
└── app.json        # Expo configuration
```

## Customization

### Styling
All styles are defined in the `StyleSheet` at the bottom of `App.js`. You can customize:
- Colors (header, message bubbles, buttons)
- Fonts and sizes
- Spacing and padding
- Border radius

### API Integration
Update the `sendMessage` function in `App.js` to connect your AI service endpoint.

## Troubleshooting

**App won't load on Expo Go:**
- Make sure your phone and computer are on the same WiFi network
- Try restarting the Metro bundler with `npm start --reset-cache`

**Keyboard covers input:**
- The app uses `KeyboardAvoidingView` which should handle this on iOS
- If issues persist, adjust `keyboardVerticalOffset` prop

**Build errors:**
- Clear cache: `npx expo start -c`
- Reinstall dependencies: `rm -rf node_modules && npm install`

## License

MIT
