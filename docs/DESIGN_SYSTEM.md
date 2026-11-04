# CraftLens 2.0 Design System Specification

## 1. Design Philosophy: Modern Artisan Commerce

CraftLens avoids noisy gradients, neon colors, and generic corporate templates. Instead, it embodies a **grounded, warm, and sophisticated craft aesthetic** inspired by:
- **Etsy**: Sensibility for handcrafted textures and maker stories.
- **Shopify**: Flawless, friction-free commerce workflows.
- **Airbnb**: Breathable spacing, crisp imagery, and editorial typography.
- **Linear**: Clean borders, predictable micro-interactions, and visual discipline.

---

## 2. Color Palette & Semantic Tokens

| Token Name | Hex Code | HSL / RGB | Purpose / Usage |
| :--- | :--- | :--- | :--- |
| `color-primary` | `#285C45` | `rgb(40, 92, 69)` | Deep Forest Green; brand identity, primary CTA, active states |
| `color-primary-dark` | `#1C4332` | `rgb(28, 67, 50)` | Hover and active state for primary buttons |
| `color-secondary` | `#C47B52` | `rgb(196, 123, 82)` | Warm Terracotta; accents, highlights, badges, craft motifs |
| `color-background` | `#F8F6F0` | `rgb(248, 246, 240)` | Warm Ivory; core canvas background, prevents eye fatigue |
| `color-surface` | `#FFFFFF` | `rgb(255, 255, 255)` | Pure White; card containers, modal dialogs, input surfaces |
| `color-surface-hover` | `#F3EFE6` | `rgb(243, 239, 230)` | Subtle table row & card hover tone |
| `color-text-primary` | `#242B27` | `rgb(36, 43, 39)` | Dark Charcoal; primary headings, readable body text |
| `color-text-muted` | `#858B83` | `rgb(133, 139, 131)` | Muted Sand/Sage; captions, secondary labels, helper text |
| `color-border` | `#E8E5DC` | `rgb(232, 229, 220)` | Natural Beige; subtle dividers, card outlines, form borders |
| `color-success` | `#32815A` | `rgb(50, 129, 90)` | Order confirmed, verified badge, in-stock indicator |
| `color-warning` | `#D69B43` | `rgb(214, 155, 67)` | Low stock, pending verification, quotation review |
| `color-error` | `#C6534B` | `rgb(198, 83, 75)` | Destructive action, payment failed, quality rejection |

---

## 3. Typography Hierarchy

### Font Family
- **English / Latin**: `Inter`, `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
- **Indic Script Support**:
  - Tamil: `Noto Sans Tamil` / system font
  - Hindi / Devanagari: `Noto Sans Devanagari`
  - Telugu: `Noto Sans Telugu`
  - Kannada: `Noto Sans Kannada`
  - Malayalam: `Noto Sans Malayalam`

### Scale & Tokens
- **Display 1**: `2.25rem (36px)` / Leading `1.2` / Weight `700` (Hero titles, marketing banners)
- **Heading 1**: `1.875rem (30px)` / Leading `1.25` / Weight `600` (Section headers)
- **Heading 2**: `1.5rem (24px)` / Leading `1.3` / Weight `600` (Card headers, modal titles)
- **Heading 3**: `1.25rem (20px)` / Leading `1.4` / Weight `600` (Sub-sections, metric callouts)
- **Body Large**: `1.125rem (18px)` / Leading `1.5` / Weight `400 / 500`
- **Body Base**: `1.0rem (16px)` / Leading `1.5` / Weight `400` (Standard content)
- **Body Small**: `0.875rem (14px)` / Leading `1.4` / Weight `400 / 500` (Tables, secondary notes)
- **Caption**: `0.75rem (12px)` / Leading `1.3` / Weight `500` (Badges, timestamps)

---

## 4. Spacing, Elevation & Corner Radii

- **Base Spacing Grid**: `4px` increments (`4px`, `8px`, `12px`, `16px`, `24px`, `32px`, `48px`, `64px`).
- **Border Radius**:
  - `rounded-sm`: `4px` (Tags, small indicators)
  - `rounded-md`: `8px` (Inputs, select dropdowns, buttons)
  - `rounded-lg`: `12px` (Cards, dialogs, media previews)
  - `rounded-xl`: `16px` (Floating sheets, hero cards)
- **Elevation / Shadows**:
  - Muted, diffuse shadows that prevent harsh contrasts against Warm Ivory (`#F8F6F0`):
  - `shadow-subtle`: `0 1px 3px 0 rgba(36, 43, 39, 0.05), 0 1px 2px -1px rgba(36, 43, 39, 0.05)`
  - `shadow-card`: `0 4px 6px -1px rgba(36, 43, 39, 0.07), 0 2px 4px -2px rgba(36, 43, 39, 0.05)`
  - `shadow-modal`: `0 20px 25px -5px rgba(36, 43, 39, 0.1), 0 8px 10px -6px rgba(36, 43, 39, 0.05)`

---

## 5. UI/UX Rules for Low-Literacy Artisan Accessibility

1. **Voice-Assisted Cues**: Every critical action (Take Photo, Price Recommendation, Order Confirmation) features high-contrast iconography and audio play/prompt cues.
2. **Minimal Text Fields**: Prefer numerical steppers, chip pickers, and voice transcription over keyboard typing.
3. **Optimistic Visual States**: Instant feedback on image capture and draft saving with persistent offline cues.
4. **No Technical Jargon**: Use "Fair Selling Price" instead of "Algorithmic Pricing Margin"; "Total Units" instead of "Inventory SKU Allocation".
