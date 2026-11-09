import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
} from "react-native";
import { Colors, Spacing, Typography, BorderRadius } from "../../src/constants/theme";
import { Package, Truck, CheckCircle2, Clock, ChevronRight } from "lucide-react-native";

interface BuyerOrder {
  id: string;
  order_number: string;
  date: string;
  status: "CONFIRMED" | "DISPATCHED" | "DELIVERED";
  total_amount: number;
  item_title: string;
  artisan_name: string;
  image_url: string;
  tracking_id?: string;
  carrier?: string;
}

const MOCK_ORDERS: BuyerOrder[] = [
  {
    id: "ord-1",
    order_number: "CL-ORD-2026-9812",
    date: "06 Nov 2026",
    status: "DISPATCHED",
    total_amount: 8500,
    item_title: "Kanchipuram Pure Mulberry Silk Saree",
    artisan_name: "Meenakshi Ammal",
    image_url: "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=600&q=80",
    tracking_id: "INDPOST-TN-882194",
    carrier: "India Post Speed Post",
  },
  {
    id: "ord-2",
    order_number: "CL-ORD-2026-7731",
    date: "28 Oct 2026",
    status: "DELIVERED",
    total_amount: 1250,
    item_title: "Channapatna Lacquered Wooden Rocking Horse",
    artisan_name: "Ramesh Channapatna",
    image_url: "https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?auto=format&fit=crop&w=600&q=80",
    tracking_id: "DTDC-KA-55102",
    carrier: "DTDC Express",
  },
];

export default function BuyerOrdersScreen() {
  const [orders] = useState<BuyerOrder[]>(MOCK_ORDERS);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.title}>Your Craft Orders</Text>
        <Text style={styles.subtitle}>
          Track your handmade authentic purchases shipped directly from artisan clusters
        </Text>
      </View>

      <View style={styles.orderList}>
        {orders.map((order) => (
          <View key={order.id} style={styles.orderCard}>
            <View style={styles.orderCardHeader}>
              <div>
                <Text style={styles.orderNumber}>{order.order_number}</Text>
                <Text style={styles.orderDate}>Ordered on {order.date}</Text>
              </div>
              <View
                style={[
                  styles.statusBadge,
                  order.status === "DELIVERED"
                    ? styles.statusDelivered
                    : styles.statusDispatched,
                ]}
              >
                {order.status === "DELIVERED" ? (
                  <CheckCircle2 color={Colors.success} size={12} />
                ) : (
                  <Truck color={Colors.secondary} size={12} />
                )}
                <Text
                  style={[
                    styles.statusText,
                    order.status === "DELIVERED"
                      ? styles.statusTextDelivered
                      : styles.statusTextDispatched,
                  ]}
                >
                  {order.status}
                </Text>
              </View>
            </View>

            <View style={styles.itemRow}>
              <Image source={{ uri: order.image_url }} style={styles.itemImage} />
              <View style={styles.itemDetails}>
                <Text style={styles.itemTitle} numberOfLines={2}>
                  {order.item_title}
                </Text>
                <Text style={styles.itemArtisan}>Artisan: {order.artisan_name}</Text>
                <Text style={styles.itemPrice}>
                  ₹{order.total_amount.toLocaleString("en-IN")}
                </Text>
              </View>
            </View>

            {order.tracking_id && (
              <View style={styles.trackingBox}>
                <View style={styles.trackingInfo}>
                  <Truck color={Colors.muted} size={14} />
                  <Text style={styles.trackingText}>
                    {order.carrier}: <Text style={styles.bold}>{order.tracking_id}</Text>
                  </Text>
                </View>
              </View>
            )}
          </View>
        ))}
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
  orderList: {
    gap: Spacing.md,
  },
  orderCard: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    padding: Spacing.md,
    gap: Spacing.sm,
  },
  orderCardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
    paddingBottom: Spacing.xs,
  },
  orderNumber: {
    fontSize: 12,
    fontWeight: "700",
    color: Colors.text,
  },
  orderDate: {
    fontSize: 10,
    color: Colors.muted,
    marginTop: 1,
  },
  statusBadge: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: BorderRadius.sm,
  },
  statusDispatched: {
    backgroundColor: "rgba(224, 122, 95, 0.1)",
  },
  statusDelivered: {
    backgroundColor: "rgba(42, 157, 143, 0.1)",
  },
  statusText: {
    fontSize: 10,
    fontWeight: "800",
  },
  statusTextDispatched: {
    color: Colors.secondary,
  },
  statusTextDelivered: {
    color: Colors.success,
  },
  itemRow: {
    flexDirection: "row",
    gap: Spacing.sm,
    alignItems: "center",
  },
  itemImage: {
    width: 60,
    height: 60,
    borderRadius: BorderRadius.md,
    backgroundColor: Colors.background,
  },
  itemDetails: {
    flex: 1,
  },
  itemTitle: {
    fontSize: 13,
    fontWeight: "700",
    color: Colors.text,
  },
  itemArtisan: {
    fontSize: 11,
    color: Colors.muted,
    marginTop: 2,
  },
  itemPrice: {
    fontSize: 13,
    fontWeight: "800",
    color: Colors.primary,
    marginTop: 2,
  },
  trackingBox: {
    backgroundColor: Colors.background,
    padding: Spacing.xs,
    borderRadius: BorderRadius.sm,
    marginTop: 2,
  },
  trackingInfo: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  trackingText: {
    fontSize: 11,
    color: Colors.muted,
  },
  bold: {
    fontWeight: "700",
    color: Colors.text,
  },
});
