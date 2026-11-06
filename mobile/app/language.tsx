import React from "react";
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from "react-native";
import { useRouter } from "expo-router";
import { Colors, Spacing, Typography, BorderRadius } from "../src/constants/theme";
import { useAuthStore } from "../src/store/authStore";

const LANGUAGES = [
  { code: "ta", native: "தமிழ்", english: "Tamil", greeting: "வணக்கம்! கைவினைப் பொருட்களை எளிதாக விற்கலாம்." },
  { code: "hi", native: "हिंदी", english: "Hindi", greeting: "नमस्ते! हस्तशिल्प को डिजिटल बनाएं।" },
  { code: "en", native: "English", english: "English", greeting: "Welcome! Digitize and sell your handmade crafts." },
  { code: "te", native: "తెలుగు", english: "Telugu", greeting: "నమస్కారం! మీ హస్తకళలను సులభంగా విక్రయించండి." },
  { code: "kn", native: "ಕನ್ನಡ", english: "Kannada", greeting: "ನಮಸ್ಕಾರ! ನಿಮ್ಮ ಕರಕುಶಲ ವಸ್ತುಗಳನ್ನು ಮಾರಾಟ ಮಾಡಿ." },
  { code: "ml", native: "മലയാളം", english: "Malayalam", greeting: "നമസ്കാരം! നിങ്ങളുടെ കരകൗശലങ്ങൾ വിപണനം ചെയ്യുക." },
];

export default function LanguageScreen() {
  const router = useRouter();
  const { language, setLanguage } = useAuthStore();

  const handleSelectLanguage = (code: string) => {
    setLanguage(code);
    router.push("/register");
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Select Your Language</Text>
      <Text style={styles.subtitle}>மொழியைத் தேர்ந்தெடுக்கவும் / भाषा चुनें</Text>

      <View style={styles.listContainer}>
        {LANGUAGES.map((lang) => {
          const isSelected = language === lang.code;
          return (
            <TouchableOpacity
              key={lang.code}
              style={[styles.card, isSelected && styles.selectedCard]}
              activeOpacity={0.7}
              onPress={() => handleSelectLanguage(lang.code)}
            >
              <View style={styles.cardHeader}>
                <Text style={[styles.nativeText, isSelected && styles.selectedText]}>
                  {lang.native}
                </Text>
                <Text style={styles.englishText}>({lang.english})</Text>
              </View>
              <Text style={styles.greetingText}>{lang.greeting}</Text>
            </TouchableOpacity>
          );
        })}
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
    padding: Spacing.lg,
  },
  title: {
    ...Typography.h2,
    color: Colors.text,
    textAlign: "center",
  },
  subtitle: {
    ...Typography.body,
    color: Colors.muted,
    textAlign: "center",
    marginBottom: Spacing.lg,
  },
  listContainer: {
    gap: Spacing.md,
  },
  card: {
    backgroundColor: Colors.surface,
    padding: Spacing.base,
    borderRadius: BorderRadius.lg,
    borderWidth: 1.5,
    borderColor: Colors.border,
    shadowColor: Colors.text,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  selectedCard: {
    borderColor: Colors.primary,
    backgroundColor: "#EFF5F1",
  },
  cardHeader: {
    flexDirection: "row",
    alignItems: "baseline",
    gap: Spacing.sm,
    marginBottom: Spacing.xs,
  },
  nativeText: {
    ...Typography.h3,
    color: Colors.text,
  },
  englishText: {
    ...Typography.small,
    color: Colors.muted,
  },
  selectedText: {
    color: Colors.primary,
  },
  greetingText: {
    ...Typography.small,
    color: Colors.muted,
  },
});

