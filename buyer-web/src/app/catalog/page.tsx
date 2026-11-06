"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Search, Filter, ShieldCheck, ShoppingBag, Eye, Sparkles } from "lucide-react";
import { api } from "@/lib/api";

interface Product {
  id: string;
  title: string;
  description?: string;
  category: string;
  price: number;
  fair_wage_amount: number;
  artisan_name: string;
  state: string;
  gi_tag?: string;
  image_url: string;
  stock_quantity: number;
}

const FALLBACK_PRODUCTS: Product[] = [
  {
    id: "p1",
    title: "Vilachery Handcrafted Terracotta Ayyanar Figurine",
    category: "Pottery & Clay",
    price: 1850,
    fair_wage_amount: 950,
    artisan_name: "Meenakshi Sundaram",
    state: "Tamil Nadu",
    gi_tag: "GI-TN-412",
    image_url: "https://images.unsplash.com/photo-1578749556568-bc2c40e68b61?auto=format&fit=crop&w=600&q=80",
    stock_quantity: 12,
  },
  {
    id: "p2",
    title: "Kanchipuram Korvai Pure Mulberry Silk Saree",
    category: "Handloom & Textiles",
    price: 14200,
    fair_wage_amount: 8200,
    artisan_name: "Ramanathan Weavers Co-op",
    state: "Tamil Nadu",
    gi_tag: "GI-TN-001",
    image_url: "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=600&q=80",
    stock_quantity: 5,
  },
  {
    id: "p3",
    title: "Bastar Tribal Dokra Lost-Wax Brass Figurine",
    category: "Metal & Bell Craft",
    price: 3600,
    fair_wage_amount: 2100,
    artisan_name: "Budhram Ghadwa",
    state: "Chhattisgarh",
    gi_tag: "GI-CG-083",
    image_url: "https://images.unsplash.com/photo-1582562124811-c09040d0a901?auto=format&fit=crop&w=600&q=80",
    stock_quantity: 8,
  },
  {
    id: "p4",
    title: "Tanjore 22K Gold Foil Sacred Temple Artwork",
    category: "Paintings & Folk Art",
    price: 8900,
    fair_wage_amount: 5200,
    artisan_name: "Rajagopal Achari",
    state: "Tamil Nadu",
    gi_tag: "GI-TN-022",
    image_url: "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=600&q=80",
    stock_quantity: 3,
  },
  {
    id: "p5",
    title: "Jaipur Traditional Cobalt Floral Blue Pottery Vase",
    category: "Pottery & Clay",
    price: 2400,
    fair_wage_amount: 1300,
    artisan_name: "Kailash Chand Kumhar",
    state: "Rajasthan",
    gi_tag: "GI-RJ-045",
    image_url: "https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?auto=format&fit=crop&w=600&q=80",
    stock_quantity: 15,
  },
  {
    id: "p6",
    title: "Bidriware Pure Silver Wire Inlay Decorative Plate",
    category: "Metal & Bell Craft",
    price: 4500,
    fair_wage_amount: 2700,
    artisan_name: "Mohammed Rashid",
    state: "Karnataka",
    gi_tag: "GI-KA-019",
    image_url: "https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=600&q=80",
    stock_quantity: 7,
  },
];

const CATEGORIES = [
  "All Categories",
  "Pottery & Clay",
  "Handloom & Textiles",
  "Metal & Bell Craft",
  "Paintings & Folk Art",
];

export default function CatalogPage() {
  const [products, setProducts] = useState<Product[]>(FALLBACK_PRODUCTS);
  const [selectedCategory, setSelectedCategory] = useState("All Categories");
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState("newest");
  const [loading, setLoading] = useState(false);
  const [cartSuccess, setCartSuccess] = useState<string | null>(null);

  useEffect(() => {
    // Attempt fetch from backend marketplace API
    api.get<Product[]>("/marketplace/products")
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) {
          setProducts(data);
        }
      })
      .catch(() => {
        // Fallback to verified seeded catalog
      });
  }, []);

  const filteredProducts = products.filter((p) => {
    const matchesCategory =
      selectedCategory === "All Categories" || p.category.toLowerCase().includes(selectedCategory.toLowerCase());
    const matchesSearch =
      p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.artisan_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.state.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const addToCart = (product: Product) => {
    // Read local cart
    const existingCart = JSON.parse(localStorage.getItem("craftlens_cart") || "[]");
    const foundIndex = existingCart.findIndex((item: any) => item.id === product.id);
    if (foundIndex > -1) {
      existingCart[foundIndex].quantity += 1;
    } else {
      existingCart.push({ ...product, quantity: 1 });
    }
    localStorage.setItem("craftlens_cart", JSON.stringify(existingCart));
    setCartSuccess(product.title);
    setTimeout(() => setCartSuccess(null), 3000);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Page Title & Search Bar */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-craft-text tracking-tight">
            Discover Authentic Indian Crafts
          </h1>
          <p className="text-xs sm:text-sm text-craft-muted mt-1">
            Every piece is verified for authentic GI heritage and fair living wage compliance.
          </p>
        </div>

        {/* Search */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-craft-muted" />
          <input
            type="text"
            placeholder="Search by craft, artisan or state..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-craft-surface border border-craft-border text-xs focus:outline-none focus:border-craft-primary"
          />
        </div>
      </div>

      {/* Notification Toast */}
      {cartSuccess && (
        <div className="p-3 bg-craft-success/10 border border-craft-success/30 rounded-lg text-craft-success text-xs font-semibold flex items-center justify-between">
          <span>✓ Added "{cartSuccess}" to your shopping bag!</span>
          <Link href="/cart" className="underline font-bold">View Bag</Link>
        </div>
      )}

      {/* Filter and Sorting Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-craft-border">
        {/* Categories */}
        <div className="flex flex-wrap gap-2">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                selectedCategory === cat
                  ? "bg-craft-primary text-white"
                  : "bg-craft-surface border border-craft-border text-craft-text hover:bg-craft-surface-hover"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Sort Selector */}
        <div className="flex items-center space-x-2 text-xs text-craft-muted">
          <span>Sort:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="bg-craft-surface border border-craft-border rounded-md px-2 py-1.5 text-xs text-craft-text focus:outline-none"
          >
            <option value="newest">Newest Arrivals</option>
            <option value="price-asc">Price: Low to High</option>
            <option value="price-desc">Price: High to Low</option>
            <option value="wage">Highest Fair Wage %</option>
          </select>
        </div>
      </div>

      {/* Product Grid */}
      {filteredProducts.length === 0 ? (
        <div className="text-center py-16 bg-craft-surface rounded-xl border border-craft-border">
          <p className="text-sm font-semibold text-craft-text">No crafts found matching your search</p>
          <p className="text-xs text-craft-muted mt-1">Try clearing filters or search terms</p>
          <button
            onClick={() => { setSelectedCategory("All Categories"); setSearchQuery(""); }}
            className="mt-4 px-4 py-2 bg-craft-primary text-white text-xs rounded-md"
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map((p) => (
            <div
              key={p.id}
              className="bg-craft-surface rounded-xl overflow-hidden border border-craft-border shadow-subtle hover:shadow-card transition-all flex flex-col justify-between"
            >
              <div>
                {/* Image */}
                <div className="h-56 overflow-hidden relative group">
                  <img
                    src={p.image_url}
                    alt={p.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  {p.gi_tag && (
                    <div className="absolute top-2 left-2 px-2.5 py-1 bg-craft-surface/90 backdrop-blur-md rounded-md text-[10px] font-bold text-craft-primary border border-craft-border flex items-center space-x-1 shadow-subtle">
                      <ShieldCheck className="w-3.5 h-3.5 text-craft-success" />
                      <span>{p.gi_tag}</span>
                    </div>
                  )}
                  <Link
                    href={`/heritage/${p.id}`}
                    className="absolute top-2 right-2 px-2 py-1 bg-craft-surface/90 backdrop-blur-md rounded-md text-[10px] font-semibold text-craft-text hover:text-craft-primary border border-craft-border shadow-subtle flex items-center space-x-1"
                  >
                    <Eye className="w-3 h-3" />
                    <span>Verify QR</span>
                  </Link>
                </div>

                {/* Details */}
                <div className="p-5 space-y-2">
                  <div className="flex justify-between items-start">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-craft-secondary">
                      {p.category}
                    </span>
                    <span className="text-[10px] font-medium text-craft-muted">
                      {p.state}
                    </span>
                  </div>

                  <h3 className="font-bold text-sm text-craft-text line-clamp-2 hover:text-craft-primary cursor-pointer">
                    {p.title}
                  </h3>

                  <p className="text-xs text-craft-muted">
                    Crafted by <span className="font-semibold text-craft-text">{p.artisan_name}</span>
                  </p>

                  <div className="pt-2 flex items-baseline justify-between">
                    <div>
                      <span className="text-[10px] text-craft-muted block">Direct Price:</span>
                      <span className="text-base font-extrabold text-craft-primary">₹{p.price}</span>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] text-craft-muted block">Artisan Fair Wage:</span>
                      <span className="text-xs font-bold text-craft-success">₹{p.fair_wage_amount}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="p-5 pt-0 grid grid-cols-2 gap-2">
                <button
                  onClick={() => addToCart(p)}
                  className="py-2.5 px-3 rounded-lg bg-craft-primary text-white text-xs font-semibold hover:bg-craft-primary-dark transition-colors flex items-center justify-center space-x-1.5 shadow-subtle"
                >
                  <ShoppingBag className="w-3.5 h-3.5" />
                  <span>Add to Bag</span>
                </button>
                <Link
                  href={`/b2b?rfq_product=${p.id}&title=${encodeURIComponent(p.title)}`}
                  className="py-2.5 px-3 rounded-lg bg-craft-background border border-craft-border text-craft-secondary text-xs font-semibold hover:bg-craft-surface-hover transition-colors text-center"
                >
                  B2B Bulk Quote
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

