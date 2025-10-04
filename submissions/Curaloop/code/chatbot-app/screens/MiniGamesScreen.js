import { View, Text, TouchableOpacity, ScrollView } from 'react-native';
import { styles } from '../styles';

export default function MiniGamesScreen({ route, navigation }) {
  const { gameId } = route.params || {};

  const games = [
    {
      id: '1',
      title: 'Memory Match',
      description: 'Test your memory by matching pairs of cards. Great for cognitive training!',
      icon: '🧠',
      color: '#3b82f6',
      comingSoon: true,
    },
    {
      id: '2',
      title: 'Word Puzzle',
      description: 'Find hidden words and expand your vocabulary. Keep your mind sharp!',
      icon: '📝',
      color: '#8b5cf6',
      comingSoon: true,
    },
    {
      id: '3',
      title: 'Number Game',
      description: 'Solve math puzzles and challenge your numerical reasoning.',
      icon: '🔢',
      color: '#10b981',
      comingSoon: true,
    },
    {
      id: '4',
      title: 'Pattern Recognition',
      description: 'Identify patterns and sequences. Perfect for cognitive exercise!',
      icon: '🎨',
      color: '#f59e0b',
      comingSoon: true,
    },
  ];

  // If gameId is provided, show specific game details
  const selectedGame = gameId ? games.find(g => g.id === gameId) : null;

  return (
    <View style={styles.container}>
      <ScrollView style={styles.miniGamesContainer}>
        {selectedGame ? (
          // Individual game view
          <View style={styles.gameDetailContainer}>
            <View style={[styles.gameDetailHeader, { backgroundColor: selectedGame.color }]}>
              <Text style={styles.gameDetailIcon}>{selectedGame.icon}</Text>
              <Text style={styles.gameDetailTitle}>{selectedGame.title}</Text>
            </View>

            <View style={styles.gameDetailContent}>
              <Text style={styles.gameDetailDescription}>
                {selectedGame.description}
              </Text>

              {selectedGame.comingSoon ? (
                <View style={styles.comingSoonContainer}>
                  <Text style={styles.comingSoonBadge}>Coming Soon</Text>
                  <Text style={styles.comingSoonText}>
                    This game is currently under development. Check back soon!
                  </Text>
                </View>
              ) : (
                <TouchableOpacity style={styles.playButton}>
                  <Text style={styles.playButtonText}>Start Playing</Text>
                </TouchableOpacity>
              )}

              <TouchableOpacity
                style={styles.backToGamesButton}
                onPress={() => navigation.goBack()}
              >
                <Text style={styles.backToGamesButtonText}>← Back to All Games</Text>
              </TouchableOpacity>
            </View>
          </View>
        ) : (
          // Games list view
          <View>
            <View style={styles.gamesListHeader}>
              <Text style={styles.gamesListTitle}>Cognitive Activities</Text>
              <Text style={styles.gamesListSubtitle}>
                Choose a game to exercise your mind and have fun!
              </Text>
            </View>

            {games.map((game) => (
              <TouchableOpacity
                key={game.id}
                style={[styles.gameListCard, { borderLeftColor: game.color }]}
                onPress={() => navigation.push('MiniGames', { gameId: game.id })}
                activeOpacity={0.7}
              >
                <View style={styles.gameListIconContainer}>
                  <Text style={styles.gameListIcon}>{game.icon}</Text>
                </View>
                <View style={styles.gameListContent}>
                  <Text style={styles.gameListTitle}>{game.title}</Text>
                  <Text style={styles.gameListDescription}>
                    {game.description}
                  </Text>
                  {game.comingSoon && (
                    <View style={styles.comingSoonBadgeSmall}>
                      <Text style={styles.comingSoonBadgeText}>Coming Soon</Text>
                    </View>
                  )}
                </View>
                <Text style={styles.gameListArrow}>→</Text>
              </TouchableOpacity>
            ))}
          </View>
        )}
      </ScrollView>
    </View>
  );
}
