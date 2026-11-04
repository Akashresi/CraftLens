import React, { useState } from "react";
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, Alert, ActivityIndicator } from "react-native";
import { useRouter } from "expo-router";
import { Colors, Spacing, Typography, BorderRadius } from "../src/constants/theme";
import { useAuthStore } from "../src/store/authStore";

export default function MobileOnboardingScreen() {
  const router = useRouter();
  const { token } = useAuthStore();
  const [craft, setCraft] = useState("Handloom Silk Weaving");
  const [experience, setExperience] = useState("12");
  const [district, setDistrict] = useState("Kanchipuram");
  const [state, setState] = useState("Tamil Nadu");
  const [pehchanCard, setPehchanCard] = useState("");
  const [loading, setLoading] = useState(false);

  const handleComplete = async () => {
    setLoading(true);
    try {
      await fetch("http://127.0.0.1:8000/api/v1/artisans/me", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          craft_specialization: craft,
          experience_years: parseInt(experience) || 1,
          city: district,
          state,
          bank_account_configured: true,
        }),
      });

      if (pehchanCard) {
        await fetch("http://127.0.0.1:8000/api/v1/artisans/me/verify", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            document_type: "PEHCHAN_CARD",
            document_number: pehchanCard,
            document_url: "https://craftlens-storage.org/docs/pehchan_sample.pdf",
          }),
        });
      }

      router.replace("/(tabs)/home");
    } catch {
      Alert.alert("Error", "Could not complete onboarding. Proceeding to studio...");
      router.replace("/(tabs)/home");
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Artisan Profile Setup</Text>
      <Text style={styles.subtitle}>உங்கள் கைவினை தகவல்கள் / अपनी शिल्प जानकारी दर्ज करें</Text>

      <View style={styles.stepCard}>
        <Text style={styles.cardTitle}>1. Your Traditional Craft / உங்கள் கைவினை</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g. Silk Weaving, Terracotta, Wood Carving"
          value={craft}
          onChangeText={setCraft}
        />
      </View>

      <View style={styles.stepCard}>
        <Text style={styles.cardTitle}>2. Experience / அனுபவம் (Years)</Text>
        <TextInput
          style={styles.input}
          placeholder="10"
          keyboardType="numeric"
          value={experience}
          onChangeText={setExperience}
        />
      </View>

      <View style={styles.stepCard}>
        <Text style={styles.cardTitle}>3. Location / உங்கள் இருப்பிடம்</Text>
        <TextInput
          style={[styles.input, { marginBottom: Spacing.sm }]}
          placeholder="District / Town (e.g. Kanchipuram)"
          value={district}
          onChangeText={setDistrict}
        />
        <TextInput
          style={styles.input}
          placeholder="State (e.g. Tamil Nadu)"
          value={state}
          onChangeText={setState}
        />
      </View>

      <View style={styles.stepCard}>
        <Text style={styles.cardTitle}>4. Pehchan / Weaver ID (Optional)</Text>
        <TextInput
          style={styles.input}
          placeholder="Govt Artisan ID number"
          value={pehchanCard}
          onChangeText={setPehchanCard}
        />
      </View>

      <TouchableOpacity
        style={styles.finishButton}
        activeOpacity={0.8}
        onPress={handleComplete}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color={Colors.surface} />
        ) : (
          <Text style={styles.finishButtonText}>Enter Studio / தொடங்குங்கள்</Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  content: {
    padding: Spacing.lg,
  },
  title: {
    ...Typography.h2,
    color: Colors.text,
  },
  subtitle: {
    ...Typography.body,
    color: Colors.muted,
    marginBottom: Spacing.lg,
  },
  stepCard: {
    backgroundColor: Colors.surface,
    padding: Spacing.base,
    borderRadius: BorderRadius.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: Spacing.md,
  },
  cardTitle: {
    ...Typography.small,
    fontWeight: "600",
    color: Colors.text,
    marginBottom: Spacing.xs,
  },
  input: {
    backgroundColor: Colors.background,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: BorderRadius.md,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    ...Typography.body,
    color: Colors.text,
  },
  finishButton: {
    backgroundColor: Colors.primary,
    paddingVertical: Spacing.base,
    borderRadius: BorderRadius.md,
    alignItems: "center",
    marginTop: Spacing.md,
    marginBottom: Spacing.xxl,
  },
  finishButtonText: {
    ...Typography.bodyBold,
    color: Colors.surface,
  },
});
