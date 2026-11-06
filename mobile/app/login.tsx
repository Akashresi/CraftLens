import React, { useState } from "react";
import { View, Text, StyleSheet, TextInput, TouchableOpacity, Alert, ActivityIndicator } from "react-native";
import { useRouter } from "expo-router";
import { Colors, Spacing, Typography, BorderRadius } from "../src/constants/theme";
import { useAuthStore } from "../src/store/authStore";

export default function MobileLoginScreen() {
  const router = useRouter();
  const { setAuth } = useAuthStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert("Input Required", "Please enter your email and password.");
      return;
    }

    setLoading(true);
    try {
      const formBody = new URLSearchParams();
      formBody.append("username", email);
      formBody.append("password", password);

      const res = await fetch("http://127.0.0.1:8000/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formBody.toString(),
      });

      const data = await res.json();
      if (!res.ok) {
        Alert.alert("Authentication Failed", data.detail || "Invalid credentials.");
        setLoading(false);
        return;
      }

      // Fetch user profile
      const profileRes = await fetch("http://127.0.0.1:8000/api/v1/auth/me", {
        headers: { Authorization: `Bearer ${data.access_token}` },
      });
      const profileData = await profileRes.json();

      setAuth(
        {
          id: profileData.data.id,
          email: profileData.data.email,
          full_name: profileData.data.full_name,
          preferred_language: profileData.data.preferred_language,
          is_verified: profileData.data.is_verified,
          role: profileData.data.roles[0]?.code || "ARTISAN",
        },
        data.access_token
      );

      router.replace("/(tabs)/home");
    } catch (err: any) {
      Alert.alert("Network Error", "Unable to connect to CraftLens backend server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Sign In to Studio</Text>
      <Text style={styles.subtitle}>Enter your email or phone to access your artisan workspace</Text>

      <View style={styles.formGroup}>
        <Text style={styles.label}>Email Address</Text>
        <TextInput
          style={styles.input}
          placeholder="artisan@craftlens.org"
          keyboardType="email-address"
          autoCapitalize="none"
          value={email}
          onChangeText={setEmail}
        />
      </View>

      <View style={styles.formGroup}>
        <Text style={styles.label}>Password</Text>
        <TextInput
          style={styles.input}
          placeholder="••••••••"
          secureTextEntry
          value={password}
          onChangeText={setPassword}
        />
      </View>

      <TouchableOpacity
        style={styles.loginButton}
        activeOpacity={0.8}
        onPress={handleLogin}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color={Colors.surface} />
        ) : (
          <Text style={styles.loginButtonText}>Sign In</Text>
        )}
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.switchButton}
        onPress={() => router.push("/register")}
      >
        <Text style={styles.switchButtonText}>
          New to CraftLens? <Text style={{ color: Colors.secondary, fontWeight: "600" }}>Register here</Text>
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
    padding: Spacing.lg,
    justifyContent: "center",
  },
  title: {
    ...Typography.h1,
    color: Colors.text,
  },
  subtitle: {
    ...Typography.body,
    color: Colors.muted,
    marginBottom: Spacing.xl,
  },
  formGroup: {
    marginBottom: Spacing.md,
  },
  label: {
    ...Typography.small,
    fontWeight: "600",
    color: Colors.text,
    marginBottom: Spacing.xs,
    textTransform: "uppercase",
  },
  input: {
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: BorderRadius.md,
    paddingHorizontal: Spacing.base,
    paddingVertical: Spacing.md,
    ...Typography.body,
    color: Colors.text,
  },
  loginButton: {
    backgroundColor: Colors.primary,
    paddingVertical: Spacing.base,
    borderRadius: BorderRadius.md,
    alignItems: "center",
    marginTop: Spacing.md,
  },
  loginButtonText: {
    ...Typography.bodyBold,
    color: Colors.surface,
  },
  switchButton: {
    alignItems: "center",
    marginTop: Spacing.lg,
  },
  switchButtonText: {
    ...Typography.body,
    color: Colors.muted,
  },
});

