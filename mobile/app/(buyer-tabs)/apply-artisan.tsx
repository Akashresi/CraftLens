import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from "react-native";
import { useRouter } from "expo-router";
import { Colors, Spacing, Typography, BorderRadius } from "../../src/constants/theme";
import { useAuthStore } from "../../src/store/authStore";
import { Sparkles, ArrowLeft, Send } from "lucide-react-native";

export default function ApplyArtisanScreen() {
  const router = useRouter();
  const { user, token } = useAuthStore();

  const [fullName, setFullName] = useState(user?.full_name || "");
  const [craftSpecialization, setCraftSpecialization] = useState("");
  const [experienceYears, setExperienceYears] = useState("5");
  const [city, setCity] = useState("");
  const [state, setState] = useState("");
  const [portfolioUrl, setPortfolioUrl] = useState("");
  const [supportingDocsUrl, setSupportingDocsUrl] = useState("");
  const [craftDescription, setCraftDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    // Validation
    if (!fullName.trim()) {
      Alert.alert("Missing Field", "Please enter your full name.");
      return;
    }
    if (!craftSpecialization.trim()) {
      Alert.alert("Missing Field", "Please specify your craft specialization (e.g. Handloom Weaving, Terracotta Pottery).");
      return;
    }
    const expNum = parseInt(experienceYears, 10);
    if (isNaN(expNum) || expNum < 0) {
      Alert.alert("Invalid Input", "Please enter a valid number of years of experience.");
      return;
    }
    if (!city.trim() || !state.trim()) {
      Alert.alert("Missing Field", "Please enter your city and state.");
      return;
    }
    if (!craftDescription.trim() || craftDescription.trim().length < 10) {
      Alert.alert("Missing Details", "Please provide a description of your craft lineage and technique (at least 10 characters).");
      return;
    }

    setSubmitting(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/artisan-applications/me", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          full_name: fullName.trim(),
          craft_specialization: craftSpecialization.trim(),
          experience_years: expNum,
          city: city.trim(),
          state: state.trim(),
          portfolio_url: portfolioUrl.trim() || undefined,
          supporting_documents_url: supportingDocsUrl.trim() || undefined,
          craft_description: craftDescription.trim(),
        }),
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        Alert.alert(
          "Application Could Not Be Submitted",
          data.detail || data.message || "An error occurred while submitting."
        );
        return;
      }

      Alert.alert(
        "Application Submitted!",
        "Your artisan application has been saved with PENDING status. Our administrative team will verify your craft details. You will remain a Buyer until approved.",
        [
          {
            text: "View Status in Profile",
            onPress: () => router.replace("/(buyer-tabs)/profile"),
          },
        ]
      );
    } catch (err) {
      Alert.alert("Network Error", "Unable to connect to server. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
        <ArrowLeft color={Colors.text} size={18} />
        <Text style={styles.backText}>Back to Profile</Text>
      </TouchableOpacity>

      <View style={styles.header}>
        <View style={styles.iconCircle}>
          <Sparkles color={Colors.surface} size={22} />
        </View>
        <Text style={styles.title}>Apply to Become an Artisan</Text>
        <Text style={styles.subtitle}>
          Tell us about your heritage craft, specialization, and cluster location. All applications undergo administrative verification.
        </Text>
      </View>

      <View style={styles.formCard}>
        <View style={styles.formGroup}>
          <Text style={styles.label}>Full Legal Name *</Text>
          <TextInput
            style={styles.input}
            placeholder="e.g. Ramesh Channapatna"
            placeholderTextColor={Colors.muted}
            value={fullName}
            onChangeText={setFullName}
          />
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Craft Specialization *</Text>
          <TextInput
            style={styles.input}
            placeholder="e.g. Channapatna Wooden Toys & Natural Lacquerware"
            placeholderTextColor={Colors.muted}
            value={craftSpecialization}
            onChangeText={setCraftSpecialization}
          />
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Years of Experience *</Text>
          <TextInput
            style={styles.input}
            placeholder="e.g. 8"
            placeholderTextColor={Colors.muted}
            keyboardType="numeric"
            value={experienceYears}
            onChangeText={setExperienceYears}
          />
        </View>

        <View style={styles.row}>
          <View style={[styles.formGroup, { flex: 1 }]}>
            <Text style={styles.label}>City / District *</Text>
            <TextInput
              style={styles.input}
              placeholder="e.g. Ramanagara"
              placeholderTextColor={Colors.muted}
              value={city}
              onChangeText={setCity}
            />
          </View>

          <View style={[styles.formGroup, { flex: 1 }]}>
            <Text style={styles.label}>State *</Text>
            <TextInput
              style={styles.input}
              placeholder="e.g. Karnataka"
              placeholderTextColor={Colors.muted}
              value={state}
              onChangeText={setState}
            />
          </View>
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Portfolio or Social Media URL (Optional)</Text>
          <TextInput
            style={styles.input}
            placeholder="https://instagram.com/mycraft or portfolio site"
            placeholderTextColor={Colors.muted}
            autoCapitalize="none"
            keyboardType="url"
            value={portfolioUrl}
            onChangeText={setPortfolioUrl}
          />
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Supporting Document URL (Optional)</Text>
          <TextInput
            style={styles.input}
            placeholder="Pehchan card link, artisan ID, or certificate URL"
            placeholderTextColor={Colors.muted}
            autoCapitalize="none"
            keyboardType="url"
            value={supportingDocsUrl}
            onChangeText={setSupportingDocsUrl}
          />
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Craft Description & Lineage *</Text>
          <TextInput
            style={[styles.input, styles.textArea]}
            placeholder="Describe your craft technique, heritage lineage, materials used, and whether your craft is GI certified..."
            placeholderTextColor={Colors.muted}
            multiline
            numberOfLines={4}
            textAlignVertical="top"
            value={craftDescription}
            onChangeText={setCraftDescription}
          />
        </View>

        <View style={styles.noteBox}>
          <Text style={styles.noteTitle}>Important Notice:</Text>
          <Text style={styles.noteBody}>
            Submitting this application does not automatically grant the Artisan role. You will continue to have Buyer access until an administrator approves your application.
          </Text>
        </View>

        <TouchableOpacity
          style={styles.submitButton}
          activeOpacity={0.85}
          onPress={handleSubmit}
          disabled={submitting}
        >
          {submitting ? (
            <ActivityIndicator color={Colors.surface} />
          ) : (
            <View style={styles.submitBtnRow}>
              <Send color={Colors.surface} size={16} />
              <Text style={styles.submitButtonText}>Submit Application</Text>
            </View>
          )}
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
    padding: Spacing.md,
    paddingBottom: Spacing.xxl,
    gap: Spacing.md,
  },
  backButton: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    paddingVertical: 6,
  },
  backText: {
    fontSize: 13,
    color: Colors.text,
    fontWeight: "600",
  },
  header: {
    alignItems: "center",
    marginVertical: Spacing.sm,
  },
  iconCircle: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: Colors.secondary,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: Spacing.xs,
  },
  title: {
    fontSize: 20,
    fontWeight: "800",
    color: Colors.text,
    textAlign: "center",
  },
  subtitle: {
    fontSize: 12,
    color: Colors.muted,
    textAlign: "center",
    marginTop: 4,
    paddingHorizontal: Spacing.md,
    lineHeight: 18,
  },
  formCard: {
    backgroundColor: Colors.surface,
    padding: Spacing.md,
    borderRadius: BorderRadius.xl,
    borderWidth: 1,
    borderColor: Colors.border,
    gap: Spacing.sm,
  },
  formGroup: {
    gap: 4,
  },
  row: {
    flexDirection: "row",
    gap: Spacing.sm,
  },
  label: {
    fontSize: 12,
    fontWeight: "700",
    color: Colors.text,
  },
  input: {
    backgroundColor: Colors.background,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: BorderRadius.md,
    paddingHorizontal: Spacing.sm,
    paddingVertical: 10,
    fontSize: 13,
    color: Colors.text,
  },
  textArea: {
    minHeight: 90,
  },
  noteBox: {
    backgroundColor: "#FEF3C7",
    padding: Spacing.sm,
    borderRadius: BorderRadius.md,
    borderWidth: 1,
    borderColor: "#FCD34D",
    marginTop: 4,
  },
  noteTitle: {
    fontSize: 11,
    fontWeight: "700",
    color: "#92400E",
  },
  noteBody: {
    fontSize: 11,
    color: "#78350F",
    lineHeight: 16,
    marginTop: 2,
  },
  submitButton: {
    backgroundColor: Colors.primary,
    paddingVertical: 14,
    borderRadius: BorderRadius.lg,
    justifyContent: "center",
    alignItems: "center",
    marginTop: Spacing.xs,
  },
  submitBtnRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  submitButtonText: {
    color: Colors.surface,
    fontSize: 14,
    fontWeight: "800",
  },
});

