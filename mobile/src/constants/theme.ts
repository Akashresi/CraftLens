/**
 * CraftLens 2.0 Mobile Design System Tokens
 * Accessible high-contrast palette (>= 4.5:1) & large low-literacy touch targets (>= 48dp).
 */

export const Colors = {
  primary: "#285C45",       // Deep Forest Green (8.0:1 vs white)
  primaryDark: "#1C4332",
  secondary: "#C47B52",     // Warm Terracotta accent
  secondaryDark: "#96512B", // High-contrast terracotta for white button text (5.7:1)
  background: "#F8F6F0",    // Warm Ivory
  surface: "#FFFFFF",       // Pure White
  surfaceHover: "#F3EFE6",
  text: "#242B27",          // Dark Charcoal (14.5:1)
  muted: "#565C55",         // Accessible Sage Slate (6.3:1 on white, 5.9:1 on ivory)
  border: "#E8E5DC",        // Natural Beige
  success: "#236946",       // Accessible green (6.6:1)
  warning: "#946200",       // Accessible amber (5.1:1)
  error: "#B43931",         // Accessible crimson (5.5:1)
};

export const TouchTargets = {
  minHeight: 52, // Exceeds 48dp WCAG/Android accessibility target for low-literacy field use
  iconButtonSize: 56,
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
