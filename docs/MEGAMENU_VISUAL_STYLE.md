# 🎨 Mega Menu - Visual Style Reference

## 🎯 Design System Overview

Your mega menu uses a cohesive design system with consistent colors, typography, spacing, and interactions.

---

## 🎨 Color Palette

### Primary Colors
```
┌─────────────────────────────────────┐
│ Burgundy Primary                    │
│ #730f33                             │
│ RGB: 115, 15, 51                    │
│ HSL: 331°, 77%, 26%                 │
│ Usage: Navbar background start      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Burgundy Dark (Gradient End)        │
│ #5a0a27                             │
│ RGB: 90, 10, 39                     │
│ HSL: 331°, 80%, 20%                 │
│ Usage: Navbar background end        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Gold Accent                         │
│ #bc935b                             │
│ RGB: 188, 147, 91                   │
│ HSL: 29°, 45%, 55%                  │
│ Usage: Active borders, hover accent │
└─────────────────────────────────────┘
```

### Text Colors
```
┌─────────────────────────────────────┐
│ Text Primary (White)                │
│ #ffffff                             │
│ RGB: 255, 255, 255                  │
│ Opacity: 1.0 (100%)                 │
│ Usage: Links, text, icons           │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Text Secondary                      │
│ rgba(255, 255, 255, 0.7)            │
│ Opacity: 0.7 (70%)                  │
│ Usage: Hover state text             │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Text Tertiary                       │
│ rgba(255, 255, 255, 0.5)            │
│ Opacity: 0.5 (50%)                  │
│ Usage: Disabled, inactive            │
└─────────────────────────────────────┘
```

### Background Colors
```
┌─────────────────────────────────────┐
│ Hover Background                    │
│ rgba(255, 255, 255, 0.1)            │
│ Opacity: 0.1 (10%)                  │
│ Usage: Link hover state              │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Scrolled Navbar Shadow              │
│ 0 4px 12px rgba(0, 0, 0, 0.15)      │
│ Usage: Depth effect when scrolled   │
└─────────────────────────────────────┘
```

---

## 🔤 Typography System

### Font Families
```
Primary Font: Inter
- Sans-serif
- Weights: 400 (regular), 500 (medium), 700 (bold)
- Used for: All text in navbar
- Fallback: -apple-system, BlinkMacSystemFont, 'Segoe UI'
- Provider: Google Fonts

Backup Fonts:
- 'Segoe UI' (Windows)
- 'Helvetica Neue' (Mac)
- 'Arial' (Universal fallback)
```

### Typography Scales

**Desktop (1024px+)**
```
Logo:           1.5rem (24px)   700 bold
Menu Items:     1rem    (16px)  500 medium
CTA Buttons:    0.95rem (15px)  500 medium
```

**Tablet (768px - 1024px)**
```
Logo:           1.3rem (21px)   700 bold
Menu Items:     0.95rem (15px)  500 medium
CTA Buttons:    0.9rem  (14px)  500 medium
```

**Mobile (<768px)**
```
Logo:           1.2rem (19px)   700 bold
Menu Items:     0.9rem  (14px)  500 medium
CTA Buttons:    0.85rem (13px)  500 medium
```

---

## 📏 Spacing System

### Base Unit: 0.25rem (4px)

```
0.25rem = 4px   (micro)
0.5rem  = 8px   (small)
0.75rem = 12px  (base)
1rem    = 16px  (medium)
1.25rem = 20px  (large)
2rem    = 32px  (extra large)
```

### Navbar Spacing

**Desktop**
```
Navbar padding:         1rem (16px) top/bottom
Logo padding:           1rem (16px) sides
Menu item gap:          0.5rem (8px)
Menu item padding:      0.75rem (12px) top/bottom
Menu item padding:      1rem (16px) left/right
CTA button gap:         0.75rem (12px)
Nav-container gap:      2rem (32px)
```

**Tablet**
```
Navbar padding:         0.8rem (12px) top/bottom
Logo padding:           0.8rem (12px) sides
Menu item gap:          0.4rem (6px)
Menu item padding:      0.6rem (10px) top/bottom
Menu item padding:      0.8rem (12px) left/right
CTA button gap:         0.6rem (10px)
```

**Mobile**
```
Navbar padding:         0.75rem (12px) top/bottom
Menu item gap:          0.3rem (5px)
Menu item padding:      0.6rem (10px) top/bottom
Menu item padding:      0.8rem (12px) left/right
Menu gap from top:      0.5rem (8px)
```

---

## 🎯 Borders & Outlines

### Active Link Border
```
Location:       Bottom of link
Color:          #bc935b (Gold)
Width:          2px
Position:       Bottom edge
Transition:     200ms ease-in-out
Animation:      Smooth fade-in on active
```

### Hover Border (Desktop)
```
Location:       Bottom of link
Color:          #bc935b (Gold)
Width:          2px
Transition:     150ms ease-in
Hover State:    Appears on hover
```

### Focus Outline (Keyboard Nav)
```
Color:          White (#ffffff)
Width:          2px
Offset:         2px
Style:          Solid
Browser:        Native focus-visible
```

---

## 🎬 Animations & Transitions

### Standard Transitions
```
Duration:       300ms
Easing:         ease-in-out
Properties:     color, background, border, transform
```

### Specific Animations

**Hover Effect**
```
Duration:       150ms
Easing:         ease-in
Properties:     background-color, border-bottom-color
```

**Link Active Border**
```
Duration:       200ms
Easing:         ease-out
Properties:     border-bottom-color
```

**Mobile Menu Open/Close**
```
Duration:       300ms
Easing:         ease-in-out
Properties:     display (fade), transform (slide)
```

**Scroll Effect**
```
Duration:       100ms (debounced)
Event:          scroll
Action:         Add/remove 'scrolled' class
```

### Scroll Behavior
```
Smooth Scroll:  Enabled for anchor links
Duration:       Auto (browser default)
Effect:         Smooth scrolling to section
```

---

## 🖱️ Interactive States

### Link States

**Default**
```
Background:     Transparent
Text Color:     #ffffff (1.0 opacity)
Border:         2px solid transparent (bottom)
Cursor:         pointer
```

**Hover (Desktop Only)**
```
Background:     rgba(255, 255, 255, 0.1)
Text Color:     #ffffff (1.0 opacity)
Border:         2px solid #bc935b (gold)
Cursor:         pointer
Transition:     150ms ease-in
```

**Active (Current Page)**
```
Background:     rgba(255, 255, 255, 0.1)
Text Color:     #ffffff (1.0 opacity)
Border:         2px solid #bc935b (gold)
Decoration:     Bold or brighter
```

**Focus (Keyboard)**
```
Background:     rgba(255, 255, 255, 0.1)
Outline:        2px solid white
Outline-offset: 2px
```

**Disabled**
```
Background:     Transparent
Text Color:     rgba(255, 255, 255, 0.5)
Border:         2px solid transparent
Cursor:         not-allowed
```

### Button States (CTA)

**Default**
```
Background:     #730f33 (burgundy)
Text Color:     #ffffff (white)
Border:         None or 2px solid #bc935b
Cursor:         pointer
```

**Hover**
```
Background:     #5a0a27 (darker burgundy)
Text Color:     #bc935b (gold text)
Border:         2px solid #bc935b (gold)
Transform:      scale(1.02) or brightness(1.1)
Shadow:         0 2px 8px rgba(0,0,0,0.3)
```

**Active (Pressed)**
```
Background:     #5a0a27 (darker)
Text Color:     #ffffff (white)
Transform:      scale(0.98)
Shadow:         Inset shadow
```

**Focus**
```
Outline:        2px solid white
Outline-offset: 2px
```

### Mobile Hamburger States

**Default**
```
Icon:           ☰ (bars)
Color:          #ffffff
Size:           1.25rem
Cursor:         pointer
```

**Hover**
```
Color:          #bc935b (gold)
Transform:      scale(1.1)
Transition:     150ms ease-in
```

**Active (Menu Open)**
```
Icon:           ✕ (X) - optional
Color:          #bc935b (gold)
Transform:      rotate(90deg) - optional
```

---

## 🌈 Visual Hierarchy

### Element Importance Order

1. **Logo** (Highest)
   - Largest text (1.5rem)
   - Bold weight (700)
   - Always visible
   - Left-aligned prominence

2. **Current Page Link** (Active)
   - Gold bottom border
   - Slightly brighter
   - Clear visual distinction

3. **Menu Items** (Standard)
   - White text
   - Medium weight
   - Hover effect available

4. **CTA Buttons** (Secondary Importance)
   - Right-aligned
   - Outlined or filled
   - Strong color contrast

5. **Disabled Items** (Low Priority)
   - 50% opacity
   - Cursor: not-allowed
   - Visually deprioritized

---

## 📱 Responsive Adaptations

### Desktop Optimization (1024px+)
```
Layout:         Horizontal, full-width menu visible
Logo Position:  Left, prominent
Menu Position:  Center, all items visible
Buttons:        Right, side-by-side
Spacing:        Generous, comfortable
Hover States:   Fully enabled
```

### Tablet Optimization (768px - 1024px)
```
Layout:         Horizontal, still full menu
Logo Position:  Left, slightly smaller
Menu Position:  Center, tighter spacing
Buttons:        Right, stacked or compact
Spacing:        Reduced, efficient
Hover States:   Fully enabled
```

### Mobile Optimization (<768px)
```
Layout:         Hamburger menu, dropdown on demand
Logo Position:  Left, compact
Menu Position:  Hidden, revealed via dropdown
Buttons:        Below menu, full-width
Spacing:        Minimal, optimized for touch
Hover States:   Limited (no hover on mobile)
Touch Targets:  ≥44x44px
```

---

## ✨ Special Effects

### Gradient Background
```
Type:           Linear gradient
Direction:      90deg (left to right)
Colors:         #730f33 (0%) → #5a0a27 (100%)
Smoothness:     Smooth color transition
Position:       Entire navbar
Animation:      Static (no animation)
```

### Shadow Effects

**Navbar Default**
```
Shadow:         None (flat design)
Effect:         Clean, modern look
```

**Navbar on Scroll (.navbar.scrolled)**
```
Shadow:         0 4px 12px rgba(0, 0, 0, 0.15)
Effect:         Adds depth, indicates sticky position
Transition:     100ms ease-out
```

**Button Hover**
```
Shadow:         0 2px 8px rgba(0, 0, 0, 0.3)
Effect:         Subtle lift effect
Transition:     150ms ease-in
```

### Opacity/Transparency Effects

**Text Primary**
```
Opacity:        1.0 (100%)
Usage:          Link text, headings
```

**Text Hover**
```
Opacity:        0.7 (70%)
Usage:          Hover state text
Effect:         Slightly faded
```

**Background Hover**
```
Color:          rgba(255, 255, 255, 0.1)
Effect:         Subtle highlight
Usage:          Link hover state
```

---

## 🎪 Animation Easing Reference

### Easing Functions Used

**ease-in**
```
Curve:          Starts slow, accelerates
Best for:       Entering animations, sudden focus
Example:        Hover effects, menu appearance
```

**ease-out**
```
Curve:          Starts fast, decelerates
Best for:       Exiting animations, smooth landing
Example:        Border fades, menu disappears
```

**ease-in-out**
```
Curve:          Slow start, fast middle, slow end
Best for:       Standard transitions, smooth changes
Example:        Link state changes, scroll effects
```

---

## 🔍 Accessibility Features

### Visual Indicators
```
✓ Color contrast: 4.5:1 (white on burgundy)
✓ Active state: Clear visual indicator (gold border)
✓ Hover state: Clear visual indicator (background)
✓ Focus indicator: Visible outline for keyboard nav
✓ Icon + text: Labels with icons for clarity
✓ Font size: ≥16px on mobile (no zoom needed)
✓ Touch targets: ≥44x44px on mobile
```

### Color Blindness Considerations
```
✓ Not relying on color alone for state
✓ Using border style (thick line) for active
✓ Using background for hover (not just color change)
✓ Text labels alongside icons
✓ High contrast maintained
```

---

## 📐 Sizing Reference

### Icon Sizes
```
Navbar icons:       1rem (16px)
Logo icon:          1.25rem (20px) relative to text
Button icons:       0.9rem (14px)
Hamburger:          1.25rem (20px)
```

### Button Sizes
```
Height:             44px (mobile), 40px (desktop)
Width:              Auto (fit content)
Min Width:          60px
Padding:            0.75rem 1rem (desktop)
Padding:            0.6rem 0.8rem (mobile)
Border Radius:      6px
```

### Component Widths
```
Navbar:             100vw (full viewport width)
Nav-container:      max-width: 1400px
Logo Width:         Auto (fit content)
Menu Width:         100% - 100px (for buttons)
Mobile Menu:        100vw (full screen width)
```

---

## 🎯 Visual Testing Patterns

### Pattern 1: Hover State
```css
/* How it looks */
Link:           "Features" (white text)
On Hover:       Light background + gold border
Effect:         Smooth 150ms transition
Appearance:     Lifted, interactive
```

### Pattern 2: Active State
```css
/* How it looks */
Current Link:   "Empresas" with gold bottom border
Background:     Light white overlay
Effect:         Stands out from other links
Appearance:     Clearly selected
```

### Pattern 3: Mobile Menu
```css
/* How it looks */
Default:        Hamburger button visible, menu hidden
On Click:       Menu slides/fades in from top
Items:          Stack vertically, full width
Buttons:        Below menu, full width
Effect:         Quick access to all pages
```

---

## 💡 Design Principles

1. **Consistency**
   - Same colors throughout
   - Same spacing units
   - Same typography
   - Same transitions

2. **Clarity**
   - Clear navigation hierarchy
   - Obvious active/hover states
   - Readable text (high contrast)
   - Clear button purposes

3. **Efficiency**
   - Quick access to all pages
   - Minimal clicks to navigate
   - Mobile-optimized spacing
   - Fast animations (not distracting)

4. **Accessibility**
   - Keyboard navigable
   - Screen reader friendly
   - Color contrast compliant
   - Touch-friendly on mobile

5. **Responsiveness**
   - Adapts to all screen sizes
   - No horizontal scroll
   - Touch targets adequate
   - Layout reflows smoothly

---

## 🎨 CSS Variables (If Using)

```css
:root {
    /* Colors */
    --color-primary: #730f33;
    --color-primary-dark: #5a0a27;
    --color-accent: #bc935b;
    --color-text: #ffffff;
    --color-text-secondary: rgba(255, 255, 255, 0.7);
    
    /* Typography */
    --font-family-base: 'Inter', sans-serif;
    --font-size-base: 1rem;
    --font-size-sm: 0.9rem;
    --font-weight-regular: 400;
    --font-weight-medium: 500;
    --font-weight-bold: 700;
    
    /* Spacing */
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 2rem;
    
    /* Transitions */
    --transition-fast: 150ms ease-in;
    --transition-base: 300ms ease-in-out;
    --transition-slow: 500ms ease-out;
    
    /* Z-index */
    --z-navbar: 1000;
    --z-dropdown: 999;
    --z-modal: 1001;
}
```

---

## 🖼️ Visual Mockups

### Desktop Layout
```
┌────────────────────────────────────────────────────────┐
│  🧠 MoirAI  │  ⭐ Caract | ⚙️ Cómo | 👥 Para Quién  │ Buttons │
│             │  💼 Oport | 🏢 Emps │ 👨‍🎓 Estudian │
└────────────────────────────────────────────────────────┘

Spacing: Comfortable, professional
Colors: Burgundy gradient with white text
Hover: Light background + gold border
Active: Gold border on current page
```

### Mobile Layout
```
When Collapsed:
┌─────────────────────┐
│ 🧠 MoirAI     ☰    │
└─────────────────────┘

When Expanded:
┌─────────────────────┐
│ 🧠 MoirAI     ☰    │
├─────────────────────┤
│ ⭐ Características  │
│ ⚙️ Cómo Funciona    │
│ 👥 Para Quién       │
│ 💼 Oportunidades    │
│ 🏢 Empresas         │
│ 👨‍🎓 Estudiantes      │
│ ✉️ Contacto         │
│                     │
│ [Inicia Sesión]     │
│ [Únete Ahora]       │
└─────────────────────┘

Spacing: Compact, mobile-optimized
Touch: ≥44x44px targets
```

---

**Last Updated**: November 12, 2025  
**Version**: 1.0  
**Design Status**: ✅ Production Ready
