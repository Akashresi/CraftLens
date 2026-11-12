import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  ScrollView,
  ActivityIndicator,
  Alert,
} from "react-native";
import { useRouter } from "expo-router";
import * as ImagePicker from "expo-image-picker";
import { Colors, Spacing, BorderRadius, Typography, TouchTargets } from "../../src/constants/theme";
import { API_BASE_URL, apiFetch } from "../../src/services/apiClient";
import { useAuthStore } from "../../src/store/authStore";
import { telemetry } from "../../src/services/telemetry";
import {
  Camera,
  Image as ImageIcon,
  Sparkles,
  CheckCircle2,
  RefreshCw,
  Sun,
  Layers,
  ArrowRight,
  ShieldCheck,
} from "lucide-react-native";

export default function MobileStudioScreen() {
  const router = useRouter();
  const { token } = useAuthStore();

  // State
  const [selectedImage, setSelectedImage] = useState<string | null>(
    "https://images.unsplash.com/photo-1578749556568-bc2c40e68b61?auto=format&fit=crop&w=600&q=80"
  );
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeStep, setActiveStep] = useState<string | null>(null);
  const [studioResult, setStudioResult] = useState<{
    originalUrl: string;
    studioUrl: string;
    isSharp: boolean;
    blurScore: number;
    bgRemoved: boolean;
    lightingCorrected: boolean;
    shadowAdded: boolean;
  } | null>({
    originalUrl: "https://images.unsplash.com/photo-1578749556568-bc2c40e68b61?auto=format&fit=crop&w=600&q=80",
    studioUrl: "https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?auto=format&fit=crop&w=600&q=80",
    isSharp: true,
    blurScore: 184.2,
    bgRemoved: true,
    lightingCorrected: true,
    shadowAdded: true,
  });

  const [viewMode, setViewMode] = useState<"studio" | "original">("studio");

  const pickCraftImage = async (fromCamera: boolean) => {
    const pickerFn = fromCamera
      ? ImagePicker.launchCameraAsync
      : ImagePicker.launchImageLibraryAsync;
    try {
      const res = await pickerFn({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        quality: 0.85,
      });
      if (!res.canceled && res.assets?.[0]?.uri) {
        setSelectedImage(res.assets[0].uri);
      }
    } catch (err) {
      telemetry.captureCrash(err, { screen: "studio" });
      Alert.alert("Camera Unavailable", "Using preview photo; pick an image on a physical device.");
    }
  };

  const runStudioPipeline = async () => {
    if (!selectedImage || !token) {
      Alert.alert("Sign In Required", "Please sign in as an Artisan and choose a craft photo first.");
      return;
    }
    setIsProcessing(true);
    setActiveStep("Uploading photo to AI Studio queue...");
    try {
      const formData = new FormData();
      formData.append("lifestyle_theme", "wood");
      formData.append("file", {
        uri: selectedImage,
        name: "craft.jpg",
        type: "image/jpeg",
      } as unknown as Blob);

      const enqueueRes = await fetch(`${API_BASE_URL}/studio/process-async`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      const enqueueJson = await enqueueRes.json().catch(() => null);
      if (!enqueueRes.ok || !enqueueJson?.data?.job_id) {
        Alert.alert("Upload Failed", enqueueJson?.detail || "Could not queue studio photo.");
        return;
      }

      const jobId = enqueueJson.data.job_id as string;
      setActiveStep("Removing background & balancing lighting...");
      for (let i = 0; i < 20; i++) {
        await new Promise((r) => setTimeout(r, 500));
        const poll = await apiFetch<{
          status: string;
          result?: {
            original_url: string;
            white_bg_url: string;
            quality_score: number;
          };
          error_message?: string;
        }>(`/studio/jobs/${jobId}`, { token });
        if (poll.ok && poll.data?.status === "COMPLETED" && poll.data.result) {
          setStudioResult({
            originalUrl: poll.data.result.original_url,
            studioUrl: poll.data.result.white_bg_url,
            isSharp: poll.data.result.quality_score >= 6.0,
            blurScore: poll.data.result.quality_score * 25,
            bgRemoved: true,
            lightingCorrected: true,
            shadowAdded: true,
          });
          telemetry.trackEvent("studio_enhance_success");
          Alert.alert("Success", "Studio enhancement completed!");
          return;
        }
        if (poll.ok && poll.data?.status === "FAILED") {
          Alert.alert("Studio Error", poll.data.error_message || "Enhancement failed.");
          return;
        }
      }
      Alert.alert("Still Processing", "Your photo is queued and will update shortly.");
    } catch (err) {
      telemetry.captureCrash(err, { screen: "studio" });
      Alert.alert("Network Unavailable", "Connect to the internet to run AI Studio enhancement.");
    } finally {
      setIsProcessing(false);
      setActiveStep(null);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Title */}
      <View style={styles.header}>
        <Text style={styles.title}>AI Product Studio</Text>
        <Text style={styles.subtitle}>
          Create studio-grade catalog photos without expensive equipment.
        </Text>
      </View>

      {/* Main Image Viewport */}
      <View style={styles.viewportContainer}>
        {selectedImage ? (
          <View style={styles.imageWrapper}>
            <Image
              source={{
                uri:
                  viewMode === "studio" && studioResult?.studioUrl
                    ? studioResult.studioUrl
                    : selectedImage,
              }}
              style={styles.previewImage}
              resizeMode="cover"
            />

            {/* Quality Score Badge */}
            {studioResult && (
              <View style={styles.qualityBadge}>
                <CheckCircle2 size={12} color={Colors.success} />
                <Text style={styles.qualityText}>
                  Sharpness: {Math.round(studioResult.blurScore)} (Good)
                </Text>
              </View>
            )}

            {/* Toggle Original / Studio */}
            {studioResult && (
              <View style={styles.toggleBar}>
                <TouchableOpacity
                  style={[styles.toggleBtn, viewMode === "original" && styles.toggleBtnActive]}
                  onPress={() => setViewMode("original")}
                >
                  <Text
                    style={[
                      styles.toggleText,
                      viewMode === "original" && styles.toggleTextActive,
                    ]}
                  >
                    Original
                  </Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.toggleBtn, viewMode === "studio" && styles.toggleBtnActive]}
                  onPress={() => setViewMode("studio")}
                >
                  <Text
                    style={[styles.toggleText, viewMode === "studio" && styles.toggleTextActive]}
                  >
                    Studio AI
                  </Text>
                </TouchableOpacity>
              </View>
            )}
          </View>
        ) : (
          <View style={styles.placeholderBox}>
            <Camera size={40} color={Colors.muted} />
            <Text style={styles.placeholderText}>No craft photo selected</Text>
          </View>
        )}
      </View>

      {/* Image Capture & Pick Buttons (>= 52dp accessible targets) */}
      <View style={styles.actionRow}>
        <TouchableOpacity
          style={[styles.pickerBtn, { minHeight: TouchTargets.minHeight }]}
          accessibilityRole="button"
          accessibilityLabel="Take camera photo of craft item"
          onPress={() => pickCraftImage(true)}
        >
          <Camera size={20} color={Colors.text} />
          <Text style={styles.pickerBtnText}>Take Photo</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.pickerBtn, { minHeight: TouchTargets.minHeight }]}
          accessibilityRole="button"
          accessibilityLabel="Choose craft photo from phone gallery"
          onPress={() => pickCraftImage(false)}
        >
          <ImageIcon size={20} color={Colors.text} />
          <Text style={styles.pickerBtnText}>Gallery</Text>
        </TouchableOpacity>
      </View>

      {/* AI Process Trigger */}
      <TouchableOpacity
        style={[
          styles.enhanceBtn,
          { minHeight: TouchTargets.minHeight },
          isProcessing && styles.enhanceBtnDisabled,
        ]}
        accessibilityRole="button"
        accessibilityLabel="Enhance craft photo with AI background removal"
        onPress={runStudioPipeline}
        disabled={isProcessing}
        activeOpacity={0.8}
      >
        {isProcessing ? (
          <ActivityIndicator color={Colors.surface} size="small" />
        ) : (
          <Sparkles size={18} color={Colors.surface} />
        )}
        <Text style={styles.enhanceBtnText}>
          {isProcessing ? activeStep || "Processing..." : "Generate Studio Photo (1-Tap AI)"}
        </Text>
      </TouchableOpacity>

      {/* Studio Pipeline Features Overview */}
      <View style={styles.featuresCard}>
        <Text style={styles.featuresTitle}>Automated Studio Enhancements</Text>

        <View style={styles.featureItem}>
          <Layers size={16} color={Colors.primary} />
          <Text style={styles.featureLabel}>Background Removal & White Studio Floor</Text>
        </View>

        <View style={styles.featureItem}>
          <Sun size={16} color={Colors.secondary} />
          <Text style={styles.featureLabel}>Adaptive CLAHE Lighting Correction</Text>
        </View>

        <View style={styles.featureItem}>
          <ShieldCheck size={16} color={Colors.success} />
          <Text style={styles.featureLabel}>Authenticity Guarantee: Pattern & Form Preserved</Text>
        </View>
      </View>

      {/* Next Step: Voice Cataloging */}
      {studioResult && (
        <TouchableOpacity
          style={styles.nextStepBtn}
          onPress={() => router.push("/(tabs)/voice")}
          activeOpacity={0.8}
        >
          <Text style={styles.nextStepText}>Continue to Voice Cataloging</Text>
          <ArrowRight size={16} color={Colors.surface} />
        </TouchableOpacity>
      )}
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
  viewportContainer: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    overflow: "hidden",
    marginBottom: Spacing.md,
  },
  imageWrapper: {
    position: "relative",
    width: "100%",
    height: 320,
  },
  previewImage: {
    width: "100%",
    height: "100%",
  },
  qualityBadge: {
    position: "absolute",
    top: 10,
    left: 10,
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "rgba(255, 255, 255, 0.92)",
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: BorderRadius.sm,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  qualityText: {
    fontSize: 10,
    fontWeight: "600",
    color: Colors.text,
    marginLeft: 4,
  },
  toggleBar: {
    position: "absolute",
    bottom: 12,
    alignSelf: "center",
    flexDirection: "row",
    backgroundColor: "rgba(36, 43, 39, 0.8)",
    borderRadius: BorderRadius.full,
    padding: 3,
  },
  toggleBtn: {
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: BorderRadius.full,
  },
  toggleBtnActive: {
    backgroundColor: Colors.surface,
  },
  toggleText: {
    fontSize: 11,
    fontWeight: "600",
    color: "#E8E5DC",
  },
  toggleTextActive: {
    color: Colors.text,
  },
  placeholderBox: {
    height: 240,
    alignItems: "center",
    justifyContent: "center",
  },
  placeholderText: {
    ...Typography.caption,
    color: Colors.muted,
    marginTop: 8,
  },
  actionRow: {
    flexDirection: "row",
    gap: Spacing.md,
    marginBottom: Spacing.md,
  },
  pickerBtn: {
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
  pickerBtnText: {
    ...Typography.caption,
    fontWeight: "600",
    color: Colors.text,
  },
  enhanceBtn: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: Colors.primary,
    borderRadius: BorderRadius.md,
    paddingVertical: Spacing.md,
    gap: 8,
    marginBottom: Spacing.base,
  },
  enhanceBtnDisabled: {
    opacity: 0.7,
  },
  enhanceBtnText: {
    ...Typography.small,
    fontWeight: "700",
    color: Colors.surface,
  },
  featuresCard: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.base,
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: Spacing.base,
  },
  featuresTitle: {
    ...Typography.caption,
    fontWeight: "700",
    color: Colors.text,
    marginBottom: Spacing.sm,
  },
  featureItem: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 6,
    gap: 8,
  },
  featureLabel: {
    fontSize: 12,
    color: Colors.muted,
  },
  nextStepBtn: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: Colors.secondary,
    borderRadius: BorderRadius.md,
    paddingVertical: Spacing.md,
    gap: 6,
  },
  nextStepText: {
    ...Typography.small,
    fontWeight: "700",
    color: Colors.surface,
  },
});

