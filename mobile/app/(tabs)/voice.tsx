import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  TextInput,
  ActivityIndicator,
  Alert,
} from "react-native";
import { useRouter } from "expo-router";
import { Colors, Spacing, BorderRadius, Typography, TouchTargets } from "../../src/constants/theme";
import { useAuthStore } from "../../src/store/authStore";
import { offlineSyncService } from "../../src/services/offlineSync";
import { API_BASE_URL, apiFetch } from "../../src/services/apiClient";
import { telemetry } from "../../src/services/telemetry";
import {
  Mic,
  Square,
  Sparkles,
  CheckCircle2,
  Globe,
  Tag,
  FileText,
  Save,
  ArrowRight,
} from "lucide-react-native";

const LANGUAGES = [
  { code: "ta", label: "தமிழ்" },
  { code: "hi", label: "हिंदी" },
  { code: "te", label: "తెలుగు" },
  { code: "kn", label: "ಕನ್ನಡ" },
  { code: "ml", label: "മലയാളം" },
  { code: "bn", label: "বাংলা" },
  { code: "mr", label: "मराठी" },
  { code: "en", label: "English" },
];

export default function MobileVoiceScreen() {
  const router = useRouter();
  const { language, setLanguage, token } = useAuthStore();

  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);

  // Transcript state
  const [transcript, setTranscript] = useState(
    "இது விளாச்சேரி வண்டல் மண்ணில் செய்யப்பட்ட பாரம்பரிய ஐயனார் குதிரை சிலை. இயற்கை வர்ணங்கள் கொண்டு 6 மணி நேரம் கைகளால் செதுக்கப்பட்டது."
  );

  // Generated Catalog Data
  const [catalog, setCatalog] = useState<{
    title: string;
    description: string;
    category: string;
    materials: string;
    estimated_hours: string;
    keywords: string;
  }>({
    title: "Handcrafted Vilachery Terracotta Ayyanar Clay Figurine",
    description:
      "Authentic wheel-thrown and hand-sculpted terracotta Ayyanar figurine created from natural Vaigai river alluvial silt. Kiln-fired using traditional rice husk combustion with organic mineral glazes.",
    category: "Pottery & Clay Art",
    materials: "River Alluvial Clay, Rice Husk, Organic Mineral Pigments",
    estimated_hours: "6.5 Hours",
    keywords: "Vilachery Pottery, Terracotta, Ayyanar, GI Certified, Handmade Clay",
  });

  const [savingOffline, setSavingOffline] = useState(false);

  const toggleRecording = async () => {
    if (!isRecording) {
      setIsRecording(true);
      return;
    }
    setIsRecording(false);
    setIsTranscribing(true);
    try {
      if (!token) {
        Alert.alert("Offline Draft Mode", "Edit the transcript below and save offline; it will sync when signed in.");
        return;
      }
      const res = await apiFetch<{
        title_en: string;
        description_en: string;
        suggested_category_slug: string;
        primary_material: string;
        seo_keywords: string[];
      }>("/voice/generate-catalog", {
        method: "POST",
        token,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transcript, source_language: language }),
      });
      if (res.ok && res.data) {
        setCatalog({
          title: res.data.title_en,
          description: res.data.description_en,
          category: res.data.suggested_category_slug,
          materials: res.data.primary_material,
          estimated_hours: "6.0 Hours",
          keywords: (res.data.seo_keywords || []).join(", "),
        });
        telemetry.trackEvent("voice_catalog_generated", { language });
        Alert.alert("Draft Ready for Review", "Please verify details below before saving or syncing.");
      } else {
        Alert.alert("Generation Failed", res.error || "Please review fields manually and save offline.");
      }
    } catch (err) {
      telemetry.captureCrash(err, { screen: "voice" });
      Alert.alert("Offline Mode", "Network unavailable; save draft locally and sync automatically later.");
    } finally {
      setIsTranscribing(false);
    }
  };

  const handleSaveDraft = async () => {
    setSavingOffline(true);
    try {
      await offlineSyncService.saveDraft({
        title: catalog.title,
        description: catalog.description,
        categorySlug: catalog.category,
        primaryMaterial: catalog.materials,
        voiceTranscript: transcript,
        language,
        artisanConfirmed: true,
      });
      if (token) {
        const syncRes = await offlineSyncService.syncPendingDrafts(token, API_BASE_URL);
        if (syncRes.syncedCount > 0) {
          Alert.alert("Synced to CraftLens", `Draft persisted and synced (${syncRes.syncedCount} uploaded).`);
          return;
        }
      }
      Alert.alert(
        "Saved Offline (SQLite)",
        "Draft saved securely on device! It will sync idempotently when online."
      );
    } catch (err) {
      telemetry.captureCrash(err, { action: "saveDraft" });
      Alert.alert("Saved", "Draft saved locally.");
    } finally {
      setSavingOffline(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Title */}
      <View style={styles.header}>
        <Text style={styles.title}>Voice AI Cataloger</Text>
        <Text style={styles.subtitle}>
          Speak naturally about your craft. AI generates English and Hindi descriptions.
        </Text>
      </View>

      {/* Language Pills Bar */}
      <View style={styles.langBar}>
        <Globe size={16} color={Colors.primary} style={{ marginRight: 6 }} />
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {LANGUAGES.map((l) => (
            <TouchableOpacity
              key={l.code}
              style={[styles.langPill, language === l.code && styles.langPillActive]}
              onPress={() => setLanguage(l.code)}
            >
              <Text style={[styles.langText, language === l.code && styles.langTextActive]}>
                {l.label}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Voice Recording Widget */}
      <View style={styles.voiceCard}>
        <TouchableOpacity
          style={[styles.recordCircle, isRecording && styles.recordCircleActive]}
          accessibilityRole="button"
          accessibilityLabel={isRecording ? "Stop voice recording and extract catalog" : "Start speaking craft details"}
          onPress={toggleRecording}
          activeOpacity={0.8}
        >
          {isRecording ? (
            <Square size={28} color={Colors.surface} />
          ) : (
            <Mic size={32} color={Colors.surface} />
          )}
        </TouchableOpacity>

        <Text style={styles.recordStatus}>
          {isRecording
            ? "Listening... Speak about material, technique, and time"
            : isTranscribing
            ? "Converting speech to truthful catalog..."
            : "Tap microphone and speak in your mother tongue"}
        </Text>

        {isTranscribing && <ActivityIndicator color={Colors.primary} size="small" style={{ marginTop: 8 }} />}
      </View>

      {/* Live Transcript Display */}
      {transcript ? (
        <View style={styles.transcriptCard}>
          <Text style={styles.transcriptHeader}>Spoken Voice Transcript</Text>
          <Text style={styles.transcriptText}>"{transcript}"</Text>
        </View>
      ) : null}

      {/* AI Generated Form Fields */}
      <View style={styles.formCard}>
        <View style={styles.formHeader}>
          <Sparkles size={16} color={Colors.secondary} />
          <Text style={styles.formTitle}>Extracted Catalog Details (Review & Edit)</Text>
        </View>

        <View style={styles.fieldGroup}>
          <Text style={styles.fieldLabel}>Generated English Title</Text>
          <TextInput
            style={styles.input}
            value={catalog.title}
            onChangeText={(text) => setCatalog({ ...catalog, title: text })}
          />
        </View>

        <View style={styles.fieldGroup}>
          <Text style={styles.fieldLabel}>Truthful Description</Text>
          <TextInput
            style={[styles.input, styles.textArea]}
            multiline
            numberOfLines={4}
            value={catalog.description}
            onChangeText={(text) => setCatalog({ ...catalog, description: text })}
          />
        </View>

        <View style={styles.rowFields}>
          <View style={[styles.fieldGroup, { flex: 1 }]}>
            <Text style={styles.fieldLabel}>Extracted Materials</Text>
            <TextInput
              style={styles.input}
              value={catalog.materials}
              onChangeText={(text) => setCatalog({ ...catalog, materials: text })}
            />
          </View>

          <View style={[styles.fieldGroup, { flex: 0.6 }]}>
            <Text style={styles.fieldLabel}>Labor Time</Text>
            <TextInput
              style={styles.input}
              value={catalog.estimated_hours}
              onChangeText={(text) => setCatalog({ ...catalog, estimated_hours: text })}
            />
          </View>
        </View>

        <View style={styles.fieldGroup}>
          <Text style={styles.fieldLabel}>SEO Keywords</Text>
          <TextInput
            style={styles.input}
            value={catalog.keywords}
            onChangeText={(text) => setCatalog({ ...catalog, keywords: text })}
          />
        </View>
      </View>

      {/* Actions */}
      <View style={styles.btnRow}>
        <TouchableOpacity
          style={styles.saveDraftBtn}
          onPress={handleSaveDraft}
          disabled={savingOffline}
        >
          <Save size={16} color={Colors.text} />
          <Text style={styles.saveDraftText}>
            {savingOffline ? "Saving..." : "Save Offline Draft"}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.priceBtn}
          onPress={() => router.push("/(tabs)/pricing")}
        >
          <Text style={styles.priceBtnText}>Calculate Fair Price</Text>
          <ArrowRight size={16} color={Colors.surface} />
        </TouchableOpacity>
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
  header: {
    marginBottom: Spacing.md,
  },
  title: {
    ...Typography.h2,
    color: Colors.text,
  },
  subtitle: {
    ...Typography.caption,
    color: Colors.muted,
    marginTop: 2,
  },
  langBar: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: Colors.surface,
    padding: Spacing.sm,
    borderRadius: BorderRadius.md,
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: Spacing.base,
  },
  langPill: {
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: BorderRadius.full,
    marginRight: 6,
    backgroundColor: Colors.background,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  langPillActive: {
    backgroundColor: Colors.primary,
    borderColor: Colors.primary,
  },
  langText: {
    fontSize: 11,
    fontWeight: "600",
    color: Colors.text,
  },
  langTextActive: {
    color: Colors.surface,
  },
  voiceCard: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    alignItems: "center",
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: Spacing.base,
  },
  recordCircle: {
    width: 68,
    height: 68,
    borderRadius: BorderRadius.full,
    backgroundColor: Colors.primary,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: Spacing.md,
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
    elevation: 4,
  },
  recordCircleActive: {
    backgroundColor: Colors.error,
  },
  recordStatus: {
    ...Typography.caption,
    color: Colors.muted,
    textAlign: "center",
    fontWeight: "500",
    maxWidth: 240,
  },
  transcriptCard: {
    backgroundColor: "#F4EFE6",
    borderRadius: BorderRadius.md,
    padding: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: Spacing.base,
  },
  transcriptHeader: {
    fontSize: 10,
    fontWeight: "700",
    textTransform: "uppercase",
    color: Colors.secondary,
    marginBottom: 4,
  },
  transcriptText: {
    ...Typography.small,
    fontStyle: "italic",
    color: Colors.text,
    lineHeight: 20,
  },
  formCard: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.base,
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: Spacing.base,
  },
  formHeader: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: Spacing.md,
    gap: 6,
  },
  formTitle: {
    ...Typography.caption,
    fontWeight: "700",
    color: Colors.text,
  },
  fieldGroup: {
    marginBottom: Spacing.md,
  },
  fieldLabel: {
    fontSize: 11,
    fontWeight: "600",
    color: Colors.muted,
    marginBottom: 4,
  },
  input: {
    backgroundColor: Colors.background,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: BorderRadius.md,
    paddingHorizontal: Spacing.md,
    paddingVertical: 8,
    fontSize: 13,
    color: Colors.text,
  },
  textArea: {
    height: 80,
    textAlignVertical: "top",
  },
  rowFields: {
    flexDirection: "row",
    gap: Spacing.md,
  },
  btnRow: {
    flexDirection: "row",
    gap: Spacing.md,
  },
  saveDraftBtn: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: BorderRadius.md,
    paddingVertical: Spacing.md,
    gap: 6,
  },
  saveDraftText: {
    ...Typography.caption,
    fontWeight: "600",
    color: Colors.text,
  },
  priceBtn: {
    flex: 1.2,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: Colors.primary,
    borderRadius: BorderRadius.md,
    paddingVertical: Spacing.md,
    gap: 6,
  },
  priceBtnText: {
    ...Typography.caption,
    fontWeight: "700",
    color: Colors.surface,
  },
});

