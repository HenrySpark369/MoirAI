# 🎨 Collapsible Sidebar - Visual States & Flows

## Screen States by Device

### 🖥️ DESKTOP (1024px+)

#### State 1: Expanded (Default)
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────────────────────┐   │
│  │ 🧠 MoirAI        │  │                                  │   │
│  │                  │  │        MAIN CONTENT              │   │
│  │ ──────────────   │  │                                  │   │
│  │ ⭐ Caracterís.   │  │  • Full width available          │   │
│  │ ⚙️ Cómo Funciona │  │  • Page title & hero section     │   │
│  │ 👥 Para Quién    │  │  • Article/listing content      │   │
│  │ 💼 Oportunidad   │  │  • Comfortable reading width     │   │
│  │ 🏢 Empresas      │  │                                  │   │
│  │ 👨‍🎓 Estudiantes   │  │                                  │   │
│  │ ✉️ Contacto      │  │                                  │   │
│  │                  │  │                                  │   │
│  │ ──────────────   │  │                                  │   │
│  │ [Login] [Signup] │  │                                  │   │
│  │                  │  │                                  │   │
│  │ ──────────────   │  │                                  │   │
│  │ ◀ Ocultar       │ ← Click to collapse                │   │
│  │                  │  │                                  │   │
│  └──────────────────┘  └──────────────────────────────────┘   │
│  ↑                     ↑                                        │
│  280px width           Main content area                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### State 2: Collapsed (After Click)
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌──────┐  ┌──────────────────────────────────────────┐        │
│  │ 🧠   │  │                                          │        │
│  │      │  │        MAIN CONTENT (Expanded)           │        │
│  │ ──── │  │                                          │        │
│  │ ⭐→ │  │  • More horizontal space!                │        │
│  │      │  │  • Page content wider                   │        │
│  │ ⚙️→ │  │  • Better for reading                    │        │
│  │      │  │                                          │        │
│  │ 👥→ │  │  Hover over icon → Tooltip appears      │        │
│  │      │  │                                          │        │
│  │ 💼→ │  │  Example: Hover ⭐ →                    │        │
│  │      │  │  ┌──────────────────┐                   │        │
│  │ 🏢→ │  │  │ Características  │ ← Dark tooltip   │        │
│  │      │  │  └──────────────────┘                   │        │
│  │ 👨‍🎓→ │  │                                          │        │
│  │      │  │                                          │        │
│  │ ✉️→ │  │                                          │        │
│  │      │  │                                          │        │
│  │ ──── │  │                                          │        │
│  │ (CTA │  │                                          │        │
│  │hidden)  │                                          │        │
│  │      │  │                                          │        │
│  │ ──── │  │                                          │        │
│  │ ▶    │ ← Click to expand                         │        │
│  │      │  │                                          │        │
│  └──────┘  └──────────────────────────────────────────┘        │
│  ↑         ↑                                                    │
│  80px      Content expanded                                    │
│  width                                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 📱 TABLET (768px - 1024px)

#### State 1: Expanded
```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  ┌────────────────┐  ┌──────────────────────┐     │
│  │ 🧠 MoirAI      │  │   MAIN CONTENT       │     │
│  │ ──────────────  │  │                      │     │
│  │ ⭐ Caracterís. │  │   Full width on      │     │
│  │ ⚙️ Cómo Func. │  │   tablet (smaller    │     │
│  │ 👥 Para Quién  │  │   than desktop)      │     │
│  │ 💼 Oportuni... │  │                      │     │
│  │ 🏢 Empresas    │  │   Sidebar takes      │     │
│  │ 👨‍🎓 Estudian... │  │   250px              │     │
│  │ ✉️ Contacto    │  │                      │     │
│  │ ─────────────   │  │                      │     │
│  │ [Login][Sign]  │  │                      │     │
│  │ ─────────────   │  │                      │     │
│  │ ◀ Ocultar     │  │                      │     │
│  └────────────────┘  └──────────────────────┘     │
│  ↑                   ↑                             │
│  250px width         Available space              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

#### State 2: Collapsed
```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  ┌────┐  ┌────────────────────────────────┐        │
│  │🧠  │  │   MAIN CONTENT (Wider now!)    │        │
│  │────│  │                                │        │
│  │ ⭐→ │  │   Much more space for content │        │
│  │    │  │   on tablet screen            │        │
│  │ ⚙️→ │  │                               │        │
│  │    │  │   Hover for tooltips ↓        │        │
│  │ 👥→ │  │   Same experience as desktop │        │
│  │    │  │                               │        │
│  │ 💼→ │  │                               │        │
│  │    │  │                               │        │
│  │ 🏢→ │  │                               │        │
│  │    │  │                               │        │
│  │ 👨‍🎓→ │  │                               │        │
│  │    │  │                               │        │
│  │ ✉️→ │  │                               │        │
│  │    │  │                               │        │
│  │────│  │                               │        │
│  │ ▶   │  │                               │        │
│  └────┘  └────────────────────────────────┘        │
│  ↑        ↑                                         │
│  70px     Content expanded                         │
│  width                                              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

### 📲 MOBILE (<768px)

#### State 1: Closed (Default)
```
┌──────────────────────────────────┐
│ ☰ MoirAI                         │  ← Hamburger button
├──────────────────────────────────┤
│                                  │
│      MAIN CONTENT               │
│      (Full Width!)              │
│                                  │
│  • No sidebar taking space       │
│  • Content uses all available    │
│    horizontal space              │
│  • Better for mobile reading     │
│                                  │
│                                  │
│                                  │
└──────────────────────────────────┘
```

#### State 2: Open (After Click ☰)
```
┌──────────────┬──────────────────┐
│ 🧠 Nav       │ Content (faded)   │
├──────────────┤                   │
│ ⭐ Inicio    │                   │
│              │ Click link or     │
│ 💼 Oportun.  │ click outside     │
│              │ → sidebar closes  │
│ 🏢 Empresas  │                   │
│              │                   │
│ 👨‍🎓 Estud.   │                   │
│              │                   │
│ 📊 Admin     │                   │
│              │                   │
│ ──────────   │                   │
│ [Login]      │                   │
│              │                   │
└──────────────┴──────────────────┘
   70vw width      Overlaid/faded
   Slides from
   left
```

---

## User Interaction Flows

### Desktop: Collapse/Expand Flow
```
                      User on Desktop (1024px+)
                              │
                              ↓
                   Page loads with state
                              │
                 ┌────────────┴────────────┐
                 ↓                         ↓
        localStorage has   localStorage empty
        'true'             or 'false'
                 │                         │
                 ↓                         ↓
    Sidebar starts    Sidebar starts
    COLLAPSED         EXPANDED
         │                 │
         ↓                 ↓
   Icon-only mode    Full labels visible
   (80px)            (280px)
         │                 │
         ├─────────────────┤
         │                 │
    User clicks       User clicks
    collapse button   expand button
         │                 │
         ↓                 ↓
    Toggle state → Save to localStorage → Show updated UI
         │
    Icon position changes: ◀ ↔ ▶
    Text changes: "Ocultar" ↔ "Expandir"
         │
         ↓
    Smooth 300ms animation
    Width transitions: 280px ↔ 80px
         │
         ↓
    Content reflows gracefully
    Margin-left transitions: 280px ↔ 80px
```

### Desktop: Tooltip Flow (Collapsed)
```
Sidebar in COLLAPSED mode
       │
       ↓
User hovers over icon (e.g., ⭐)
       │
       ↓
Icon has data-tooltip="Características"
       │
       ↓
CSS ::after pseudo-element triggered
       │
       ↓
Tooltip appears with text:
┌──────────────────┐
│ Características  │
└──────────────────┘
       │
       ↓
User moves mouse away
       │
       ↓
Tooltip fades out (opacity: 1 → 0)
```

### Mobile: Hamburger Toggle Flow
```
Mobile user (<768px)
       │
       ↓
Page loads → JavaScript creates hamburger button
       │
       ↓
Hamburger button (☰) visible in top-left
       │
       ↓
User clicks ☰
       │
       ↓
Sidebar slides in from left (transform: translateX(0))
       │
       ├─────────────────────────────────┐
       │                                 │
    User clicks          User clicks
    navigation link      outside sidebar
       │                 │
       ↓                 ↓
    Navigate to      Sidebar closes
    new page         (transform: translateX(-100%))
       │
       ↓
    Sidebar auto-closes
    (Same effect as clicking outside)
```

---

## Viewport Size Transitions

### Expanding from Mobile to Tablet
```
<768px (Mobile)           768-1024px (Tablet)      1024px+ (Desktop)
─────────────────         ──────────────────      ─────────────────
☰ (Hamburger)     →       Collapse button   →     Collapse button
70vw full-width   →       250px sidebar     →     280px sidebar
No collapse       →       Collapse works    →     Collapse works
Toggle only       →       Tooltips on hover →     Tooltips on hover
                  
User preference
from 768px onwards:
All changes remembered!
```

### Shrinking from Desktop to Mobile
```
1024px+ (Desktop)         768-1024px (Tablet)      <768px (Mobile)
─────────────────         ──────────────────      ─────────────────
If collapsed:             If collapsed:           Collapses
  → Auto-expands            → Auto-expands         automatically
  → Collapses hidden        → Updates size       Hamburger appears
  → Hamburger appears       to 70px              instead
                          Hamburger appears
```

---

## Active State Indicators

### Expanded Mode (Desktop/Tablet)
```
Normal Link          Active Link
───────────────      ─────────────────
⭐ Caracterís.       ║ ⭐ Oportunidades
(No indicator)       ║ (Gold left border)
                     (Highlighted bg)
                     (Bright white text)
```

### Collapsed Mode (Desktop/Tablet)
```
Normal Icon          Active Icon
───────────        ─────────────
⭐                 ⭐
(No indicator)     ═ (Gold bottom border)
                   (Highlighted bg)
                   (Bright white)
```

---

## Animation Timeline

### Collapse Animation (300ms)
```
Time    Navbar Width    Body Margin    Text Opacity    Icons
────    ────────────    ───────────    ────────────    ─────
0ms     280px           280px          100%            Visible
50ms    240px           240px          80%             Visible
100ms   200px           200px          60%             Visible
150ms   140px           140px          40%             Visible
200ms   110px           110px          20%             Visible
250ms   90px            90px           5%              Visible
300ms   80px            80px           0%              Hidden

Result: Smooth collapse with text fading
```

### Tooltip Fade-in (300ms)
```
Time    Opacity    Effect
────    ────────   ──────
0ms     0          Hidden
75ms    0.25       Starting to show
150ms   0.5        Semi-visible
225ms   0.75       Almost visible
300ms   1          Fully visible

Result: Smooth fade-in when hovering icon
```

---

## Color Scheme in Different States

### Expanded Mode
```
Background:    Gradient #730f33 → #5a0a27
Text:          White (opacity 0.8)
Text Hover:    White (opacity 1.0)
Active Border: Left gold border (#bc935b)
Active BG:     Light white (opacity 0.15)
```

### Collapsed Mode
```
Background:    Same gradient (unchanged)
Text:          White (opacity 0.8)
Text Hover:    White (opacity 1.0)
Active Border: Bottom gold border (#bc935b) ← Changed!
Active BG:     Light white (opacity 0.15)
Tooltip BG:    Dark overlay (rgba 0,0,0,0.9)
Tooltip Text:  White
```

---

## Summary: States Overview

| State | Width | Labels | CTA Btn | Tooltips | Active | Device |
|-------|-------|--------|---------|----------|--------|--------|
| Expanded | 280px | ✅ | ✅ | ❌ | Left gold | DT |
| Collapsed | 80px | ❌ | ❌ | ✅ | Bottom gold | DT |
| Expanded | 250px | ✅ | ✅ | ❌ | Left gold | TB |
| Collapsed | 70px | ❌ | ❌ | ✅ | Bottom gold | TB |
| Toggle Open | 70vw | ✅ | ✅ | ❌ | Left gold | MB |
| Toggle Close | N/A | ❌ | ❌ | ❌ | N/A | MB |

**DT** = Desktop | **TB** = Tablet | **MB** = Mobile

---

**Last Updated**: November 12, 2025
