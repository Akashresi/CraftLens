import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from "react-native";
import { useRouter } from "expo-router";
import { Colors, Spacing, BorderRadius, Typography } from "../../src/constants/theme";
import { useAuthStore } from "../../src/store/authStore";
import {
  Camera,
  Mic,
  Calculator,
  TrendingUp,
  Package,
  AlertTriangle,
  Sparkles,
  ArrowRight,
  ShieldCheck,
} from "lucide-react-native";

export default function ArtisanHomeScreen() {
  const router = useRouter();
  const { user, language } = useAuthStore();
  const [voiceQueryActive, setVoiceQueryActive] = useState(false);

  const getGreeting = () => {
    switch (language) {
      case "ta":
        return "வணக்கம்";
      case "hi":
        return "नमस्ते";
      case "te":
        return "నమస్కారం";
      case "kn":
        return "ನಮಸ್ಕಾರ";
      case "ml":
        return "നമസ്കാരം";
      default:
        return "Welcome";
    }
  };

  const handleVoiceAssistant = () => {
    setVoiceQueryActive(true);
    setTimeout(() => {
      setVoiceQueryActive(false);
      Alert.alert(
        "AI Business Assistant",
        language === "ta"
          ? "இந்த வாரம் உங்கள் மண்பாண்ட தயாரிப்புகளுக்கு 12 ஆர்டர்கள் வந்துள்ளன! மொத்த வருமானம் ₹18,400. 1 பொருளுக்கு இருப்பு குறைவாக உள்ளது."
          : "You received 12 orders this week! Total income ₹18,400. 1 item is running low on stock."
      );
    }, 1500);
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Artisan Welcome Card */}
      <View style={styles.welcomeCard}>
        <View style={styles.welcomeRow}>
          <View style={{ flex: 1 }}>
            <Text style={styles.greetingText}>
              {getGreeting()}, {user?.full_name || "Meenakshi Sundaram"}
            </Text>
            <View style={styles.clusterBadge}>
              <ShieldCheck size={14} color={Colors.success} />
              <Text style={styles.clusterText}>Vilachery Pottery Cluster • GI Verified</Text>
            </View>
          </View>
        </View>

        {/* Voice Assistant Tap Bar */}
        <TouchableOpacity
          style={[styles.voiceBar, voiceQueryActive && styles.voiceBarActive]}
          onPress={handleVoiceAssistant}
          activeOpacity={0.8}
        >
          <View style={styles.micIconContainer}>
            <Mic size={18} color={Colors.surface} />
          </View>
          <Text style={styles.voiceBarText}>
            {voiceQueryActive
              ? "Listening to voice..."
              : language === "ta"
              ? "விற்பனை, லாபம் பற்றி தமிழில் கேட்க அழுத்தவும்"
              : "Tap to ask business questions with your voice"}
          </Text>
          <Sparkles size={16} color={Colors.secondary} />
        </TouchableOpacity>
      </View>

      {/* Metrics Row */}
      <View style={styles.metricsGrid}>
        <View style={styles.metricCard}>
          <View style={styles.metricHeader}>
            <Text style={styles.metricLabel}>Total Revenue</Text>
            <TrendingUp size={16} color={Colors.primary} />
          </View>
          <Text style={styles.metricValue}>₹48,600</Text>
          <Text style={styles.metricSubtext}>+18% this month</Text>
        </View>

        <View style={styles.metricCard}>
          <View style={styles.metricHeader}>
            <Text style={styles.metricLabel}>Fair Wages</Text>
            <Sparkles size={16} color={Colors.secondary} />
          </View>
          <Text style={[styles.metricValue, { color: Colors.secondary }]}>₹32,400</Text>
          <Text style={styles.metricSubtext}>100% direct to bank</Text>
        </View>
      </View>

      {/* Low Stock Warning */}
      <View style={styles.warningCard}>
        <AlertTriangle size={18} color={Colors.warning} />
        <View style={{ flex: 1, marginLeft: 10 }}>
          <Text style={styles.warningTitle}>Low Inventory Alert</Text>
          <Text style={styles.warningDesc}>
            Terracotta Diya Set has only 2 units left in stock.
          </Text>
        </View>
      </View>

      {/* Quick Actions Grid */}
      <Text style={styles.sectionTitle}>Artisan Studio Tools</Text>
      <View style={styles.toolsGrid}>
        <TouchableOpacity
          style={styles.toolCard}
          onPress={() => router.push("/(tabs)/studio")}
          activeOpacity={0.8}
        >
          <View style={[styles.toolIcon, { backgroundColor: "#EAF2ED" }]}>
            <Camera size={22} color={Colors.primary} />
          </View>
          <Text style={styles.toolTitle}>AI Photo Studio</Text>
          <Text style={styles.toolDesc}>Remove background & fix lighting</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.toolCard}
          onPress={() => router.push("/(tabs)/voice")}
          activeOpacity={0.8}
        >
          <View style={[styles.toolIcon, { backgroundColor: "#F7ECE6" }]}>
            <Mic size={22} color={Colors.secondary} />
          </View>
          <Text style={styles.toolTitle}>Voice Catalog</Text>
          <Text style={styles.toolDesc}>Describe craft in mother tongue</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.toolCard}
          onPress={() => router.push("/(tabs)/pricing")}
          activeOpacity={0.8}
        >
          <View style={[styles.toolIcon, { backgroundColor: "#EBF3EF" }]}>
            <Calculator size={22} color={Colors.success} />
          </View>
          <Text style={styles.toolTitle}>Fair Wage Pricing</Text>
          <Text style={styles.toolDesc}>Calculate labor & profit tiers</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.toolCard}
          onPress={() => router.push("/(tabs)/orders")}
          activeOpacity={0.8}
        >
          <View style={[styles.toolIcon, { backgroundColor: "#F5F3ED" }]}>
            <Package size={22} color={Colors.text} />
          </View>
          <Text style={styles.toolTitle}>Manage Orders</Text>
          <Text style={styles.toolDesc}>Retail & wholesale dispatch</Text>
        </TouchableOpacity>
      </View>

      {/* Recent Orders Overview */}
      <View style={styles.recentSection}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Recent Orders</Text>
          <TouchableOpacity onPress={() => router.push("/(tabs)/orders")}>
            <Text style={styles.viewAllText}>View All</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.orderItem}>
          <View style={{ flex: 1 }}>
            <Text style={styles.orderTitle}>Vilachery Clay Ayyanar Figurine</Text>
            <Text style={styles.orderBuyer}>Buyer: Anita Roy • Bengaluru</Text>
            <Text style={styles.orderPrice}>₹1,850 (Artisan Wage: ₹950)</Text>
          </View>
          <View style={styles.statusBadge}>
            <Text style={styles.statusText}>Ready to Pack</Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  content: {
    padding: Spacing.base,
    paddingBottom: Spacing.xl,
  },
  welcomeCard: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.base,
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: Spacing.base,
  },
  welcomeRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  greetingText: {
    ...Typography.h2,
    color: Colors.text,
  },
  clusterBadge: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: 4,
  },
  clusterText: {
    ...Typography.caption,
    color: Colors.success,
    fontWeight: "600",
    marginLeft: 4,
  },
  voiceBar: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: Colors.background,
    borderRadius: BorderRadius.md,
    padding: Spacing.sm,
    paddingHorizontal: Spacing.md,
    marginTop: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  voiceBarActive: {
    borderColor: Colors.secondary,
    backgroundColor: "#FBF3EE",
  },
  micIconContainer: {
    width: 32,
    height: 32,
    borderRadius: BorderRadius.full,
    backgroundColor: Colors.primary,
    alignItems: "center",
    justifyContent: "center",
    marginRight: 10,
  },
  voiceBarText: {
    ...Typography.caption,
    color: Colors.text,
    flex: 1,
    fontWeight: "500",
  },
  metricsGrid: {
    flexDirection: "row",
    gap: Spacing.md,
    marginBottom: Spacing.base,
  },
  metricCard: {
    flex: 1,
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.base,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  metricHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 4,
  },
  metricLabel: {
    ...Typography.caption,
    color: Colors.muted,
  },
  metricValue: {
    ...Typography.h2,
    color: Colors.primary,
    fontWeight: "700",
  },
  metricSubtext: {
    fontSize: 11,
    color: Colors.success,
    fontWeight: "500",
    marginTop: 2,
  },
  warningCard: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#FDF8ED",
    borderRadius: BorderRadius.md,
    padding: Spacing.md,
    borderWidth: 1,
    borderColor: "#F4DFB8",
    marginBottom: Spacing.base,
  },
  warningTitle: {
    ...Typography.caption,
    fontWeight: "700",
    color: Colors.warning,
  },
  warningDesc: {
    fontSize: 11,
    color: Colors.text,
    marginTop: 1,
  },
  sectionTitle: {
    ...Typography.bodyBold,
    color: Colors.text,
    marginBottom: Spacing.md,
  },
  toolsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: Spacing.md,
    marginBottom: Spacing.base,
  },
  toolCard: {
    width: "47.5%",
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.base,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  toolIcon: {
    width: 44,
    height: 44,
    borderRadius: BorderRadius.md,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: Spacing.sm,
  },
  toolTitle: {
    ...Typography.small,
    fontWeight: "700",
    color: Colors.text,
  },
  toolDesc: {
    fontSize: 11,
    color: Colors.muted,
    marginTop: 2,
    lineHeight: 14,
  },
  recentSection: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.base,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  sectionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: Spacing.sm,
  },
  viewAllText: {
    ...Typography.caption,
    color: Colors.primary,
    fontWeight: "600",
  },
  orderItem: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: Spacing.sm,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
  },
  orderTitle: {
    ...Typography.small,
    fontWeight: "600",
    color: Colors.text,
  },
  orderBuyer: {
    fontSize: 11,
    color: Colors.muted,
    marginTop: 1,
  },
  orderPrice: {
    fontSize: 11,
    fontWeight: "700",
    color: Colors.primary,
    marginTop: 2,
  },
  statusBadge: {
    backgroundColor: "#EAF2ED",
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: BorderRadius.sm,
    borderWidth: 1,
    borderColor: "#CFE3D5",
  },
  statusText: {
    fontSize: 10,
    fontWeight: "700",
    color: Colors.success,
  },
});
