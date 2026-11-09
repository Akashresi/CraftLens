import React, { useEffect } from "react";
import { Tabs, useRouter } from "expo-router";
import { Colors } from "../../src/constants/theme";
import { Store, ShoppingBag, User } from "lucide-react-native";
import { useAuthStore } from "../../src/store/authStore";

export default function BuyerTabLayout() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();

  useEffect(() => {
    // If not authenticated, prompt to sign in
    if (!isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, router]);

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
        name="marketplace"
        options={{
          title: "Craft Marketplace",
          tabBarLabel: "Explore",
          tabBarIcon: ({ color, size }) => <Store color={color} size={size} />,
        }}
      />
      <Tabs.Screen
        name="orders"
        options={{
          title: "My Orders",
          tabBarLabel: "Orders",
          tabBarIcon: ({ color, size }) => <ShoppingBag color={color} size={size} />,
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: "Buyer Profile",
          tabBarLabel: "Profile",
          tabBarIcon: ({ color, size }) => <User color={color} size={size} />,
        }}
      />
      <Tabs.Screen
        name="apply-artisan"
        options={{
          href: null, // Hidden from bottom tab bar, accessible from profile
          title: "Become an Artisan",
        }}
      />
    </Tabs>
  );
}

