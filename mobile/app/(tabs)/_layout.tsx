import React, { useEffect } from "react";
import { Tabs, useRouter } from "expo-router";
import { Colors } from "../../src/constants/theme";
import { Home, Camera, Mic, Calculator, ShoppingBag, User } from "lucide-react-native";
import { useAuthStore } from "../../src/store/authStore";

export default function TabLayout() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace("/login");
      return;
    }

    // Role-based access control: Only ARTISAN may enter this tab suite
    if (user && user.role !== "ARTISAN") {
      router.replace("/(buyer-tabs)/marketplace");
    }
  }, [isAuthenticated, user, router]);

  if (!isAuthenticated || user?.role !== "ARTISAN") {
    return null;
  }
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: Colors.primary,
        tabBarInactiveTintColor: Colors.muted,
        tabBarStyle: {
          backgroundColor: Colors.surface,
          borderTopColor: Colors.border,
          height: 60,
          paddingBottom: 8,
          paddingTop: 6,
        },
        headerStyle: {
          backgroundColor: Colors.surface,
          borderBottomColor: Colors.border,
        },
        headerTintColor: Colors.primary,
        headerTitleStyle: {
          fontWeight: "700",
          fontSize: 17,
        },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: "Dashboard",
          tabBarLabel: "Home",
          tabBarIcon: ({ color, size }) => <Home color={color} size={size} />,
        }}
      />
      <Tabs.Screen
        name="studio"
        options={{
          title: "AI Studio",
          tabBarLabel: "Studio",
          tabBarIcon: ({ color, size }) => <Camera color={color} size={size} />,
        }}
      />
      <Tabs.Screen
        name="voice"
        options={{
          title: "Voice Catalog",
          tabBarLabel: "Voice AI",
          tabBarIcon: ({ color, size }) => <Mic color={color} size={size} />,
        }}
      />
      <Tabs.Screen
        name="pricing"
        options={{
          title: "Fair Pricing",
          tabBarLabel: "Pricing",
          tabBarIcon: ({ color, size }) => <Calculator color={color} size={size} />,
        }}
      />
      <Tabs.Screen
        name="orders"
        options={{
          title: "Orders & B2B",
          tabBarLabel: "Orders",
          tabBarIcon: ({ color, size }) => <ShoppingBag color={color} size={size} />,
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: "Heritage Profile",
          tabBarLabel: "Profile",
          tabBarIcon: ({ color, size }) => <User color={color} size={size} />,
        }}
      />
    </Tabs>
  );
}

