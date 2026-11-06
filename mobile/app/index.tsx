import React, { useEffect } from "react";
import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { useRouter } from "expo-router";
import { Colors, Spacing, Typography, BorderRadius } from "../src/constants/theme";
import { useAuthStore } from "../src/store/authStore";

export default function WelcomeScreen() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();

  return (
    <View style={styles.container}>
      <View style={styles.logoContainer}>
        <View style={styles.logoBadge}>
          <Text style={styles.logoIcon}>✨</Text>
        </View>
        <Text style={styles.brandTitle}>
          Craft<Text style={{ color: Colors.secondary }}>Lens</Text>
        </Text>
        <Text style={styles.subtitle}>
          AI-Powered Artisan Business Manager & Marketplace
        </Text>
      </View>

      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={styles.primaryButton}
          activeOpacity={0.8}
          onPress={() => router.push("/language")}
        >
          <Text style={styles.primaryButtonText}>
            Get Started / தொடங்கவும்
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.secondaryButton}
          activeOpacity={0.8}
          onPress={() => router.push("/login")}
        >
          <Text style={styles.secondaryButtonText}>
            Already have an account? Sign In
          </Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.footerNote}>
        Ministry of Social Justice and Empowerment • SIH 26090
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
    justifyContent: "space-between",
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.xxl,
  },
  logoContainer: {
    alignItems: "center",
    marginTop: 80,
  },
  logoBadge: {
    width: 80,
    height: 80,
    borderRadius: BorderRadius.xl,
    backgroundColor: Colors.primary,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: Spacing.md,
    shadowColor: Colors.text,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  logoIcon: {
    fontSize: 36,
  },
  brandTitle: {
    ...Typography.h1,
    color: Colors.primary,
    fontSize: 36,
    letterSpacing: -0.5,
  },
  subtitle: {
    ...Typography.body,
    color: Colors.muted,
    textAlign: "center",
    marginTop: Spacing.sm,
    paddingHorizontal: Spacing.md,
  },
  buttonContainer: {
    width: "100%",
    gap: Spacing.md,
  },
  primaryButton: {
    backgroundColor: Colors.primary,
    paddingVertical: Spacing.base,
    borderRadius: BorderRadius.md,
    alignItems: "center",
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 3,
  },
  primaryButtonText: {
    ...Typography.bodyBold,
    color: Colors.surface,
  },
  secondaryButton: {
    backgroundColor: Colors.surface,
    paddingVertical: Spacing.base,
    borderRadius: BorderRadius.md,
    alignItems: "center",
    borderWidth: 1,
    borderColor: Colors.border,
  },
  secondaryButtonText: {
    ...Typography.body,
    color: Colors.text,
    fontWeight: "500",
  },
  footerNote: {
    ...Typography.caption,
    color: Colors.muted,
    textAlign: "center",
  },
});

