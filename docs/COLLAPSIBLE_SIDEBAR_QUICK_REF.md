# 🎯 Collapsible Sidebar - Quick Reference

## At a Glance

| Feature | Desktop | Tablet | Mobile |
|---------|---------|--------|--------|
| **Sidebar Width** | 280px | 250px | 70vw |
| **Collapsed Width** | 80px | 70px | N/A |
| **Collapse Button** | ✅ | ✅ | ❌ |
| **Toggle Button** | N/A | N/A | ✅ |
| **Tooltips** | ✅ | ✅ | ❌ |
| **State Saved** | ✅ | ✅ | ❌ |

---

## User Controls

### Desktop / Tablet
```
EXPANDED STATE
┌────────────────────┐
│ 🧠 MoirAI          │
├────────────────────┤
│ ⭐ Características │
│ [... more items ...]
├────────────────────┤
│ [Login] [Signup]   │
├────────────────────┤
│ ◀ Ocultar          │ ← Click to collapse
└────────────────────┘

COLLAPSED STATE
┌──────┐
│ 🧠   │
├──────┤
│ ⭐→ │ Hover for tooltip
│ ⚙️→ │ Tooltip: "Cómo Funciona"
│ ...  │
├──────┤
│ ▶    │ ← Click to expand
└──────┘
```

### Mobile
```
┌─────────────────┐          ┌──────────────┐
│ ☰               │  Click   │ 🧠 Nav       │
│  Content        │  ────→   │ ⭐ Menu      │
│  (Full Width)   │          │ ... items    │
│                 │          │ [Login]      │
└─────────────────┘          └──────────────┘
                  Click link or outside → closes
```

---

## CSS Classes

### Applied to `.navbar`
```css
/* Normal state (default) */
.navbar {
    width: 280px;
}

/* Collapsed state */
.navbar.collapsed {
    width: 80px;
}
```

### Applied to `body`
```css
/* Normal state (default) */
body {
    margin-left: 280px;
}

/* Collapsed state */
body.collapsed {
    margin-left: 80px;
}
```

### Applied to `.nav-link` (when navbar collapsed)
```css
.navbar.collapsed .nav-link {
    border-left: none;
    border-bottom: 3px solid transparent;
    justify-content: center;
}

.navbar.collapsed .nav-link.active {
    border-bottom-color: #bc935b;
}

/* Tooltip appears on hover */
.navbar.collapsed .nav-link:hover::after {
    opacity: 1;
}
```

---

## HTML Structure

### Collapse Button
```html
<!-- Add at bottom of .nav-container, before closing </nav> -->
<button class="collapse-toggle" id="collapseToggle">
    <i class="fas fa-chevron-left"></i>
    <span>Ocultar</span>
</button>
```

### Nav Links with Tooltips
```html
<!-- Add data-tooltip to each link -->
<a href="/path" class="nav-link" data-tooltip="Label">
    <i class="fas fa-icon"></i>
    <span>Label</span>
</a>
```

---

## JavaScript Functions

### `initSidebar()`
- Creates mobile hamburger button
- Handles mobile open/close
- Manages resize events
- Sets active links

**Auto-runs on page load** ✅

### `initCollapsible()`
- Loads collapsed state from localStorage
- Adds collapse button click handler
- Manages responsive behavior
- Hides collapse button on mobile

**Auto-runs on page load** ✅

### `updateCollapseButton()`
- Changes icon: ◀ ↔ ▶
- Changes text: "Ocultar" ↔ "Expandir"
- Called when collapse state changes

**Auto-called on toggle** ✅

### `setActiveLink()`
- Highlights current page link
- Compares URL to links
- Adds `.active` class

**Auto-runs on page load** ✅

---

## localStorage Keys

### Key: `sidebarCollapsed`
```javascript
// Save (when collapsing)
localStorage.setItem('sidebarCollapsed', 'true');

// Load (on page load)
localStorage.getItem('sidebarCollapsed') === 'true'
```

**Scope**: Per browser/device  
**Persistence**: Permanent (until user clears)  
**Breakpoint**: Only applies on 1024px+

---

## Breakpoints

```css
/* Desktop 1024px+ */
@media (min-width: 1025px) {
    .collapse-toggle { display: flex; }
    .sidebar-toggle { display: none; }
}

/* Tablet 768px - 1024px */
@media (max-width: 1024px) {
    .navbar { width: 250px; }
    .navbar.collapsed { width: 70px; }
    .collapse-toggle { display: flex; }
}

/* Mobile <768px */
@media (max-width: 768px) {
    .navbar { transform: translateX(-100%); }
    .navbar.show { transform: translateX(0); }
    .collapse-toggle { display: none; }
    .sidebar-toggle { display: block; }
}
```

---

## Color Values

```css
:root {
    --primary-color: #730f33;      /* Sidebar bg start */
    --primary-dark: #5a0a27;       /* Sidebar bg end */
    --secondary-dark: #bc935b;     /* Active border/accent */
}

/* In collapsed mode */
.navbar.collapsed .nav-link:hover {
    border-bottom-color: #bc935b;  /* Gold border */
}

/* Tooltip style */
.navbar.collapsed .nav-link::after {
    background: rgba(0, 0, 0, 0.9);
    color: white;
}
```

---

## Animations

### Collapse/Expand (300ms)
```css
.navbar {
    transition: width 0.3s ease;
}

body {
    transition: margin-left 0.3s ease;
}
```

### Tooltip Fade-in (300ms)
```css
.navbar.collapsed .nav-link::after {
    transition: opacity 0.3s ease;
    opacity: 0;
}

.navbar.collapsed .nav-link:hover::after {
    opacity: 1;
}
```

### Icon Flip (300ms)
```css
.collapse-toggle i {
    transition: transform 0.3s ease;
}

.navbar.collapsed .collapse-toggle i {
    transform: scaleX(-1);  /* Flip left/right */
}
```

---

## States & Indicators

### Active Link (In Sidebar)
- 🔹 Border-left: 3px gold (#bc935b)
- 🔹 Background: Light white (0.15 opacity)
- 🔹 Text: Bright white

### Active Link (Collapsed)
- 🔹 Border-bottom: 3px gold (#bc935b)
- 🔹 Background: Light white (0.15 opacity)
- 🔹 Text: Bright white

### Hover State
- 🔹 Background: Light white (0.1 opacity)
- 🔹 Text: Bright white

### Hover with Tooltip (Collapsed)
- 🔹 Tooltip appears left of icon
- 🔹 Dark background (high contrast)
- 🔹 Fades in smoothly

---

## Customization

### Change Collapsed Width
```css
.navbar.collapsed { width: 90px; }      /* Was 80px */
body.collapsed { margin-left: 90px; }   /* Update body too */
```

### Change Tooltip Position
```css
.navbar.collapsed .nav-link::after {
    left: 100px;  /* Distance from left edge */
}
```

### Change Button Text
```html
<button class="collapse-toggle">
    <i class="fas fa-angles-left"></i>  <!-- Different icon -->
    <span>Hide</span>                     <!-- English text -->
</button>
```

### Change Animation Speed
```css
.navbar {
    transition: width 0.5s ease;  /* Was 0.3s */
}
```

### Disable State Persistence
Comment out in `sidebar.js`:
```javascript
// localStorage.setItem('sidebarCollapsed', ...);
// const isCollapsed = localStorage.getItem(...);
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Button not showing | Check screen width > 1024px |
| Sidebar won't collapse | Verify `.collapsed` in CSS exists |
| Tooltip not appearing | Hover over icon (not text), check data-tooltip attr |
| State not saving | Check if localStorage is enabled |
| Collapse button on mobile | Should NOT appear - check media query |
| Animation too fast/slow | Adjust `transition: ... 0.3s` to desired value |
| Tooltip position wrong | Edit `left: 90px` in `.nav-link::after` |

---

## Browser Support

| Browser | Support |
|---------|---------|
| Chrome 90+ | ✅ Full |
| Firefox 88+ | ✅ Full |
| Safari 14+ | ✅ Full |
| Edge 90+ | ✅ Full |
| IE 11 | ⚠️ Limited |

---

## Performance Tips

✅ **Do:**
- Use collapse for power users
- Keep tooltips short (1-2 words)
- Test on different devices
- Monitor localStorage usage

❌ **Don't:**
- Add too many nested menus
- Make tooltips too long
- Disable animations completely
- Change breakpoints casually

---

## Files to Know

```
app/frontend/
├── static/
│   ├── css/
│   │   └── styles.css          ← Collapse styles here
│   └── js/
│       └── sidebar.js           ← Collapse functions here
└── templates/
    ├── index.html              ← Add data-tooltip attrs
    ├── oportunidades.html      ← Add data-tooltip attrs
    ├── empresas.html           ← Add data-tooltip attrs
    └── estudiantes.html        ← Add data-tooltip attrs

docs/
├── COLLAPSIBLE_SIDEBAR_GUIDE.md      ← Full documentation
└── SIDEBAR_VISUAL_REFERENCE.md       ← Visual diagrams
```

---

## Testing Scenarios

### Scenario 1: User Collapses on Desktop
1. Open site on desktop (1024px+)
2. Click "◀ Ocultar" button
3. Sidebar shrinks to 80px
4. Icons visible, text hidden
5. Content expands to fill space
6. Refresh page → stays collapsed ✅

### Scenario 2: User Hovers Collapsed Icon
1. Sidebar is collapsed (icon-only)
2. Hover over any icon
3. Tooltip appears with label
4. Move mouse away → fades out
5. Click icon → navigates to page ✅

### Scenario 3: Mobile User Opens Menu
1. Open site on mobile (<768px)
2. Click hamburger (☰) button
3. Sidebar slides in from left
4. Click a link
5. Sidebar auto-closes
6. Navigate to new page ✅

### Scenario 4: Resize from Desktop to Mobile
1. Start on desktop with sidebar collapsed
2. Resize browser to <768px
3. Sidebar shows toggle instead
4. Collapse button disappears
5. Hamburger button appears
6. Click hamburger → sidebar toggles ✅

---

## Version Info

- **Version**: 1.0
- **Release Date**: November 12, 2025
- **Status**: 🚀 Production Ready
- **Browser Support**: All modern browsers
- **Mobile Support**: ✅ Optimized

---

**Last Updated**: November 12, 2025
