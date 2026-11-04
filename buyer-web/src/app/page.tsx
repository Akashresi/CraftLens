import React from "react";
import Link from "next/link";
import { Sparkles, ShieldCheck, HeartHandshake, Mic, Camera, ArrowRight, Award, Compass } from "lucide-react";

const FEATURED_CRAFTS = [
  {
    id: "pottery",
    title: "Terracotta & Clay Art",
    region: "Bankura, West Bengal & Vilachery, Tamil Nadu",
    image: "https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?auto=format&fit=crop&w=600&q=80",
    description: "Centuries-old wheel pottery kiln-fired with organic husk and natural earthen glazes.",
  },
  {
    id: "handloom",
    title: "Handloom Weaves & Silk",
    region: "Kanchipuram, Tamil Nadu & Varanasi, Uttar Pradesh",
    image: "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=600&q=80",
    description: "Pure mulberry silk handwoven on traditional pit looms with authentic pure zari motifs.",
  },
  {
    id: "brass",
    title: "Dokra Lost-Wax Bell Metal",
    region: "Bastar, Chhattisgarh",
    image: "https://images.unsplash.com/photo-1582562124811-c09040d0a901?auto=format&fit=crop&w=600&q=80",
    description: "Non-ferrous metal casting using the ancient 4,000-year-old Indus Valley lost-wax technique.",
  },
  {
    id: "painting",
    title: "Tanjore Gold Foil Painting",
    region: "Thanjavur, Tamil Nadu",
    image: "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=600&q=80",
    description: "Sacred artwork embellished with 22-carat gold foil leaf and semi-precious Jaipur gems.",
  },
];

const CURATED_PRODUCTS = [
  {
    id: "prod-1",
    title: "Handcrafted Vilachery Terracotta Ayyanar Figurine",
    artisan: "Meenakshi Sundaram",
    cluster: "Vilachery Pottery Cluster, Madurai, TN",
    price: 1850,
    fairWage: 950,
    giTag: "GI-TN-412",
    image: "https://images.unsplash.com/photo-1578749556568-bc2c40e68b61?auto=format&fit=crop&w=600&q=80",
  },
  {
    id: "prod-2",
    title: "Kanchipuram Traditional Korvai Mulberry Silk Saree",
    artisan: "Ramanathan Weavers Cooperative",
    cluster: "Kanchipuram Handloom Society, TN",
    price: 14200,
    fairWage: 8200,
    giTag: "GI-TN-001",
    image: "https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?auto=format&fit=crop&w=600&q=80",
  },
  {
    id: "prod-3",
    title: "Bastar Tribal Dokra Brass Sun Chariot",
    artisan: "Budhram Ghadwa",
    cluster: "Kondagaon Craft Shilp, CG",
    price: 3600,
    fairWage: 2100,
    giTag: "GI-CG-083",
    image: "https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=600&q=80",
  },
];

export default function HomePage() {
  return (
    <div className="space-y-16 pb-12">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-craft-background border-b border-craft-border py-16 lg:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            <div className="lg:col-span-7 space-y-6">
              <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-craft-surface border border-craft-border text-xs font-semibold text-craft-primary shadow-subtle">
                <Sparkles className="w-3.5 h-3.5 text-craft-secondary" />
                <span>Next-Generation Artisan Commerce Platform</span>
              </div>
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-craft-text tracking-tight leading-[1.15]">
                Preserving Heritage. <br />
                <span className="text-craft-primary">Empowering Hands.</span> <br />
                Connecting Worlds.
              </h1>
              <p className="text-base sm:text-lg text-craft-muted leading-relaxed max-w-xl">
                CraftLens empowers traditional Indian artisans with AI camera studios, voice cataloging in regional languages, explainable fair wage pricing, and tamper-evident GI provenance verification.
              </p>
              <div className="flex flex-wrap gap-4 pt-2">
                <Link
                  href="/catalog"
                  className="px-6 py-3.5 rounded-lg bg-craft-primary text-white font-semibold text-sm shadow-subtle hover:bg-craft-primary-dark transition-all flex items-center space-x-2"
                >
                  <span>Explore Verified Crafts</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
                <Link
                  href="/artisan/studio"
                  className="px-6 py-3.5 rounded-lg bg-craft-surface border border-craft-border text-craft-text font-semibold text-sm shadow-subtle hover:bg-craft-surface-hover transition-all flex items-center space-x-2"
                >
                  <Camera className="w-4 h-4 text-craft-secondary" />
                  <span>Artisan AI Studio</span>
                </Link>
                <Link
                  href="/b2b"
                  className="px-6 py-3.5 rounded-lg bg-craft-surface border border-craft-border text-craft-secondary font-semibold text-sm shadow-subtle hover:bg-craft-surface-hover transition-all"
                >
                  <span>Wholesale & B2B RFQ</span>
                </Link>
              </div>
            </div>

            <div className="lg:col-span-5 relative">
              <div className="relative rounded-2xl overflow-hidden border border-craft-border shadow-modal bg-craft-surface p-2">
                <img
                  src="https://images.unsplash.com/photo-1544717305-2782549b5136?auto=format&fit=crop&w=800&q=80"
                  alt="Traditional Indian Artisan weaving"
                  className="rounded-xl w-full h-[400px] object-cover"
                />
                <div className="absolute bottom-6 left-6 right-6 bg-craft-surface/95 backdrop-blur-md p-4 rounded-xl border border-craft-border shadow-card flex items-center justify-between">
                  <div>
                    <div className="flex items-center space-x-1.5 text-xs font-bold text-craft-primary">
                      <ShieldCheck className="w-4 h-4 text-craft-success" />
                      <span>100% Cryptographic GI Provenance</span>
                    </div>
                    <p className="text-xs text-craft-muted mt-0.5">
                      Direct-from-Maker • No Exploitative Intermediaries
                    </p>
                  </div>
                  <span className="text-xs font-bold px-2.5 py-1 bg-craft-background rounded-md text-craft-secondary border border-craft-border">
                    Living Wage Verified
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Trust & Empowerment Pillars */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-craft-surface p-6 rounded-xl border border-craft-border shadow-subtle flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded-lg bg-craft-background flex items-center justify-center text-craft-primary mb-4 border border-craft-border">
                <Camera className="w-5 h-5 text-craft-primary" />
              </div>
              <h3 className="font-bold text-craft-text mb-2 text-base">In-App AI Studio</h3>
              <p className="text-xs text-craft-muted leading-relaxed">
                Automated blur detection, background isolation, studio shadow compositing, and CLAHE lighting enhancement directly from any smartphone.
              </p>
            </div>
          </div>

          <div className="bg-craft-surface p-6 rounded-xl border border-craft-border shadow-subtle flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded-lg bg-craft-background flex items-center justify-center text-craft-secondary mb-4 border border-craft-border">
                <Mic className="w-5 h-5 text-craft-secondary" />
              </div>
              <h3 className="font-bold text-craft-text mb-2 text-base">Multilingual Voice AI</h3>
              <p className="text-xs text-craft-muted leading-relaxed">
                Artisans speak naturally in Tamil, Hindi, Telugu, Kannada, or Malayalam. AI extracts truthful craft descriptions and generates English and SEO catalogs.
              </p>
            </div>
          </div>

          <div className="bg-craft-surface p-6 rounded-xl border border-craft-border shadow-subtle flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded-lg bg-craft-background flex items-center justify-center text-craft-success mb-4 border border-craft-border">
                <HeartHandshake className="w-5 h-5 text-craft-success" />
              </div>
              <h3 className="font-bold text-craft-text mb-2 text-base">Fair Living Wage Engine</h3>
              <p className="text-xs text-craft-muted leading-relaxed">
                Transparent price calculator guaranteeing that artisans receive a fair wage for every hour invested, preventing market undercutting.
              </p>
            </div>
          </div>

          <div className="bg-craft-surface p-6 rounded-xl border border-craft-border shadow-subtle flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded-lg bg-craft-background flex items-center justify-center text-craft-primary mb-4 border border-craft-border">
                <Award className="w-5 h-5 text-craft-primary" />
              </div>
              <h3 className="font-bold text-craft-text mb-2 text-base">Verifiable QR Seal</h3>
              <p className="text-xs text-craft-muted leading-relaxed">
                Tamper-evident SHA-256 maker signature on every package. Consumers scan the QR code to verify cluster authenticity and see the maker's story.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Craft Traditions */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-end mb-8">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-craft-secondary">
              Heritage Clusters
            </span>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-craft-text mt-1">
              Explore Living Indian Traditions
            </h2>
          </div>
          <Link
            href="/catalog"
            className="text-sm font-semibold text-craft-primary hover:underline flex items-center space-x-1"
          >
            <span>View All Clusters</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {FEATURED_CRAFTS.map((craft) => (
            <div
              key={craft.id}
              className="bg-craft-surface rounded-xl overflow-hidden border border-craft-border shadow-subtle group hover:shadow-card transition-all"
            >
              <div className="h-48 overflow-hidden relative">
                <img
                  src={craft.image}
                  alt={craft.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
              </div>
              <div className="p-5">
                <span className="text-[10px] font-semibold text-craft-secondary uppercase tracking-wider block mb-1">
                  {craft.region}
                </span>
                <h3 className="font-bold text-base text-craft-text group-hover:text-craft-primary transition-colors">
                  {craft.title}
                </h3>
                <p className="text-xs text-craft-muted mt-2 leading-relaxed">
                  {craft.description}
                </p>
                <div className="mt-4 pt-3 border-t border-craft-border flex items-center justify-between">
                  <Link
                    href={`/catalog?craft=${craft.id}`}
                    className="text-xs font-semibold text-craft-primary hover:underline flex items-center space-x-1"
                  >
                    <span>Discover Works</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Curated Products with Transparent Fair Wage */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-craft-surface rounded-2xl border border-craft-border p-8 shadow-card">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-8 gap-4">
            <div>
              <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded bg-craft-background text-craft-primary text-xs font-bold border border-craft-border mb-2">
                <Compass className="w-3.5 h-3.5 text-craft-secondary" />
                <span>Ethical Commerce in Action</span>
              </div>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-craft-text">
                Direct from Master Artisans
              </h2>
              <p className="text-xs sm:text-sm text-craft-muted mt-1">
                Every purchase shows exactly how much goes directly to the creator as verified fair wages.
              </p>
            </div>
            <Link
              href="/catalog"
              className="px-4 py-2 rounded-lg bg-craft-primary text-white text-xs font-semibold hover:bg-craft-primary-dark transition-colors"
            >
              Browse Full Catalog
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {CURATED_PRODUCTS.map((prod) => (
              <div
                key={prod.id}
                className="bg-craft-background rounded-xl p-4 border border-craft-border flex flex-col justify-between"
              >
                <div>
                  <div className="h-52 rounded-lg overflow-hidden relative mb-4">
                    <img
                      src={prod.image}
                      alt={prod.title}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute top-2 left-2 px-2 py-1 bg-craft-surface/90 backdrop-blur-md rounded text-[10px] font-bold text-craft-primary border border-craft-border flex items-center space-x-1">
                      <ShieldCheck className="w-3 h-3 text-craft-success" />
                      <span>{prod.giTag}</span>
                    </div>
                  </div>
                  <h3 className="font-bold text-sm text-craft-text line-clamp-2">
                    {prod.title}
                  </h3>
                  <p className="text-xs text-craft-muted mt-1">
                    By <span className="font-semibold text-craft-text">{prod.artisan}</span>
                  </p>
                  <p className="text-[11px] text-craft-muted">
                    {prod.cluster}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-craft-border">
                  <div className="flex justify-between items-baseline mb-2">
                    <div>
                      <span className="text-xs text-craft-muted">Price: </span>
                      <span className="text-lg font-extrabold text-craft-primary">₹{prod.price}</span>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] text-craft-muted block">Direct Fair Wage:</span>
                      <span className="text-xs font-bold text-craft-success">₹{prod.fairWage}</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 mt-3">
                    <Link
                      href={`/catalog`}
                      className="text-center py-2 px-3 rounded-lg bg-craft-primary text-white text-xs font-semibold hover:bg-craft-primary-dark transition-colors"
                    >
                      View Details
                    </Link>
                    <Link
                      href={`/b2b?rfq=${prod.id}`}
                      className="text-center py-2 px-3 rounded-lg bg-craft-surface border border-craft-border text-craft-secondary text-xs font-semibold hover:bg-craft-surface-hover transition-colors"
                    >
                      Request Bulk
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Call to Action for Artisans and Cooperatives */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-craft-primary text-white rounded-2xl p-8 sm:p-12 relative overflow-hidden shadow-modal">
          <div className="relative z-10 max-w-2xl space-y-4">
            <span className="text-xs font-bold uppercase tracking-wider text-craft-secondary">
              Artisan Empowerment
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold leading-tight">
              Are you an artisan, weaver, or craft self-help group?
            </h2>
            <p className="text-sm sm:text-base text-gray-200 leading-relaxed">
              Join thousands of craftspeople who catalog their products using just their voice in their mother tongue. No complex software, no English barriers, and guaranteed fair living wages.
            </p>
            <div className="flex flex-wrap gap-4 pt-2">
              <Link
                href="/register"
                className="px-6 py-3 rounded-lg bg-craft-secondary text-white font-bold text-sm shadow-card hover:brightness-110 transition-all"
              >
                Register as Artisan
              </Link>
              <Link
                href="/artisan/studio"
                className="px-6 py-3 rounded-lg bg-white/10 hover:bg-white/20 border border-white/20 text-white font-semibold text-sm transition-all"
              >
                Try In-App Photo Studio
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
