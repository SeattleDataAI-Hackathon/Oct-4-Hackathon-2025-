import { View, Text, ScrollView } from 'react-native';
import { styles } from '../styles';

export default function DashboardScreen() {
  const chartData = {
    weeks: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    memory: [76, 78, 77, 79],
    attention: [68, 72, 76, 80],
  };

  // Simple chart visualization using positioned views
  const renderChart = () => {
    const maxValue = 100;
    const minValue = 50;
    const range = maxValue - minValue;

    return (
      <View style={styles.dashboardChart}>
        {/* Y-axis labels */}
        <View style={styles.dashboardChartYAxis}>
          <Text style={styles.dashboardChartYLabel}>100</Text>
          <Text style={styles.dashboardChartYLabel}>80</Text>
          <Text style={styles.dashboardChartYLabel}>65</Text>
          <Text style={styles.dashboardChartYLabel}>50</Text>
        </View>

        {/* Chart area */}
        <View style={styles.dashboardChartArea}>
          {/* Memory line (blue) */}
          <View style={styles.dashboardMemoryLine} />
          {chartData.memory.map((value, index) => {
            const leftPos = (index * 68) + 10;
            const topPos = ((maxValue - value) / range) * 150;
            return (
              <View
                key={`memory-${index}`}
                style={[
                  styles.dashboardMemoryPoint,
                  { left: leftPos, top: topPos }
                ]}
              />
            );
          })}

          {/* Attention line (green) */}
          <View style={styles.dashboardAttentionLine} />
          {chartData.attention.map((value, index) => {
            const leftPos = (index * 68) + 10;
            const topPos = ((maxValue - value) / range) * 150;
            return (
              <View
                key={`attention-${index}`}
                style={[
                  styles.dashboardAttentionPoint,
                  { left: leftPos, top: topPos }
                ]}
              />
            );
          })}

          {/* X-axis labels */}
          <View style={styles.dashboardChartXAxis}>
            {chartData.weeks.map((week, index) => (
              <Text key={week} style={styles.dashboardChartXLabel}>
                {week}
              </Text>
            ))}
          </View>
        </View>
      </View>
    );
  };

  return (
    <ScrollView style={styles.dashboardContainer}>
      {/* Header */}
      <View style={styles.dashboardHeader}>
        <View style={styles.dashboardHeaderIcon}>
          <Text style={styles.dashboardHeaderIconText}>📈</Text>
        </View>
        <View style={styles.dashboardHeaderText}>
          <Text style={styles.dashboardHeaderTitle}>Progress Overview</Text>
          <Text style={styles.dashboardHeaderSubtitle}>Past 30 days</Text>
        </View>
      </View>

      {/* Chart Card */}
      <View style={styles.dashboardChartCard}>
        <Text style={styles.dashboardChartTitle}>Progress over the past 30 days</Text>
        {renderChart()}

        {/* Legend */}
        <View style={styles.dashboardLegend}>
          <View style={styles.dashboardLegendItem}>
            <View style={styles.dashboardMemoryDot} />
            <Text style={styles.dashboardLegendText}>Memory</Text>
          </View>
          <View style={styles.dashboardLegendItem}>
            <View style={styles.dashboardAttentionDot} />
            <Text style={styles.dashboardLegendText}>Attention</Text>
          </View>
        </View>
      </View>

      {/* Metric Cards */}
      <View style={styles.dashboardMetrics}>
        {/* Memory Card */}
        <View style={styles.dashboardMemoryCard}>
          <View style={styles.dashboardMetricIcon}>
            <Text style={styles.dashboardMemoryIconText}>🧠</Text>
          </View>
          <View style={styles.dashboardMetricContent}>
            <Text style={styles.dashboardMetricTitle}>Memory</Text>
            <Text style={styles.dashboardMetricSubtitle}>Stable performance</Text>
          </View>
          <View style={styles.dashboardMetricStats}>
            <Text style={styles.dashboardMetricValue}>79%</Text>
            <Text style={styles.dashboardMetricStable}>Stable</Text>
          </View>
        </View>

        {/* Attention Card */}
        <View style={styles.dashboardAttentionCard}>
          <View style={styles.dashboardMetricIcon}>
            <Text style={styles.dashboardAttentionIconText}>👁️</Text>
          </View>
          <View style={styles.dashboardMetricContent}>
            <Text style={styles.dashboardMetricTitle}>Attention</Text>
            <Text style={styles.dashboardMetricSubtitle}>Great improvement</Text>
          </View>
          <View style={styles.dashboardMetricStats}>
            <Text style={styles.dashboardMetricValue}>80%</Text>
            <Text style={styles.dashboardMetricImproved}>↑ +12%</Text>
          </View>
        </View>

        {/* Mood Card */}
        <View style={styles.dashboardMoodCard}>
          <View style={styles.dashboardMetricIcon}>
            <Text style={styles.dashboardMoodIconText}>💛</Text>
          </View>
          <View style={styles.dashboardMetricContent}>
            <Text style={styles.dashboardMetricTitle}>Mood</Text>
            <Text style={styles.dashboardMetricSubtitle}>Much better</Text>
          </View>
          <View style={styles.dashboardMetricStats}>
            <Text style={styles.dashboardMetricValue}>Good</Text>
            <Text style={styles.dashboardMetricImproved}>Improved</Text>
          </View>
        </View>
      </View>

      {/* Summary Card */}
      <View style={styles.dashboardSummaryCard}>
        <Text style={styles.dashboardSummaryTitle}>
          Attention +12%, Memory stable, Mood improved 🪴
        </Text>
        <Text style={styles.dashboardSummaryText}>
          Keep up the great work with your daily exercises!
        </Text>
      </View>
    </ScrollView>
  );
}
