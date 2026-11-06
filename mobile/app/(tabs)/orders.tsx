import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Image,
  Alert,
} from "react-native";
import { Colors, Spacing, BorderRadius, Typography } from "../../src/constants/theme";
import {
  Package,
  Truck,
  CheckCircle2,
  Building2,
  Clock,
  ArrowRight,
  ShieldCheck,
} from "lucide-react-native";

export default function MobileOrdersScreen() {
  const [activeTab, setActiveTab] = useState<"retail" | "wholesale">("retail");

  const [retailOrders, setRetailOrders] = useState([
    {
      id: "ORD-94812",
      productTitle: "Handcrafted Vilachery Terracotta Ayyanar Figurine",
      buyerName: "Anita Roy",
      city: "Bengaluru, Karnataka",
      date: "04 Nov 2026",
      totalPrice: 1850,
      fairWage: 950,
      status: "READY_TO_PACK",
      imageUrl: "https://images.unsplash.com/photo-1578749556568-bc2c40e68b61?auto=format&fit=crop&w=600&q=80",
    },
    {
      id: "ORD-94751",
      productTitle: "Traditional Terracotta Diya Set of 6",
      buyerName: "Sanjay Sharma",
      city: "New Delhi",
      date: "03 Nov 2026",
      totalPrice: 750,
      fairWage: 420,
      status: "SHIPPED",
      imageUrl: "https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?auto=format&fit=crop&w=600&q=80",
    },
  ]);

  const [b2bRequests, setB2bRequests] = useState([
    {
      id: "RFQ-2041",
      buyerOrg: "FabCraft Global Retail",
      title: "100 Units Kiln-Fired Vilachery Sculptures",
      quantity: 100,
      targetPrice: "₹1,100 / unit",
      deliveryDate: "28 Nov 2026",
      status: "ACTIVE_INQUIRY",
    },
  ]);

  const handlePackOrder = (id: string) => {
    setRetailOrders((prev) =>
      prev.map((o) => (o.id === id ? { ...o, status: "SHIPPED" } : o))
    );
    Alert.alert(
      "Order Dispatched",
      `Order ${id} is marked as packed. Cryptographic QR verification seal generated!`
    );
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Title */}
      <View style={styles.header}>
        <Text style={styles.title}>Orders & Inquiries</Text>
        <Text style={styles.subtitle}>
          Track your direct retail shipments and wholesale bulk orders.
        </Text>
      </View>

      {/* Segmented Control */}
      <View style={styles.tabBar}>
        <TouchableOpacity
          style={[styles.tabBtn, activeTab === "retail" && styles.tabBtnActive]}
          onPress={() => setActiveTab("retail")}
        >
          <Text style={[styles.tabText, activeTab === "retail" && styles.tabTextActive]}>
            Retail Orders ({retailOrders.length})
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tabBtn, activeTab === "wholesale" && styles.tabBtnActive]}
          onPress={() => setActiveTab("wholesale")}
        >
          <Text style={[styles.tabText, activeTab === "wholesale" && styles.tabTextActive]}>
            Wholesale B2B ({b2bRequests.length})
          </Text>
        </TouchableOpacity>
      </View>

      {activeTab === "retail" ? (
        <View style={styles.listContainer}>
          {retailOrders.map((order) => (
            <View key={order.id} style={styles.orderCard}>
              <View style={styles.orderTop}>
                <Image source={{ uri: order.imageUrl }} style={styles.thumb} />
                <View style={{ flex: 1, marginLeft: 12 }}>
                  <View style={styles.idRow}>
                    <Text style={styles.orderId}>{order.id}</Text>
                    <View
                      style={[
                        styles.statusBadge,
                        order.status === "SHIPPED" && { backgroundColor: "#EAF2ED" },
                      ]}
                    >
                      <Text
                        style={[
                          styles.statusText,
                          order.status === "SHIPPED" && { color: Colors.success },
                        ]}
                      >
                        {order.status === "SHIPPED" ? "Dispatched" : "Ready to Pack"}
                      </Text>
                    </View>
                  </View>
                  <Text style={styles.orderTitle} numberOfLines={2}>
                    {order.productTitle}
                  </Text>
                  <Text style={styles.orderBuyer}>Buyer: {order.buyerName} ({order.city})</Text>
                </View>
              </View>

              <View style={styles.payoutRow}>
                <View>
                  <Text style={styles.payoutLabel}>Total Price</Text>
                  <Text style={styles.priceValue}>₹{order.totalPrice}</Text>
                </View>
                <View style={{ alignItems: "flex-end" }}>
                  <Text style={styles.payoutLabel}>Your Direct Wage</Text>
                  <Text style={styles.wageValue}>₹{order.fairWage}</Text>
                </View>
              </View>

              {order.status !== "SHIPPED" ? (
                <TouchableOpacity
                  style={styles.actionBtn}
                  onPress={() => handlePackOrder(order.id)}
                  activeOpacity={0.8}
                >
                  <CheckCircle2 size={16} color={Colors.surface} />
                  <Text style={styles.actionBtnText}>Mark Packed & Print QR</Text>
                </TouchableOpacity>
              ) : (
                <View style={styles.shippedRow}>
                  <Truck size={14} color={Colors.success} />
                  <Text style={styles.shippedText}>In Transit • Payout will release upon delivery</Text>
                </View>
              )}
            </View>
          ))}
        </View>
      ) : (
        <View style={styles.listContainer}>
          {b2bRequests.map((rfq) => (
            <View key={rfq.id} style={styles.orderCard}>
              <View style={styles.idRow}>
                <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
                  <Building2 size={16} color={Colors.secondary} />
                  <Text style={styles.b2bOrg}>{rfq.buyerOrg}</Text>
                </View>
                <View style={styles.statusBadge}>
                  <Text style={styles.statusText}>Active RFQ</Text>
                </View>
              </View>

              <Text style={[styles.orderTitle, { marginTop: 6 }]}>{rfq.title}</Text>

              <View style={styles.b2bDetails}>
                <Text style={styles.b2bDetailText}>Quantity: {rfq.quantity} Units</Text>
                <Text style={styles.b2bDetailText}>Target: {rfq.targetPrice}</Text>
                <Text style={styles.b2bDetailText}>Delivery: {rfq.deliveryDate}</Text>
              </View>

              <TouchableOpacity
                style={[styles.actionBtn, { backgroundColor: Colors.secondary }]}
                onPress={() =>
                  Alert.alert(
                    "Submit Quote",
                    "Quotation formulated with 30% material advance and guaranteed fair wages!"
                  )
                }
              >
                <Text style={styles.actionBtnText}>Send Quotation (With 30% Advance)</Text>
              </TouchableOpacity>
            </View>
          ))}
        </View>
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
  tabBar: {
    flexDirection: "row",
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.md,
    padding: 3,
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: Spacing.base,
  },
  tabBtn: {
    flex: 1,
    paddingVertical: 8,
    alignItems: "center",
    borderRadius: BorderRadius.sm,
  },
  tabBtnActive: {
    backgroundColor: Colors.primary,
  },
  tabText: {
    fontSize: 12,
    fontWeight: "600",
    color: Colors.muted,
  },
  tabTextActive: {
    color: Colors.surface,
  },
  listContainer: {
    gap: Spacing.md,
  },
  orderCard: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.base,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  orderTop: {
    flexDirection: "row",
  },
  thumb: {
    width: 68,
    height: 68,
    borderRadius: BorderRadius.md,
  },
  idRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  orderId: {
    fontSize: 11,
    fontWeight: "700",
    color: Colors.muted,
  },
  statusBadge: {
    backgroundColor: "#FDF8ED",
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: BorderRadius.sm,
    borderWidth: 1,
    borderColor: "#F4DFB8",
  },
  statusText: {
    fontSize: 10,
    fontWeight: "700",
    color: Colors.warning,
  },
  orderTitle: {
    ...Typography.small,
    fontWeight: "700",
    color: Colors.text,
    marginTop: 3,
  },
  orderBuyer: {
    fontSize: 11,
    color: Colors.muted,
    marginTop: 2,
  },
  payoutRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    backgroundColor: Colors.background,
    borderRadius: BorderRadius.md,
    padding: Spacing.sm,
    paddingHorizontal: Spacing.md,
    marginTop: Spacing.md,
    marginBottom: Spacing.md,
  },
  payoutLabel: {
    fontSize: 10,
    color: Colors.muted,
  },
  priceValue: {
    fontSize: 14,
    fontWeight: "700",
    color: Colors.text,
  },
  wageValue: {
    fontSize: 14,
    fontWeight: "700",
    color: Colors.success,
  },
  actionBtn: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: Colors.primary,
    borderRadius: BorderRadius.md,
    paddingVertical: 10,
    gap: 6,
  },
  actionBtnText: {
    ...Typography.caption,
    fontWeight: "700",
    color: Colors.surface,
  },
  shippedRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 6,
    paddingVertical: 4,
  },
  shippedText: {
    fontSize: 11,
    color: Colors.success,
    fontWeight: "600",
  },
  b2bOrg: {
    ...Typography.small,
    fontWeight: "700",
    color: Colors.text,
  },
  b2bDetails: {
    backgroundColor: Colors.background,
    borderRadius: BorderRadius.md,
    padding: Spacing.sm,
    marginVertical: Spacing.md,
    gap: 2,
  },
  b2bDetailText: {
    fontSize: 11,
    color: Colors.muted,
  },
});

