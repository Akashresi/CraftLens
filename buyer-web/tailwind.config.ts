import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        craft: {
          primary: "#285C45",       // Deep Forest Green
          "primary-dark": "#1C4332",
          secondary: "#C47B52",     // Warm Terracotta
          background: "#F8F6F0",    // Warm Ivory
          surface: "#FFFFFF",       // Pure White
          "surface-hover": "#F3EFE6",
          text: "#242B27",          // Dark Charcoal
          muted: "#858B83",         // Muted Sand / Sage
          border: "#E8E5DC",        // Natural Beige
          success: "#32815A",
          warning: "#D69B43",
          error: "#C6534B",
        },
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
      },
      boxShadow: {
        subtle: "0 1px 3px 0 rgba(36, 43, 39, 0.05), 0 1px 2px -1px rgba(36, 43, 39, 0.05)",
        card: "0 4px 6px -1px rgba(36, 43, 39, 0.07), 0 2px 4px -2px rgba(36, 43, 39, 0.05)",
        modal: "0 20px 25px -5px rgba(36, 43, 39, 0.1), 0 8px 10px -6px rgba(36, 43, 39, 0.05)",
      },
    },
  },
  plugins: [],
};
export default config;

