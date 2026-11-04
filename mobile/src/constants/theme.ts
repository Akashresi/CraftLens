/**
 * CraftLens 2.0 Mobile Design System Tokens
 * Strict adherence to docs/DESIGN_SYSTEM.md
 */

export const Colors = {
  primary: "#285C45",       // Deep Forest Green
  primaryDark: "#1C4332",
  secondary: "#C47B52",     // Warm Terracotta
  background: "#F8F6F0",    // Warm Ivory
  surface: "#FFFFFF",       // Pure White
  surfaceHover: "#F3EFE6",
  text: "#242B27",          // Dark Charcoal
  muted: "#858B83",         // Muted Sand / Sage
  border: "#E8E5DC",        // Natural Beige
  success: "#32815A",
  warning: "#D69B43",
  error: "#C6534B",
};

export const Spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  base: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

export const BorderRadius = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  full: 9999,
};

export const Typography = {
  h1: { fontSize: 28, fontWeight: "700" as const, lineHeight: 34 },
  h2: { fontSize: 22, fontWeight: "600" as const, lineHeight: 28 },
  h3: { fontSize: 18, fontWeight: "600" as const, lineHeight: 24 },
  body: { fontSize: 16, fontWeight: "400" as const, lineHeight: 22 },
  bodyBold: { fontSize: 16, fontWeight: "600" as const, lineHeight: 22 },
  small: { fontSize: 14, fontWeight: "400" as const, lineHeight: 18 },
  caption: { fontSize: 12, fontWeight: "500" as const, lineHeight: 16 },
};

