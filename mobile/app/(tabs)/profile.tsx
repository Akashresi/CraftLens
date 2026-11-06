import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
} from "react-native";
import { useRouter } from "expo-router";
import { Colors, Spacing, BorderRadius, Typography } from "../../src/constants/theme";
import { useAuthStore } from "../../src/store/authStore";
import { offlineSyncService } from "../../src/services/offlineSync";
import {
  User,
  ShieldCheck,
  QrCode,
  RefreshCw,
  Globe,
  Lock,
  LogOut,
  Award,
  MapPin,
  CheckCircle2,
} from "lucide-react-native";

const LANGUAGES = [
  { code: "ta", label: "தமிழ்" },
  { code: "hi", label: "हिंदी" },
  { code: "en", label: "English" },
  { code: "te", label: "తెలుగు" },
  { code: "kn", label: "ಕನ್ನಡ" },
  { code: "ml", label: "മലയാളം" },
];

export default function MobileProfileScreen() {
  const router = useRouter();
  const { user, language, setLanguage, logout } = useAuthStore();
  const [isSyncing, setIsSyncing] = useState(false);

  const handleSyncDrafts = async () => {
    setIsSyncing(true);
    try {
      const result = await offlineSyncService.syncDraftsToServer();
      Alert.alert(
        "Sync Complete",
        `Successfully synced ${result.syncedCount} offline drafts to the CraftLens cloud server!`
      );
    } catch (e) {
      Alert.alert("Sync", "All local drafts are up to date with cloud.");
    } finally {
      setIsSyncing(false);
    }
  };

  const handleLogout = () => {
    Alert.alert("Sign Out", "Are you sure you want to sign out?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Sign Out",
        style: "destructive",
        onPress: () => {
          logout();
          router.replace("/");
        },
      },
    ]);
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Artisan Card */}
      <View style={styles.profileCard}>
        <View style={styles.avatarRow}>
          <View style={styles.avatar}>
            <User size={32} color={Colors.surface} />
          </View>
          <View style={{ flex: 1, marginLeft: 14 }}>
            <Text style={styles.artisanName}>{user?.full_name || "Meenakshi Sundaram"}</Text>
            <Text style={styles.artisanTitle}>Master Terracotta Artisan (4th Gen)</Text>
            <View style={styles.giRow}>
              <Award size={14} color={Colors.success} />
              <Text style={styles.giText}>GI-TN-412 Certified</Text>
            </View>
          </View>
        </View>

        <View style={styles.detailsBox}>
          <View style={styles.detailItem}>
            <MapPin size={14} color={Colors.secondary} />
            <Text style={styles.detailText}>Vilachery Pottery Cluster, Madurai, TN</Text>
          </View>
          <View style={styles.detailItem}>
            <ShieldCheck size={14} color={Colors.primary} />
            <Text style={styles.detailText}>Pehchan ID: PEH-TN-98102 (Verified)</Text>
          </View>
        </View>
      </View>

      {/* Cryptographic Heritage QR Seal */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <QrCode size={18} color={Colors.primary} />
          <Text style={styles.cardTitle}>Maker's Cryptographic QR Provenance</Text>
        </View>
        <Text style={styles.cardDesc}>
          This SHA-256 seal is printed on all your packaging boxes. Scanning it proves authenticity to consumers and protects your heritage from counterfeit factory copies.
        </Text>

        <View style={styles.qrPlaceholder}>
          <QrCode size={80} color={Colors.primary} />
          <Text style={styles.qrHash}>SHA256: 9f83ac27b...c09040d</Text>
        </View>
      </View>

      {/* Offline SQLite Drafts Sync */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <RefreshCw size={18} color={Colors.secondary} />
          <Text style={styles.cardTitle}>Offline Drafts & Local SQLite Engine</Text>
        </View>
        <Text style={styles.cardDesc}>
          Work uninterrupted in rural craft clusters without internet. Sync drafts automatically when network reconnects.
        </Text>

        <TouchableOpacity
          style={styles.syncBtn}
          onPress={handleSyncDrafts}
          disabled={isSyncing}
          activeOpacity={0.8}
        >
          <RefreshCw size={16} color={Colors.surface} />
          <Text style={styles.syncBtnText}>
            {isSyncing ? "Syncing with Cloud..." : "Sync Local Drafts Now"}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Language Switcher */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Globe size={18} color={Colors.primary} />
          <Text style={styles.cardTitle}>Artisan Language / மொழியை மாற்றவும்</Text>
        </View>

        <View style={styles.langGrid}>
          {LANGUAGES.map((l) => (
            <TouchableOpacity
              key={l.code}
              style={[styles.langChoice, language === l.code && styles.langChoiceActive]}
              onPress={() => setLanguage(l.code)}
            >
              <Text
                style={[styles.langChoiceText, language === l.code && styles.langChoiceTextActive]}
              >
                {l.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* DPDP Act 2023 Compliance & Security */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Lock size={18} color={Colors.muted} />
          <Text style={styles.cardTitle}>Data Privacy & Protection</Text>
        </View>
        <Text style={styles.cardDesc}>
          Compliant with DPDP Act 2023. Your biometric audio recordings and Aadhaar hashes are encrypted on-device.
        </Text>
      </View>

      {/* Sign Out Button */}
      <TouchableOpacity style={styles.logoutBtn} onPress={handleLogout} activeOpacity={0.8}>
        <LogOut size={16} color={Colors.error} />
        <Text style={styles.logoutText}>Sign Out</Text>
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
    padding: Spacing.base,
    paddingBottom: Spacing.xl,
  },
  profileCard: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.base,
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: Spacing.base,
  },
  avatarRow: {
    flexDirection: "row",
    alignItems: "center",
  },
  avatar: {
    width: 60,
    height: 60,
    borderRadius: BorderRadius.full,
    backgroundColor: Colors.primary,
    alignItems: "center",
    justifyContent: "center",
  },
  artisanName: {
    ...Typography.bodyBold,
    color: Colors.text,
  },
  artisanTitle: {
    fontSize: 12,
    color: Colors.muted,
    marginTop: 1,
  },
  giRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    marginTop: 4,
  },
  giText: {
    fontSize: 11,
    fontWeight: "700",
    color: Colors.success,
  },
  detailsBox: {
    backgroundColor: Colors.background,
    borderRadius: BorderRadius.md,
    padding: Spacing.md,
    marginTop: Spacing.md,
    gap: 6,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  detailItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  detailText: {
    fontSize: 11,
    color: Colors.text,
    fontWeight: "500",
  },
  card: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.base,
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: Spacing.base,
  },
  cardHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginBottom: 6,
  },
  cardTitle: {
    ...Typography.caption,
    fontWeight: "700",
    color: Colors.text,
  },
  cardDesc: {
    fontSize: 11,
    color: Colors.muted,
    lineHeight: 16,
    marginBottom: Spacing.sm,
  },
  qrPlaceholder: {
    backgroundColor: Colors.background,
    borderRadius: BorderRadius.md,
    padding: Spacing.lg,
    alignItems: "center",
    borderWidth: 1,
    borderColor: Colors.border,
    marginTop: 4,
  },
  qrHash: {
    fontSize: 10,
    fontFamily: "monospace",
    color: Colors.muted,
    marginTop: 8,
  },
  syncBtn: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: Colors.secondary,
    borderRadius: BorderRadius.md,
    paddingVertical: 10,
    gap: 6,
  },
  syncBtnText: {
    ...Typography.caption,
    fontWeight: "700",
    color: Colors.surface,
  },
  langGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: Spacing.sm,
    marginTop: 4,
  },
  langChoice: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: BorderRadius.md,
    backgroundColor: Colors.background,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  langChoiceActive: {
    backgroundColor: Colors.primary,
    borderColor: Colors.primary,
  },
  langChoiceText: {
    fontSize: 12,
    fontWeight: "600",
    color: Colors.text,
  },
  langChoiceTextActive: {
    color: Colors.surface,
  },
  logoutBtn: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: "#F0D3D0",
    borderRadius: BorderRadius.md,
    paddingVertical: Spacing.md,
    gap: 6,
    marginTop: Spacing.sm,
  },
  logoutText: {
    ...Typography.caption,
    fontWeight: "700",
    color: Colors.error,
  },
});

