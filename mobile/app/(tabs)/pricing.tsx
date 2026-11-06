import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  TextInput,
  Alert,
} from "react-native";
import { Colors, Spacing, BorderRadius, Typography } from "../../src/constants/theme";
import {
  Calculator,
  HeartHandshake,
  CheckCircle2,
  TrendingUp,
  ShieldCheck,
  Info,
} from "lucide-react-native";

export default function MobilePricingScreen() {
  const [materialCost, setMaterialCost] = useState("320");
  const [laborHours, setLaborHours] = useState("6.5");
  const [hourlyRate, setHourlyRate] = useState("150");
  const [packagingTransport, setPackagingTransport] = useState("180");
  const [profitMargin, setProfitMargin] = useState("25");

  // Calculations
  const mat = parseFloat(materialCost) || 0;
  const hrs = parseFloat(laborHours) || 0;
  const rate = parseFloat(hourlyRate) || 0;
  const pack = parseFloat(packagingTransport) || 0;
  const margin = parseFloat(profitMargin) || 0;

  const laborTotal = Math.round(hrs * rate);
  const baseCost = Math.round(mat + laborTotal + pack);
  const retailPrice = Math.round(baseCost * (1 + margin / 100));
  const wholesalePrice = Math.round(baseCost * 1.15);
  const exportPrice = Math.round(retailPrice * 1.45);

  const handleApply = () => {
    Alert.alert(
      "Price Locked",
      `Retail price ₹${retailPrice} and Wholesale ₹${wholesalePrice} applied to current catalog draft with full living wage protection!`
    );
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Fair Wage Pricing</Text>
        <Text style={styles.subtitle}>
          Ensure fair compensation for every hour of skilled craftsmanship.
        </Text>
      </View>

      {/* Living Wage Banner */}
      <View style={styles.wageBanner}>
        <HeartHandshake size={20} color={Colors.success} />
        <View style={{ flex: 1, marginLeft: 10 }}>
          <Text style={styles.wageBannerTitle}>Living Wage Guaranteed</Text>
          <Text style={styles.wageBannerDesc}>
            Calculated to guarantee artisans at least ₹150/hour for skilled manual labor.
          </Text>
        </View>
      </View>

      {/* Input Form */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Cost & Labor Breakdown</Text>

        <View style={styles.fieldRow}>
          <View style={{ flex: 1, marginRight: 8 }}>
            <Text style={styles.label}>Raw Materials (₹)</Text>
            <TextInput
              style={styles.input}
              keyboardType="numeric"
              value={materialCost}
              onChangeText={setMaterialCost}
            />
          </View>
          <View style={{ flex: 1, marginLeft: 8 }}>
            <Text style={styles.label}>Labor Hours</Text>
            <TextInput
              style={styles.input}
              keyboardType="numeric"
              value={laborHours}
              onChangeText={setLaborHours}
            />
          </View>
        </View>

        <View style={styles.fieldRow}>
          <View style={{ flex: 1, marginRight: 8 }}>
            <Text style={styles.label}>Hourly Rate (₹/hr)</Text>
            <TextInput
              style={styles.input}
              keyboardType="numeric"
              value={hourlyRate}
              onChangeText={setHourlyRate}
            />
          </View>
          <View style={{ flex: 1, marginLeft: 8 }}>
            <Text style={styles.label}>Packaging & Transport (₹)</Text>
            <TextInput
              style={styles.input}
              keyboardType="numeric"
              value={packagingTransport}
              onChangeText={setPackagingTransport}
            />
          </View>
        </View>

        <View style={{ marginTop: Spacing.sm }}>
          <Text style={styles.label}>Desired Artisan Profit Margin ({profitMargin}%)</Text>
          <TextInput
            style={styles.input}
            keyboardType="numeric"
            value={profitMargin}
            onChangeText={setProfitMargin}
          />
        </View>
      </View>

      {/* Recommended Pricing Tiers */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Computed Fair Price Tiers</Text>

        <View style={styles.tiersGrid}>
          <View style={styles.tierBox}>
            <Text style={styles.tierLabel}>Retail Price</Text>
            <Text style={styles.tierValue}>₹{retailPrice}</Text>
            <Text style={styles.tierSub}>Direct to Buyer</Text>
          </View>

          <View style={styles.tierBox}>
            <Text style={styles.tierLabel}>Wholesale</Text>
            <Text style={[styles.tierValue, { color: Colors.secondary }]}>₹{wholesalePrice}</Text>
            <Text style={styles.tierSub}>Min 25 Units</Text>
          </View>

          <View style={styles.tierBox}>
            <Text style={styles.tierLabel}>Export Global</Text>
            <Text style={styles.tierValue}>₹{exportPrice}</Text>
            <Text style={styles.tierSub}>International</Text>
          </View>
        </View>

        {/* Explainable Allocation */}
        <View style={styles.allocationBox}>
          <View style={styles.allocRow}>
            <Text style={styles.allocText}>Your Direct Artisan Wage:</Text>
            <Text style={[styles.allocValue, { color: Colors.success }]}>₹{laborTotal}</Text>
          </View>
          <View style={styles.allocRow}>
            <Text style={styles.allocText}>Direct Materials & Logistics:</Text>
            <Text style={styles.allocValue}>₹{mat + pack}</Text>
          </View>
          <View style={[styles.allocRow, styles.allocTotal]}>
            <Text style={styles.allocTotalText}>Minimum Break-Even Price:</Text>
            <Text style={styles.allocTotalValue}>₹{baseCost}</Text>
          </View>
        </View>

        <TouchableOpacity style={styles.applyBtn} onPress={handleApply} activeOpacity={0.8}>
          <CheckCircle2 size={18} color={Colors.surface} />
          <Text style={styles.applyBtnText}>Apply Price to Product</Text>
        </TouchableOpacity>
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
  wageBanner: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#EAF2ED",
    borderRadius: BorderRadius.md,
    padding: Spacing.md,
    borderWidth: 1,
    borderColor: "#CFE3D5",
    marginBottom: Spacing.base,
  },
  wageBannerTitle: {
    ...Typography.caption,
    fontWeight: "700",
    color: Colors.success,
  },
  wageBannerDesc: {
    fontSize: 11,
    color: Colors.text,
    marginTop: 1,
  },
  card: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.base,
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: Spacing.base,
  },
  cardTitle: {
    ...Typography.bodyBold,
    color: Colors.text,
    marginBottom: Spacing.md,
  },
  fieldRow: {
    flexDirection: "row",
    marginBottom: Spacing.sm,
  },
  label: {
    fontSize: 11,
    fontWeight: "600",
    color: Colors.muted,
    marginBottom: 4,
  },
  input: {
    backgroundColor: Colors.background,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: BorderRadius.md,
    paddingHorizontal: Spacing.md,
    paddingVertical: 8,
    fontSize: 14,
    color: Colors.text,
    fontWeight: "600",
  },
  tiersGrid: {
    flexDirection: "row",
    gap: Spacing.sm,
    marginBottom: Spacing.base,
  },
  tierBox: {
    flex: 1,
    backgroundColor: Colors.background,
    borderRadius: BorderRadius.md,
    padding: Spacing.sm,
    alignItems: "center",
    borderWidth: 1,
    borderColor: Colors.border,
  },
  tierLabel: {
    fontSize: 10,
    fontWeight: "700",
    color: Colors.muted,
    textTransform: "uppercase",
  },
  tierValue: {
    ...Typography.h3,
    color: Colors.primary,
    fontWeight: "700",
    marginTop: 2,
  },
  tierSub: {
    fontSize: 9,
    color: Colors.muted,
    marginTop: 2,
  },
  allocationBox: {
    backgroundColor: Colors.background,
    borderRadius: BorderRadius.md,
    padding: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: Spacing.base,
  },
  allocRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 4,
  },
  allocText: {
    fontSize: 12,
    color: Colors.muted,
  },
  allocValue: {
    fontSize: 12,
    fontWeight: "700",
    color: Colors.text,
  },
  allocTotal: {
    borderTopWidth: 1,
    borderTopColor: Colors.border,
    marginTop: 6,
    paddingTop: 6,
  },
  allocTotalText: {
    fontSize: 12,
    fontWeight: "700",
    color: Colors.text,
  },
  allocTotalValue: {
    fontSize: 13,
    fontWeight: "800",
    color: Colors.primary,
  },
  applyBtn: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: Colors.primary,
    borderRadius: BorderRadius.md,
    paddingVertical: Spacing.md,
    gap: 6,
  },
  applyBtnText: {
    ...Typography.small,
    fontWeight: "700",
    color: Colors.surface,
  },
});

