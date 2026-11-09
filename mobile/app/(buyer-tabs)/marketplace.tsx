import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Image,
  Modal,
  ActivityIndicator,
  FlatList,
} from "react-native";
import { Colors, Spacing, Typography, BorderRadius } from "../../src/constants/theme";
import { Search, MapPin, Tag, Check, X, ShoppingCart } from "lucide-react-native";

interface ProductItem {
  id: string;
  title: string;
  category: string;
  category_slug: string;
  price: number;
  artisan_name: string;
  origin: string;
  gi_tagged: boolean;
  image_url: string;
  description: string;
  material: string;
  technique: string;
}

const CATEGORIES = [
  { id: "all", label: "All Crafts" },
  { id: "handloom-textiles", label: "Handloom & Textiles" },
  { id: "terracotta-pottery", label: "Terracotta & Pottery" },
  { id: "woodcraft-toys", label: "Woodcraft & Toys" },
  { id: "metal-brassware", label: "Metal & Brassware" },
  { id: "traditional-painting", label: "Folk Paintings" },
];

const INITIAL_PRODUCTS: ProductItem[] = [
  {
    id: "prod-1",
    title: "Kanchipuram Pure Mulberry Silk Saree",
    category: "Handloom & Textiles",
    category_slug: "handloom-textiles",
    price: 8500,
    artisan_name: "Meenakshi Ammal",
    origin: "Kanchipuram, Tamil Nadu",
    gi_tagged: true,
    image_url: "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=600&q=80",
    description: "Woven on traditional pit looms with pure mulberry silk and tested silver zari temple borders.",
    material: "100% Mulberry Silk, Zari",
    technique: "Korvai Handloom Weaving",
  },
  {
    id: "prod-2",
    title: "Channapatna Lacquered Wooden Rocking Horse",
    category: "Woodcraft & Toys",
    category_slug: "woodcraft-toys",
    price: 1250,
    artisan_name: "Ramesh Channapatna",
    origin: "Channapatna, Karnataka",
    gi_tagged: true,
    image_url: "https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?auto=format&fit=crop&w=600&q=80",
    description: "Safe, child-friendly toy handcrafted from Wrightia tinctoria wood and colored using non-toxic natural vegetable lacquers.",
    material: "Ivory Wood (Aale Mara), Natural Lac",
    technique: "Lathe Turning & Buffing",
  },
  {
    id: "prod-3",
    title: "Hand-thrown Terracotta Water Jug",
    category: "Terracotta & Pottery",
    category_slug: "terracotta-pottery",
    price: 650,
    artisan_name: "Lakshmi Potter",
    origin: "Gorakhpur, Uttar Pradesh",
    gi_tagged: true,
    image_url: "https://images.unsplash.com/photo-1578749556568-bc2c40e68b61?auto=format&fit=crop&w=600&q=80",
    description: "Traditional porous terracotta clay pot naturally cools water through evaporative cooling without electricity.",
    material: "Natural Alluvial Clay",
    technique: "Wheel Throwing & Wood Firing",
  },
  {
    id: "prod-4",
    title: "Bastar Dhokra Bell Metal Tribal Musician",
    category: "Metal & Brassware",
    category_slug: "metal-brassware",
    price: 3200,
    artisan_name: "Sukhram Baghel",
    origin: "Bastar, Chhattisgarh",
    gi_tagged: true,
    image_url: "https://images.unsplash.com/photo-1582562124811-c09040d0a901?auto=format&fit=crop&w=600&q=80",
    description: "4,000-year-old lost wax non-ferrous metal casting depicting indigenous folk musicians.",
    material: "Brass, Bronze, Beeswax",
    technique: "Cire Perdue Lost Wax Casting",
  },
  {
    id: "prod-5",
    title: "Madhubani Tree of Life Mithila Painting",
    category: "Traditional Painting",
    category_slug: "traditional-painting",
    price: 4500,
    artisan_name: "Kavita Devi",
    origin: "Madhubani, Bihar",
    gi_tagged: true,
    image_url: "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=600&q=80",
    description: "Freehand line drawing on cowdung treated handmade paper using bamboo twigs and vegetable pigments.",
    material: "Handmade Paper, Natural Pigments",
    technique: "Kachni Fine Nib Painting",
  },
];

export default function BuyerMarketplaceScreen() {
  const [products, setProducts] = useState<ProductItem[]>(INITIAL_PRODUCTS);
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedProduct, setSelectedProduct] = useState<ProductItem | null>(null);
  const [cartSuccess, setCartSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Attempt to fetch fresh products from backend
    const loadMarketplace = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/v1/marketplace/products");
        if (res.ok) {
          const json = await res.json();
          if (json.success && Array.isArray(json.data) && json.data.length > 0) {
            // Map backend product data to ProductItem format
            const mapped: ProductItem[] = json.data.map((p: any) => ({
              id: p.id,
              title: p.title,
              category: p.category_name || "Handicrafts",
              category_slug: p.category_slug || "handcraft",
              price: p.retail_price || 999,
              artisan_name: p.artisan_name || "Verified Artisan",
              origin: p.origin_state ? `${p.origin_name || "Heritage"}, ${p.origin_state}` : "India",
              gi_tagged: !!p.gi_certified,
              image_url: p.primary_image_url || "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=600&q=80",
              description: p.description || "Handcrafted traditional Indian craft product.",
              material: p.primary_material || "Authentic materials",
              technique: p.craft_technique || "Traditional handcrafting",
            }));
            setProducts(mapped);
          }
        }
      } catch (err) {
        // Fallback to rich curated local dataset
      }
    };
    loadMarketplace();
  }, []);

  const filtered = products.filter((p) => {
    const matchesCategory =
      selectedCategory === "all" || p.category_slug === selectedCategory;
    const matchesSearch =
      !searchQuery ||
      p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.artisan_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.origin.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const handleAddToCart = () => {
    setCartSuccess(true);
    setTimeout(() => {
      setCartSuccess(false);
      setSelectedProduct(null);
    }, 1500);
  };

  return (
    <View style={styles.container}>
      {/* Search Header */}
      <View style={styles.searchBarContainer}>
        <Search color={Colors.muted} size={18} style={styles.searchIcon} />
        <TextInput
          style={styles.searchInput}
          placeholder="Search sarees, pottery, toys, woodcraft..."
          placeholderTextColor={Colors.muted}
          value={searchQuery}
          onChangeText={setSearchQuery}
        />
        {searchQuery.length > 0 && (
          <TouchableOpacity onPress={() => setSearchQuery("")}>
            <X color={Colors.muted} size={16} />
          </TouchableOpacity>
        )}
      </View>

      {/* Category Horizontal Filter */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.categoryScroll}
      >
        {CATEGORIES.map((cat) => (
          <TouchableOpacity
            key={cat.id}
            style={[
              styles.categoryChip,
              selectedCategory === cat.id && styles.categoryChipActive,
            ]}
            onPress={() => setSelectedCategory(cat.id)}
          >
            <Text
              style={[
                styles.categoryChipText,
                selectedCategory === cat.id && styles.categoryChipTextActive,
              ]}
            >
              {cat.label}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Product List */}
      <FlatList
        data={filtered}
        keyExtractor={(item) => item.id}
        numColumns={2}
        contentContainerStyle={styles.productList}
        columnWrapperStyle={styles.columnWrapper}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.productCard}
            activeOpacity={0.85}
            onPress={() => setSelectedProduct(item)}
          >
            <Image source={{ uri: item.image_url }} style={styles.productImage} />
            {item.gi_tagged && (
              <View style={styles.giBadge}>
                <Text style={styles.giBadgeText}>GI CERTIFIED</Text>
              </View>
            )}
            <View style={styles.cardContent}>
              <Text style={styles.productTitle} numberOfLines={2}>
                {item.title}
              </Text>
              <Text style={styles.artisanName} numberOfLines={1}>
                By {item.artisan_name}
              </Text>
              <View style={styles.originRow}>
                <MapPin color={Colors.muted} size={11} />
                <Text style={styles.originText} numberOfLines={1}>
                  {item.origin}
                </Text>
              </View>
              <View style={styles.priceRow}>
                <Text style={styles.priceText}>₹{item.price.toLocaleString("en-IN")}</Text>
                <Text style={styles.fairWageTag}>Fair Wage</Text>
              </View>
            </View>
          </TouchableOpacity>
        )}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyTitle}>No products found</Text>
            <Text style={styles.emptySubtitle}>Try adjusting your search query or category filter</Text>
          </View>
        }
      />

      {/* Product Details Modal */}
      {selectedProduct && (
        <Modal
          visible={!!selectedProduct}
          animationType="slide"
          transparent
          onRequestClose={() => setSelectedProduct(null)}
        >
          <View style={styles.modalOverlay}>
            <View style={styles.modalContent}>
              <TouchableOpacity
                style={styles.modalCloseButton}
                onPress={() => setSelectedProduct(null)}
              >
                <X color={Colors.text} size={20} />
              </TouchableOpacity>

              <ScrollView showsVerticalScrollIndicator={false}>
                <Image
                  source={{ uri: selectedProduct.image_url }}
                  style={styles.modalImage}
                />

                <View style={styles.modalBody}>
                  {selectedProduct.gi_tagged && (
                    <View style={styles.modalGiBadge}>
                      <Text style={styles.modalGiBadgeText}>
                        GEOGRAPHICAL INDICATION (GI) CERTIFIED AUTHENTIC CRAFT
                      </Text>
                    </View>
                  )}

                  <Text style={styles.modalTitle}>{selectedProduct.title}</Text>
                  <Text style={styles.modalArtisan}>
                    Crafted with pride by <Text style={styles.bold}>{selectedProduct.artisan_name}</Text>
                  </Text>
                  <Text style={styles.modalOrigin}>
                    Heritage Origin: {selectedProduct.origin}
                  </Text>

                  <View style={styles.metaBox}>
                    <View style={styles.metaRow}>
                      <Text style={styles.metaLabel}>Primary Material:</Text>
                      <Text style={styles.metaValue}>{selectedProduct.material}</Text>
                    </View>
                    <View style={styles.metaRow}>
                      <Text style={styles.metaLabel}>Technique:</Text>
                      <Text style={styles.metaValue}>{selectedProduct.technique}</Text>
                    </View>
                  </View>

                  <Text style={styles.descriptionHeader}>Product Story</Text>
                  <Text style={styles.descriptionText}>
                    {selectedProduct.description}
                  </Text>

                  <View style={styles.pricingSection}>
                    <div>
                      <Text style={styles.modalPriceLabel}>Direct Artisan Price</Text>
                      <Text style={styles.modalPrice}>
                        ₹{selectedProduct.price.toLocaleString("en-IN")}
                      </Text>
                    </div>

                    <TouchableOpacity
                      style={[
                        styles.buyButton,
                        cartSuccess && styles.buyButtonSuccess,
                      ]}
                      onPress={handleAddToCart}
                    >
                      {cartSuccess ? (
                        <View style={styles.btnRow}>
                          <Check color={Colors.surface} size={18} />
                          <Text style={styles.buyButtonText}>Added to Cart!</Text>
                        </View>
                      ) : (
                        <View style={styles.btnRow}>
                          <ShoppingCart color={Colors.surface} size={18} />
                          <Text style={styles.buyButtonText}>Add to Cart</Text>
                        </View>
                      )}
                    </TouchableOpacity>
                  </View>
                </View>
              </ScrollView>
            </View>
          </View>
        </Modal>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  searchBarContainer: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: Colors.surface,
    marginHorizontal: Spacing.md,
    marginTop: Spacing.sm,
    paddingHorizontal: Spacing.sm,
    borderRadius: BorderRadius.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    height: 44,
  },
  searchIcon: {
    marginRight: Spacing.xs,
  },
  searchInput: {
    flex: 1,
    fontSize: 13,
    color: Colors.text,
  },
  categoryScroll: {
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    gap: Spacing.xs,
  },
  categoryChip: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: BorderRadius.full,
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  categoryChipActive: {
    backgroundColor: Colors.primary,
    borderColor: Colors.primary,
  },
  categoryChipText: {
    fontSize: 12,
    fontWeight: "600",
    color: Colors.muted,
  },
  categoryChipTextActive: {
    color: Colors.surface,
    fontWeight: "700",
  },
  productList: {
    paddingHorizontal: Spacing.md,
    paddingBottom: Spacing.xl,
  },
  columnWrapper: {
    justifyContent: "space-between",
    marginBottom: Spacing.md,
  },
  productCard: {
    width: "48%",
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    overflow: "hidden",
  },
  productImage: {
    width: "100%",
    height: 140,
    backgroundColor: Colors.background,
  },
  giBadge: {
    position: "absolute",
    top: 6,
    left: 6,
    backgroundColor: Colors.secondary,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  giBadgeText: {
    color: Colors.surface,
    fontSize: 8,
    fontWeight: "800",
    letterSpacing: 0.5,
  },
  cardContent: {
    padding: Spacing.sm,
  },
  productTitle: {
    fontSize: 13,
    fontWeight: "700",
    color: Colors.text,
    lineHeight: 18,
    minHeight: 36,
  },
  artisanName: {
    fontSize: 11,
    color: Colors.muted,
    marginTop: 2,
  },
  originRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 3,
    marginTop: 3,
  },
  originText: {
    fontSize: 10,
    color: Colors.muted,
  },
  priceRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginTop: Spacing.xs,
    paddingTop: 4,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
  },
  priceText: {
    fontSize: 14,
    fontWeight: "800",
    color: Colors.primary,
  },
  fairWageTag: {
    fontSize: 9,
    color: Colors.success,
    fontWeight: "700",
  },
  emptyContainer: {
    padding: Spacing.xxl,
    alignItems: "center",
  },
  emptyTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: Colors.text,
  },
  emptySubtitle: {
    fontSize: 12,
    color: Colors.muted,
    marginTop: 4,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.5)",
    justifyContent: "flex-end",
  },
  modalContent: {
    backgroundColor: Colors.surface,
    borderTopLeftRadius: BorderRadius.xl,
    borderTopRightRadius: BorderRadius.xl,
    maxHeight: "85%",
  },
  modalCloseButton: {
    position: "absolute",
    right: 16,
    top: 16,
    zIndex: 10,
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: "rgba(255,255,255,0.85)",
    justifyContent: "center",
    alignItems: "center",
  },
  modalImage: {
    width: "100%",
    height: 240,
  },
  modalBody: {
    padding: Spacing.md,
  },
  modalGiBadge: {
    backgroundColor: Colors.secondary,
    alignSelf: "flex-start",
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 4,
    marginBottom: Spacing.xs,
  },
  modalGiBadgeText: {
    color: Colors.surface,
    fontSize: 9,
    fontWeight: "800",
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: "800",
    color: Colors.text,
  },
  modalArtisan: {
    fontSize: 13,
    color: Colors.muted,
    marginTop: 2,
  },
  bold: {
    fontWeight: "700",
    color: Colors.text,
  },
  modalOrigin: {
    fontSize: 12,
    color: Colors.muted,
    marginTop: 2,
  },
  metaBox: {
    backgroundColor: Colors.background,
    padding: Spacing.sm,
    borderRadius: BorderRadius.md,
    marginVertical: Spacing.sm,
    gap: 4,
  },
  metaRow: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  metaLabel: {
    fontSize: 11,
    color: Colors.muted,
  },
  metaValue: {
    fontSize: 11,
    fontWeight: "600",
    color: Colors.text,
  },
  descriptionHeader: {
    fontSize: 13,
    fontWeight: "700",
    color: Colors.text,
    marginTop: Spacing.xs,
  },
  descriptionText: {
    fontSize: 12,
    color: Colors.muted,
    lineHeight: 18,
    marginTop: 2,
  },
  pricingSection: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginTop: Spacing.md,
    paddingTop: Spacing.sm,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
  },
  modalPriceLabel: {
    fontSize: 10,
    color: Colors.muted,
  },
  modalPrice: {
    fontSize: 20,
    fontWeight: "800",
    color: Colors.primary,
  },
  buyButton: {
    backgroundColor: Colors.primary,
    paddingHorizontal: Spacing.lg,
    paddingVertical: 12,
    borderRadius: BorderRadius.lg,
  },
  buyButtonSuccess: {
    backgroundColor: Colors.success,
  },
  btnRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  buyButtonText: {
    color: Colors.surface,
    fontSize: 13,
    fontWeight: "700",
  },
});
