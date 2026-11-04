import React, { useState } from "react";
import { View, Text, StyleSheet, TextInput, TouchableOpacity, Alert, ActivityIndicator, ScrollView } from "react-native";
import { useRouter } from "expo-router";
import { Colors, Spacing, Typography, BorderRadius } from "../src/constants/theme";
import { useAuthStore } from "../src/store/authStore";

export default function MobileRegisterScreen() {
  const router = useRouter();
  const { language, setAuth } = useAuthStore();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    if (!fullName || !email || !password) {
      Alert.alert("Required Fields", "Please provide your name, email, and a password.");
      return;
    }

    setLoading(true);
    try {
      const registerRes = await fetch("http://127.0.0.1:8000/api/v1/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          full_name: fullName,
          email,
          phone,
          password,
          role_code: "ARTISAN",
          preferred_language: language || "ta",
        }),
      });

      const registerData = await registerRes.json();
      if (!registerRes.ok || !registerData.success) {
        Alert.alert("Registration Error", registerData.error || registerData.detail || "Could not register account.");
        setLoading(false);
        return;
      }

      // Automatically login
      const formBody = new URLSearchParams();
      formBody.append("username", email);
      formBody.append("password", password);

      const loginRes = await fetch("http://127.0.0.1:8000/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formBody.toString(),
      });
      const loginData = await loginRes.json();

      setAuth(
        {
          id: registerData.data.id,
          email: registerData.data.email,
          full_name: registerData.data.full_name,
          preferred_language: registerData.data.preferred_language,
          is_verified: false,
          role: "ARTISAN",
        },
        loginData.access_token
      );

      router.replace("/onboarding");
    } catch (err: any) {
      Alert.alert("Connection Failed", "Unable to reach server. Please check internet connection.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Artisan Registration</Text>
      <Text style={styles.subtitle}>Join India&apos;s digital craft network</Text>

      <View style={styles.formGroup}>
        <Text style={styles.label}>Full Name / பெயர்</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g. Meenakshi Ammal"
          value={fullName}
          onChangeText={setFullName}
        />
      </View>

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
        <Text style={styles.label}>Mobile Number</Text>
        <TextInput
          style={styles.input}
          placeholder="+91 98410 12345"
          keyboardType="phone-pad"
          value={phone}
          onChangeText={setPhone}
        />
      </View>

      <View style={styles.formGroup}>
        <Text style={styles.label}>Create Password</Text>
        <TextInput
          style={styles.input}
          placeholder="••••••••"
          secureTextEntry
          value={password}
          onChangeText={setPassword}
        />
      </View>

      <TouchableOpacity
        style={styles.registerButton}
        activeOpacity={0.8}
        onPress={handleRegister}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color={Colors.surface} />
        ) : (
          <Text style={styles.registerButtonText}>Register as Artisan</Text>
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
  registerButton: {
    backgroundColor: Colors.primary,
    paddingVertical: Spacing.base,
    borderRadius: BorderRadius.md,
    alignItems: "center",
    marginTop: Spacing.md,
  },
  registerButtonText: {
    ...Typography.bodyBold,
    color: Colors.surface,
  },
});
