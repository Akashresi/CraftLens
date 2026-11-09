import React, { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from "react-native";
import { useRouter } from "expo-router";
import { Colors, Spacing, Typography, BorderRadius } from "../../src/constants/theme";
import { useAuthStore } from "../../src/store/authStore";
import {
  User,
  Sparkles,
  Clock,
  CheckCircle2,
  XCircle,
  ChevronRight,
  LogOut,
  Globe,
  Briefcase,
  ShieldCheck,
  RefreshCw,
} from "lucide-react-native";

interface ApplicationStatusData {
  id: string;
  status: "PENDING" | "APPROVED" | "REJECTED";
  craft_specialization: string;
  experience_years: number;
  city: string;
  state: string;
  reviewer_notes: string | null;
  created_at: string;
  reviewed_at: string | null;
}

export default function BuyerProfileScreen() {
  const router = useRouter();
  const { user, token, setAuth, logout } = useAuthStore();
  const [application, setApplication] = useState<ApplicationStatusData | null>(null);
  const [loadingApp, setLoadingApp] = useState(false);
  const [refreshingRole, setRefreshingRole] = useState(false);

  const fetchApplicationStatus = useCallback(async () => {
    if (!token) return;
    setLoadingApp(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/artisan-applications/me", {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });
      if (res.ok) {
        const json = await res.json();
        if (json.success && json.data) {
          setApplication(json.data);
        } else {
          setApplication(null);
        }
      }
    } catch (err) {
      // Offline fallback or silent fail
    } finally {
      setLoadingApp(false);
    }
  }, [token]);

  useEffect(() => {
    fetchApplicationStatus();
  }, [fetchApplicationStatus]);

  // Refresh profile to pick up approved Artisan role
  const handleCheckRoleApproval = async () => {
    if (!token) return;
    setRefreshingRole(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/auth/me", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (res.ok && data.success) {
        const latestRole = data.data.roles[0]?.code || "RETAIL_BUYER";
        setAuth(
          {
            id: data.data.id,
            email: data.data.email,
            full_name: data.data.full_name,
            phone: data.data.phone,
            preferred_language: data.data.preferred_language,
            is_verified: data.data.is_verified,
            role: latestRole,
          },
          token
        );

        if (latestRole === "ARTISAN") {
          Alert.alert(
            "Artisan Status Verified!",
            "Your artisan application has been approved by the admin. Redirecting to Artisan Studio workspace.",
            [{ text: "Open Studio", onPress: () => router.replace("/(tabs)") }]
          );
        } else {
          Alert.alert(
            "Application Under Review",
            "Your application is currently pending admin review. Please check back shortly."
          );
        }
      }
    } catch (err) {
      Alert.alert("Network Error", "Could not refresh profile from server.");
    } finally {
      setRefreshingRole(false);
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
          router.replace("/login");
        },
      },
    ]);
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Buyer Header Info */}
      <View style={styles.profileCard}>
        <View style={styles.avatar}>
          <User color={Colors.surface} size={30} />
        </View>
        <View style={styles.profileDetails}>
          <Text style={styles.userName}>{user?.full_name || "CraftLens Buyer"}</Text>
          <Text style={styles.userEmail}>{user?.email || "buyer@craftlens.org"}</Text>
          <View style={styles.roleBadgeContainer}>
            <Text style={styles.roleBadgeText}>
              {user?.role === "WHOLESALE_BUYER" ? "WHOLESALE BUYER" : "RETAIL BUYER"}
            </Text>
          </View>
        </View>
      </View>

      {/* Become an Artisan / Application Status Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Artisan Program</Text>

        {loadingApp ? (
          <View style={styles.loadingBox}>
            <ActivityIndicator color={Colors.primary} />
            <Text style={styles.loadingText}>Checking artisan application status...</Text>
          </View>
        ) : !application ? (
          /* Option: Become an Artisan */
          <View style={styles.artisanCtaCard}>
            <View style={styles.ctaHeader}>
              <View style={styles.sparkleIcon}>
                <Sparkles color={Colors.surface} size={20} />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={styles.ctaTitle}>Become an Artisan</Text>
                <Text style={styles.ctaSubtitle}>
                  Are you a traditional craftsperson, weaver, or artisan?
                </Text>
              </View>
            </View>

            <Text style={styles.ctaBody}>
              Join the CraftLens Artisan Network to access AI Studio photo processing, voice-to-catalog generation in Indian regional languages, fair wage pricing calculator, and reach buyers worldwide.
            </Text>

            <TouchableOpacity
              style={styles.applyButton}
              activeOpacity={0.85}
              onPress={() => router.push("/(buyer-tabs)/apply-artisan")}
            >
              <Text style={styles.applyButtonText}>Apply to Become an Artisan</Text>
              <ChevronRight color={Colors.surface} size={16} />
            </TouchableOpacity>
          </View>
        ) : application.status === "PENDING" ? (
          /* Application Status: PENDING */
          <View style={styles.statusCardPending}>
            <View style={styles.statusHeaderRow}>
              <View style={styles.statusIndicatorPending}>
                <Clock color="#B45309" size={16} />
                <Text style={styles.statusTitlePending}>Application Pending Review</Text>
              </View>
              <TouchableOpacity
                onPress={fetchApplicationStatus}
                hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
              >
                <RefreshCw color="#B45309" size={14} />
              </TouchableOpacity>
            </View>

            <Text style={styles.statusDescription}>
              Your application to register as a traditional artisan is under review by our governance team. We audit craft provenance and credentials before approving studio access.
            </Text>

            <View style={styles.appSummaryBox}>
              <View style={styles.summaryRow}>
                <Text style={styles.summaryLabel}>Specialization:</Text>
                <Text style={styles.summaryValue}>{application.craft_specialization}</Text>
              </View>
              <View style={styles.summaryRow}>
                <Text style={styles.summaryLabel}>Experience:</Text>
                <Text style={styles.summaryValue}>{application.experience_years} Years</Text>
              </View>
              <View style={styles.summaryRow}>
                <Text style={styles.summaryLabel}>Location:</Text>
                <Text style={styles.summaryValue}>{application.city}, {application.state}</Text>
              </View>
              <View style={styles.summaryRow}>
                <Text style={styles.summaryLabel}>Submitted on:</Text>
                <Text style={styles.summaryValue}>
                  {new Date(application.created_at).toLocaleDateString()}
                </Text>
              </View>
            </View>

            <TouchableOpacity
              style={styles.checkStatusBtn}
              onPress={handleCheckRoleApproval}
              disabled={refreshingRole}
            >
              {refreshingRole ? (
                <ActivityIndicator color={Colors.surface} size="small" />
              ) : (
                <Text style={styles.checkStatusBtnText}>Check Approval Status</Text>
              )}
            </TouchableOpacity>
          </View>
        ) : application.status === "APPROVED" ? (
          /* Application Status: APPROVED */
          <View style={styles.statusCardApproved}>
            <View style={styles.statusIndicatorApproved}>
              <CheckCircle2 color="#047857" size={18} />
              <Text style={styles.statusTitleApproved}>Artisan Application Approved!</Text>
            </View>

            <Text style={styles.statusDescriptionApproved}>
              Congratulations! Your craft application has been approved by the platform administrators. Your role is upgraded to ARTISAN.
            </Text>

            {application.reviewer_notes && (
              <Text style={styles.reviewerNoteText}>
                Reviewer Note: &ldquo;{application.reviewer_notes}&rdquo;
              </Text>
            )}

            <TouchableOpacity
              style={styles.switchStudioBtn}
              onPress={handleCheckRoleApproval}
              disabled={refreshingRole}
            >
              {refreshingRole ? (
                <ActivityIndicator color={Colors.surface} size="small" />
              ) : (
                <Text style={styles.switchStudioBtnText}>Launch Artisan Studio</Text>
              )}
            </TouchableOpacity>
          </View>
        ) : (
          /* Application Status: REJECTED */
          <View style={styles.statusCardRejected}>
            <View style={styles.statusIndicatorRejected}>
              <XCircle color="#B91C1C" size={18} />
              <Text style={styles.statusTitleRejected}>Application Not Approved</Text>
            </View>

            <Text style={styles.statusDescriptionRejected}>
              Your previous artisan application was declined. You retain your Buyer account and can submit a new application with verified craft details.
            </Text>

            {application.reviewer_notes && (
              <View style={styles.rejectionReasonBox}>
                <Text style={styles.rejectionReasonLabel}>Feedback:</Text>
                <Text style={styles.rejectionReasonText}>{application.reviewer_notes}</Text>
              </View>
            )}

            <TouchableOpacity
              style={styles.reapplyBtn}
              onPress={() => router.push("/(buyer-tabs)/apply-artisan")}
            >
              <Text style={styles.reapplyBtnText}>Submit New Application</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>

      {/* Account Settings */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Preferences & Account</Text>
        <View style={styles.settingsMenu}>
          <TouchableOpacity
            style={styles.menuItem}
            onPress={() => router.push("/language")}
          >
            <View style={styles.menuLeft}>
              <Globe color={Colors.muted} size={18} />
              <Text style={styles.menuText}>App Language / மொழி</Text>
            </View>
            <ChevronRight color={Colors.muted} size={18} />
          </TouchableOpacity>

          <TouchableOpacity style={styles.menuItem} onPress={handleLogout}>
            <View style={styles.menuLeft}>
              <LogOut color={Colors.error} size={18} />
              <Text style={[styles.menuText, { color: Colors.error }]}>Sign Out</Text>
            </View>
          </TouchableOpacity>
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
    padding: Spacing.md,
    paddingBottom: Spacing.xxl,
    gap: Spacing.lg,
  },
  profileCard: {
    flexDirection: "row",
    backgroundColor: Colors.surface,
    padding: Spacing.md,
    borderRadius: BorderRadius.xl,
    borderWidth: 1,
    borderColor: Colors.border,
    alignItems: "center",
    gap: Spacing.md,
  },
  avatar: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: Colors.primary,
    justifyContent: "center",
    alignItems: "center",
  },
  profileDetails: {
    flex: 1,
  },
  userName: {
    fontSize: 16,
    fontWeight: "800",
    color: Colors.text,
  },
  userEmail: {
    fontSize: 12,
    color: Colors.muted,
    marginTop: 2,
  },
  roleBadgeContainer: {
    backgroundColor: Colors.background,
    borderWidth: 1,
    borderColor: Colors.border,
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: BorderRadius.sm,
    alignSelf: "flex-start",
    marginTop: 6,
  },
  roleBadgeText: {
    fontSize: 9,
    fontWeight: "800",
    color: Colors.primary,
    letterSpacing: 0.5,
  },
  section: {
    gap: Spacing.xs,
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: "700",
    color: Colors.muted,
    textTransform: "uppercase",
    letterSpacing: 0.5,
    marginBottom: 4,
  },
  loadingBox: {
    backgroundColor: Colors.surface,
    padding: Spacing.lg,
    borderRadius: BorderRadius.lg,
    alignItems: "center",
    gap: 8,
  },
  loadingText: {
    fontSize: 12,
    color: Colors.muted,
  },
  artisanCtaCard: {
    backgroundColor: Colors.surface,
    borderWidth: 1.5,
    borderColor: Colors.secondary,
    borderRadius: BorderRadius.xl,
    padding: Spacing.md,
    gap: Spacing.sm,
  },
  ctaHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: Spacing.sm,
  },
  sparkleIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: Colors.secondary,
    justifyContent: "center",
    alignItems: "center",
  },
  ctaTitle: {
    fontSize: 15,
    fontWeight: "800",
    color: Colors.text,
  },
  ctaSubtitle: {
    fontSize: 11,
    color: Colors.muted,
  },
  ctaBody: {
    fontSize: 12,
    color: Colors.text,
    lineHeight: 18,
  },
  applyButton: {
    flexDirection: "row",
    backgroundColor: Colors.secondary,
    paddingVertical: 10,
    paddingHorizontal: Spacing.md,
    borderRadius: BorderRadius.lg,
    justifyContent: "center",
    alignItems: "center",
    gap: 6,
    marginTop: 4,
  },
  applyButtonText: {
    color: Colors.surface,
    fontSize: 13,
    fontWeight: "700",
  },
  statusCardPending: {
    backgroundColor: "#FEF3C7",
    borderWidth: 1,
    borderColor: "#FCD34D",
    borderRadius: BorderRadius.xl,
    padding: Spacing.md,
    gap: Spacing.xs,
  },
  statusHeaderRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  statusIndicatorPending: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  statusTitlePending: {
    fontSize: 14,
    fontWeight: "800",
    color: "#92400E",
  },
  statusDescription: {
    fontSize: 11,
    color: "#78350F",
    lineHeight: 16,
    marginVertical: 4,
  },
  appSummaryBox: {
    backgroundColor: "rgba(255,255,255,0.7)",
    borderRadius: BorderRadius.md,
    padding: Spacing.sm,
    gap: 4,
    marginVertical: 4,
  },
  summaryRow: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  summaryLabel: {
    fontSize: 11,
    color: "#92400E",
    fontWeight: "600",
  },
  summaryValue: {
    fontSize: 11,
    fontWeight: "700",
    color: "#78350F",
  },
  checkStatusBtn: {
    backgroundColor: "#D97706",
    paddingVertical: 10,
    borderRadius: BorderRadius.lg,
    alignItems: "center",
    marginTop: 6,
  },
  checkStatusBtnText: {
    color: "#FFFFFF",
    fontSize: 12,
    fontWeight: "700",
  },
  statusCardApproved: {
    backgroundColor: "#D1FAE5",
    borderWidth: 1,
    borderColor: "#6EE7B7",
    borderRadius: BorderRadius.xl,
    padding: Spacing.md,
    gap: Spacing.xs,
  },
  statusIndicatorApproved: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  statusTitleApproved: {
    fontSize: 14,
    fontWeight: "800",
    color: "#065F46",
  },
  statusDescriptionApproved: {
    fontSize: 11,
    color: "#047857",
    lineHeight: 16,
    marginVertical: 4,
  },
  reviewerNoteText: {
    fontSize: 11,
    fontStyle: "italic",
    color: "#065F46",
    backgroundColor: "rgba(255,255,255,0.6)",
    padding: 6,
    borderRadius: 6,
  },
  switchStudioBtn: {
    backgroundColor: "#059669",
    paddingVertical: 10,
    borderRadius: BorderRadius.lg,
    alignItems: "center",
    marginTop: 6,
  },
  switchStudioBtnText: {
    color: "#FFFFFF",
    fontSize: 12,
    fontWeight: "700",
  },
  statusCardRejected: {
    backgroundColor: "#FEE2E2",
    borderWidth: 1,
    borderColor: "#FCA5A5",
    borderRadius: BorderRadius.xl,
    padding: Spacing.md,
    gap: Spacing.xs,
  },
  statusIndicatorRejected: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  statusTitleRejected: {
    fontSize: 14,
    fontWeight: "800",
    color: "#991B1B",
  },
  statusDescriptionRejected: {
    fontSize: 11,
    color: "#7F1D1D",
    lineHeight: 16,
    marginVertical: 4,
  },
  rejectionReasonBox: {
    backgroundColor: "rgba(255,255,255,0.7)",
    padding: 6,
    borderRadius: 6,
    marginVertical: 4,
  },
  rejectionReasonLabel: {
    fontSize: 10,
    fontWeight: "700",
    color: "#991B1B",
  },
  rejectionReasonText: {
    fontSize: 11,
    color: "#7F1D1D",
  },
  reapplyBtn: {
    backgroundColor: "#DC2626",
    paddingVertical: 10,
    borderRadius: BorderRadius.lg,
    alignItems: "center",
    marginTop: 6,
  },
  reapplyBtnText: {
    color: "#FFFFFF",
    fontSize: 12,
    fontWeight: "700",
  },
  settingsMenu: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.xl,
    borderWidth: 1,
    borderColor: Colors.border,
    overflow: "hidden",
  },
  menuItem: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: Spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  menuLeft: {
    flexDirection: "row",
    alignItems: "center",
    gap: Spacing.sm,
  },
  menuText: {
    fontSize: 13,
    fontWeight: "600",
    color: Colors.text,
  },
});

