"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Trash2, ShieldCheck, HeartHandshake, CheckCircle2, ArrowRight } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export default function CartPage() {
  const { user } = useAuth();
  const [cart, setCart] = useState<any[]>([]);
  const [address, setAddress] = useState({
    name: user?.full_name || "Anita Roy",
    phone: "+91 98450 12345",
    street: "Flat 402, Lotus Greens, Indiranagar",
    city: "Bengaluru",
    state: "Karnataka",
    pincode: "560038",
  });
  const [paymentMethod, setPaymentMethod] = useState("upi");
  const [orderConfirmed, setOrderConfirmed] = useState<any | null>(null);

  useEffect(() => {
    const saved = localStorage.getItem("craftlens_cart");
    if (saved) {
      try {
        setCart(JSON.parse(saved));
      } catch (e) {
        setCart([]);
      }
    }
  }, []);

  const updateQuantity = (id: string, delta: number) => {
    const updated = cart
      .map((item) => {
        if (item.id === id) {
          const newQty = item.quantity + delta;
          return newQty > 0 ? { ...item, quantity: newQty } : null;
        }
        return item;
      })
      .filter(Boolean);

    setCart(updated);
    localStorage.setItem("craftlens_cart", JSON.stringify(updated));
  };

  const removeItem = (id: string) => {
    const updated = cart.filter((item) => item.id !== id);
    setCart(updated);
    localStorage.setItem("craftlens_cart", JSON.stringify(updated));
  };

  const subtotal = cart.reduce((acc, item) => acc + item.price * item.quantity, 0);
  const fairWageTotal = cart.reduce(
    (acc, item) => acc + (item.fair_wage_amount || Math.round(item.price * 0.6)) * item.quantity,
    0
  );
  const shipping = subtotal > 1500 || subtotal === 0 ? 0 : 120;
  const total = subtotal + shipping;

  const handleCheckout = (e: React.FormEvent) => {
    e.preventDefault();
    const orderData = {
      orderId: "CL-" + Math.floor(100000 + Math.random() * 900000),
      items: cart,
      subtotal,
      fairWageTotal,
      shipping,
      total,
      address,
      paymentMethod,
      date: new Date().toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric",
      }),
      trackingHash: "provenance-" + Math.random().toString(36).substring(2, 10),
    };

    setOrderConfirmed(orderData);
    setCart([]);
    localStorage.removeItem("craftlens_cart");
  };

  if (orderConfirmed) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center space-y-6">
        <div className="w-16 h-16 rounded-full bg-craft-success/10 text-craft-success mx-auto flex items-center justify-center">
          <CheckCircle2 className="w-10 h-10" />
        </div>
        <h1 className="text-3xl font-extrabold text-craft-text">Order Confirmed!</h1>
        <p className="text-xs sm:text-sm text-craft-muted">
          Your order <span className="font-bold text-craft-primary">{orderConfirmed.orderId}</span> has been dispatched to the artisan cluster.
        </p>

        <div className="bg-craft-surface border border-craft-border rounded-xl p-6 text-left space-y-4 shadow-subtle">
          <div className="flex justify-between items-center border-b border-craft-border pb-3">
            <span className="text-xs text-craft-muted">Delivery To</span>
            <span className="text-xs font-semibold text-craft-text">{orderConfirmed.address.name} ({orderConfirmed.address.city})</span>
          </div>
          <div className="flex justify-between items-center border-b border-craft-border pb-3">
            <span className="text-xs text-craft-muted">Direct Artisan Fair Wage</span>
            <span className="text-xs font-bold text-craft-success">₹{orderConfirmed.fairWageTotal}</span>
          </div>
          <div className="flex justify-between items-center border-b border-craft-border pb-3">
            <span className="text-xs text-craft-muted">Total Paid</span>
            <span className="text-base font-extrabold text-craft-primary">₹{orderConfirmed.total}</span>
          </div>
          <div className="pt-2 flex items-center justify-between">
            <span className="text-xs text-craft-muted">Provenance Hash:</span>
            <Link
              href={`/heritage/${orderConfirmed.trackingHash}`}
              className="text-xs font-semibold text-craft-secondary underline"
            >
              {orderConfirmed.trackingHash} (Verify QR)
            </Link>
          </div>
        </div>

        <Link
          href="/catalog"
          className="inline-flex items-center space-x-2 px-6 py-3 rounded-lg bg-craft-primary text-white text-xs font-semibold hover:bg-craft-primary-dark transition-colors"
        >
          <span>Continue Discovering Crafts</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-craft-text">Your Shopping Bag</h1>
        <p className="text-xs sm:text-sm text-craft-muted mt-1">
          Review your authentic handmade selections and direct artisan payouts.
        </p>
      </div>

      {cart.length === 0 ? (
        <div className="text-center py-20 bg-craft-surface rounded-xl border border-craft-border space-y-4">
          <p className="text-sm font-semibold text-craft-text">Your shopping bag is empty</p>
          <p className="text-xs text-craft-muted">Support master artisans and discover unique crafts.</p>
          <Link
            href="/catalog"
            className="inline-block px-5 py-2.5 rounded-lg bg-craft-primary text-white text-xs font-semibold hover:bg-craft-primary-dark"
          >
            Browse Catalog
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Cart Items */}
          <div className="lg:col-span-7 space-y-4">
            {cart.map((item) => (
              <div
                key={item.id}
                className="bg-craft-surface border border-craft-border rounded-xl p-4 flex space-x-4 shadow-subtle"
              >
                <img
                  src={item.image_url}
                  alt={item.title}
                  className="w-24 h-24 rounded-lg object-cover border border-craft-border flex-shrink-0"
                />
                <div className="flex-1 flex flex-col justify-between">
                  <div>
                    <div className="flex justify-between items-start">
                      <h3 className="font-bold text-sm text-craft-text line-clamp-1">{item.title}</h3>
                      <button
                        onClick={() => removeItem(item.id)}
                        className="text-craft-muted hover:text-craft-error p-1"
                        title="Remove"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                    <p className="text-xs text-craft-muted mt-0.5">By {item.artisan_name}</p>
                    {item.gi_tag && (
                      <span className="inline-flex items-center space-x-1 text-[10px] text-craft-success font-semibold mt-1">
                        <ShieldCheck className="w-3 h-3" />
                        <span>{item.gi_tag} Certified</span>
                      </span>
                    )}
                  </div>

                  <div className="flex justify-between items-center mt-3">
                    <div className="flex items-center space-x-2 border border-craft-border rounded-md px-2 py-1 bg-craft-background">
                      <button
                        onClick={() => updateQuantity(item.id, -1)}
                        className="text-xs font-bold text-craft-text px-1 hover:text-craft-primary"
                      >
                        -
                      </button>
                      <span className="text-xs font-semibold px-2">{item.quantity}</span>
                      <button
                        onClick={() => updateQuantity(item.id, 1)}
                        className="text-xs font-bold text-craft-text px-1 hover:text-craft-primary"
                      >
                        +
                      </button>
                    </div>

                    <div className="text-right">
                      <span className="text-sm font-extrabold text-craft-primary">
                        ₹{item.price * item.quantity}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}

            {/* Impact Banner */}
            <div className="bg-craft-success/10 border border-craft-success/20 rounded-xl p-4 flex items-center space-x-3 text-craft-success">
              <HeartHandshake className="w-6 h-6 flex-shrink-0" />
              <div>
                <p className="text-xs font-bold">100% Transparent Fair Living Wages</p>
                <p className="text-[11px] text-craft-muted mt-0.5">
                  ₹{fairWageTotal} of your purchase will be transferred directly to the artisans upon dispatch.
                </p>
              </div>
            </div>
          </div>

          {/* Checkout & Summary */}
          <div className="lg:col-span-5 bg-craft-surface border border-craft-border rounded-xl p-6 shadow-subtle space-y-6">
            <h2 className="font-bold text-base text-craft-text pb-2 border-b border-craft-border">
              Order Summary & Delivery
            </h2>

            <form onSubmit={handleCheckout} className="space-y-4">
              <div className="space-y-3">
                <label className="text-xs font-semibold text-craft-text block">Shipping Address</label>
                <input
                  type="text"
                  required
                  placeholder="Full Name"
                  value={address.name}
                  onChange={(e) => setAddress({ ...address, name: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-craft-background border border-craft-border text-xs focus:outline-none focus:border-craft-primary"
                />
                <input
                  type="text"
                  required
                  placeholder="Contact Phone"
                  value={address.phone}
                  onChange={(e) => setAddress({ ...address, phone: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-craft-background border border-craft-border text-xs focus:outline-none focus:border-craft-primary"
                />
                <input
                  type="text"
                  required
                  placeholder="Street / Flat / House Address"
                  value={address.street}
                  onChange={(e) => setAddress({ ...address, street: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-craft-background border border-craft-border text-xs focus:outline-none focus:border-craft-primary"
                />
                <div className="grid grid-cols-3 gap-2">
                  <input
                    type="text"
                    required
                    placeholder="City"
                    value={address.city}
                    onChange={(e) => setAddress({ ...address, city: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-craft-background border border-craft-border text-xs focus:outline-none focus:border-craft-primary"
                  />
                  <input
                    type="text"
                    required
                    placeholder="State"
                    value={address.state}
                    onChange={(e) => setAddress({ ...address, state: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-craft-background border border-craft-border text-xs focus:outline-none focus:border-craft-primary"
                  />
                  <input
                    type="text"
                    required
                    placeholder="Pincode"
                    value={address.pincode}
                    onChange={(e) => setAddress({ ...address, pincode: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-craft-background border border-craft-border text-xs focus:outline-none focus:border-craft-primary"
                  />
                </div>
              </div>

              {/* Payment Method */}
              <div className="space-y-2 pt-2">
                <label className="text-xs font-semibold text-craft-text block">Payment Mode</label>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <button
                    type="button"
                    onClick={() => setPaymentMethod("upi")}
                    className={`py-2 px-3 rounded-lg border text-left font-medium ${
                      paymentMethod === "upi"
                        ? "border-craft-primary bg-craft-background text-craft-primary font-bold"
                        : "border-craft-border text-craft-text"
                    }`}
                  >
                    UPI / QR Code
                  </button>
                  <button
                    type="button"
                    onClick={() => setPaymentMethod("cards")}
                    className={`py-2 px-3 rounded-lg border text-left font-medium ${
                      paymentMethod === "cards"
                        ? "border-craft-primary bg-craft-background text-craft-primary font-bold"
                        : "border-craft-border text-craft-text"
                    }`}
                  >
                    Card / NetBanking
                  </button>
                </div>
              </div>

              {/* Breakdown */}
              <div className="border-t border-craft-border pt-4 space-y-2 text-xs text-craft-muted">
                <div className="flex justify-between">
                  <span>Subtotal</span>
                  <span className="text-craft-text font-semibold">₹{subtotal}</span>
                </div>
                <div className="flex justify-between">
                  <span>Shipping</span>
                  <span className="text-craft-text font-semibold">
                    {shipping === 0 ? "FREE" : `₹${shipping}`}
                  </span>
                </div>
                <div className="flex justify-between text-craft-success font-semibold">
                  <span>Artisan Fair Wage</span>
                  <span>₹{fairWageTotal}</span>
                </div>
                <div className="flex justify-between text-base font-extrabold text-craft-primary pt-2 border-t border-craft-border">
                  <span>Total</span>
                  <span>₹{total}</span>
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-3 rounded-lg bg-craft-primary text-white text-xs font-bold hover:bg-craft-primary-dark shadow-subtle transition-all"
              >
                Place Order & Direct Pay (₹{total})
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
