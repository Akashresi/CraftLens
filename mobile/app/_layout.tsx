import React from "react";
import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { Colors } from "../src/constants/theme";

export default function RootLayout() {
  return (
    <SafeAreaProvider>
      <StatusBar style="dark" backgroundColor={Colors.background} />
      <Stack
        screenOptions={{
          headerStyle: {
            backgroundColor: Colors.surface,
          },
          headerTintColor: Colors.primary,
          headerTitleStyle: {
            fontWeight: "600",
          },
          contentStyle: {
            backgroundColor: Colors.background,
          },
        }}
      >
        <Stack.Screen name="index" options={{ headerShown: false }} />
        <Stack.Screen name="language" options={{ title: "Select Language / மொழியைத் தேர்ந்தெடுக்கவும்" }} />
        <Stack.Screen name="login" options={{ title: "Sign In" }} />
        <Stack.Screen name="register" options={{ title: "Create Buyer Account" }} />
        <Stack.Screen name="onboarding" options={{ title: "Artisan Onboarding" }} />
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="(buyer-tabs)" options={{ headerShown: false }} />
      </Stack>
    </SafeAreaProvider>
  );
}

