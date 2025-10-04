import { View, Text, TouchableOpacity, ScrollView } from 'react-native';
import { styles } from '../styles';

export default function HomeScreen({ navigation }) {
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const miniGames = [
    {
      id: '1',
      title: 'Zip',
      description: 'A light, playful way to wake up your brain — just tap, react, and smile.',
      gradient: ['#d946ef', '#e879f9'],
    },
    {
      id: '2',
      title: 'Sudoku',
      description: 'Turn simple logic play into daily brain care — fun, calming, and good for your memory.',
      gradient: ['#0ea5e9', '#67e8f9'],
    },
  ];

  return (
    <ScrollView style={styles.figmaHomeContainer}>
      {/* Top Greeting Section */}
      <View style={styles.figmaGreetingSection}>
        <Text style={styles.figmaGreetingText}>{getGreeting()}, Ms. Li 🌞</Text>
        <Text style={styles.figmaSubtitle}>Let's start your daily check-in</Text>
      </View>

      {/* Dashboard and Doctor Buttons */}
      <View style={styles.figmaButtonRow}>
        <TouchableOpacity
          style={styles.figmaButton}
          onPress={() => navigation.navigate('Dashboard')}
        >
          <View style={styles.figmaButtonIcon}>
            <Text style={styles.figmaButtonIconText}>🏠</Text>
          </View>
          <Text style={styles.figmaButtonText}>Dashboard</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.figmaButton}>
          <Text style={styles.figmaButtonText}>Doctor</Text>
        </TouchableOpacity>
      </View>

      {/* Chat Conversation Preview */}
      <TouchableOpacity
        style={styles.figmaChatPreviewContainer}
        onPress={() => navigation.navigate('Chat')}
        activeOpacity={0.8}
      >
        <View style={styles.figmaChatPreview}>
          <View style={styles.figmaChatMessageRow}>
            <View style={styles.figmaAvatarLeft}>
              <Text style={styles.figmaAvatarText}>👤</Text>
            </View>
            <View style={styles.figmaChatBubbleLeft}>
              <Text style={styles.figmaChatBubbleText}>How are you feeling today?</Text>
            </View>
          </View>

          <View style={styles.figmaChatMessageRowRight}>
            <View style={styles.figmaChatBubbleRight}>
              <Text style={styles.figmaChatBubbleTextRight}>I just took my morning medicine</Text>
            </View>
            <View style={styles.figmaAvatarRight}>
              <Text style={styles.figmaAvatarText}>👤</Text>
            </View>
          </View>

          <View style={styles.figmaChatMessageRowRight}>
            <View style={styles.figmaChatBubbleRight}>
              <Text style={styles.figmaChatBubbleTextRight}>I forgot where I put my keys....</Text>
            </View>
          </View>
        </View>

        <View style={styles.figmaChatPreviewTap}>
          <Text style={styles.figmaChatPreviewTapText}>Tap to open chat</Text>
        </View>
      </TouchableOpacity>

      {/* Games Section */}
      <View style={styles.figmaGamesContainer}>
        <View style={styles.figmaGamesHeader}>
          <View style={styles.figmaGamesIconContainer}>
            <Text style={styles.figmaGamesIcon}>🧠</Text>
          </View>
          <Text style={styles.figmaGamesTitle}>Let's play games!</Text>
        </View>

        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.figmaGamesScrollContainer}
        >
          {miniGames.map((game) => (
            <TouchableOpacity
              key={game.id}
              style={styles.figmaGameCard}
              onPress={() => navigation.navigate('MiniGames', { gameId: game.id })}
              activeOpacity={0.7}
            >
              <View style={[styles.figmaGameIcon, { backgroundColor: game.gradient[0] }]}>
                <View style={[styles.figmaGameIconInner, { backgroundColor: game.gradient[1] }]} />
              </View>
              <View style={styles.figmaGameContent}>
                <Text style={styles.figmaGameTitle}>{game.title}</Text>
                <Text style={styles.figmaGameDescription}>{game.description}</Text>
              </View>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>
    </ScrollView>
  );
}
