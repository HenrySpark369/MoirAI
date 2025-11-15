# Sidebar Navigation Implementation Guide

## 🎉 What's New

The navigation menu has been transformed from a **horizontal top navbar** into a **professional fixed sidebar** design, providing better organization and navigation across all pages (landing page, oportunidades, empresas, estudiantes, and admin dashboard).

---

## 📐 Design Features

### Sidebar Structure
- **Fixed Position**: Stays visible while scrolling
- **Width**: 280px on desktop, 250px on tablet, 70vw on mobile
- **Height**: Full viewport height with auto-scrolling for long menus
- **Gradient Background**: Professional gradient using brand colors (Burgundy → Dark Burgundy)
- **Color**: White text with hover effects

### Navigation Items
- **Icons**: Each menu item has a Font Awesome icon
- **Active State**: Highlight with background color and left border
- **Hover Effect**: Smooth background color transition
- **Responsive**: Stacks vertically and adjusts on all screen sizes

### Button Styling
- **CTA Buttons**: Styled consistently with brand colors
- **Icons + Text**: Each button has an icon for better visual hierarchy

---

## 🎨 Visual Layout

### Desktop View (1024px+)
```
┌─────────────────┬────────────────────────────────┐
│                 │                                 │
│   SIDEBAR       │      MAIN CONTENT             │
│   (280px)       │      (Remaining width)         │
│                 │                                 │
│  🧠 MoirAI      │                                 │
│  ──────────     │                                 │
│  ★ Features     │    Landing page or              │
│  ⚙️ Cómo         │    Sub-site content             │
│  👥 Para Quién  │                                 │
│  💼 Oportunidad │                                 │
│  🏢 Empresas    │                                 │
│  👨‍🎓 Estudiantes │                                 │
│  ✉️ Contacto    │                                 │
│  ──────────     │                                 │
│  🔐 Inicia Sesión│                                 │
│  ──────────     │                                 │
│                 │                                 │
└─────────────────┴────────────────────────────────┘
```

### Tablet View (768px - 1023px)
```
┌──────────────────────────────────────┐
│ SIDEBAR (Horizontal)                 │
│ 250px width                          │
├──────────────────────────────────────┤
│                                      │
│      MAIN CONTENT                    │
│      (Full width adjusted)           │
│                                      │
└──────────────────────────────────────┘
```

### Mobile View (<768px)
```
┌──────────────────┐
│ ☰ (toggle btn)   │
├──────────────────┤
│                  │
│  MAIN CONTENT    │
│  (Full width)    │
│                  │
└──────────────────┘

Sidebar appears as overlay
when toggle is clicked
```

---

## 🎯 Features

### ✅ Fully Responsive
- **Desktop**: Fixed sidebar on the left, content flows right
- **Tablet**: Sidebar width adjusted (250px), content adjusted
- **Mobile**: Sidebar hidden by default, toggle button shows/hides it
- **Auto-hide on mobile**: Closes when a link is clicked

### ✅ Smart Navigation
- **Active State Detection**: Highlights current page link
- **Smooth Transitions**: All interactions smooth and fluid
- **Click Outside**: Closes sidebar on mobile when clicking outside
- **Resize Handler**: Adapts layout when window resizes

### ✅ Accessibility
- **Semantic HTML**: Proper nav elements
- **Icons with Labels**: Text visible next to icons
- **Keyboard Navigation**: All links accessible via keyboard
- **Color Contrast**: High contrast for readability

### ✅ Performance
- **No Dependencies**: Vanilla JavaScript only
- **Lightweight**: Minimal CSS and JS
- **Smooth Animations**: Hardware-accelerated transforms
- **Fast Load**: No external libraries required

---

## 📁 Files Changed

### CSS Updated
- **`styles.css`** - Replaced navbar styles with sidebar styles
  - `navbar` - Fixed sidebar positioning
  - `nav-container` - Flexbox column layout
  - `nav-logo` - Brand header styling
  - `nav-menu` - Vertical menu layout
  - `nav-link` - Hover and active states
  - Responsive media queries for all breakpoints

### JavaScript Added
- **`sidebar.js`** - New file for sidebar functionality
  - `initSidebar()` - Initialize sidebar on page load
  - `setActiveLink()` - Highlight current page
  - Mobile toggle button creation and handling
  - Click outside detection
  - Resize event handling

### HTML Updated
- **`index.html`** - Updated navbar to sidebar structure with icons
- **`oportunidades.html`** - Updated navbar to sidebar structure
- **`empresas.html`** - Updated navbar to sidebar structure
- **`estudiantes.html`** - Updated navbar to sidebar structure
- All pages now include `sidebar.js` script

---

## 🎨 Color Scheme

The sidebar uses the brand color scheme:

```
Background (Gradient):
  Start: #730f33 (Deep Burgundy)
  End:   #5a0a27 (Dark Burgundy)

Text: white (rgba(255,255,255,0.8))
Hover: white (rgba(255,255,255,1)) with background tint
Active Border: #bc935b (Warm Gold)
Active Background: rgba(255,255,255,0.15)
```

---

## 📍 Navigation Structure

### Landing Page (`/`)
1. 🧠 **Logo** (MoirAI)
2. ⭐ **Características**
3. ⚙️ **Cómo Funciona**
4. 👥 **Para Quién**
5. 💼 **Oportunidades**
6. 🏢 **Empresas**
7. 👨‍🎓 **Estudiantes**
8. ✉️ **Contacto**
9. Buttons: Inicia Sesión | Únete Ahora

### Sub-Sites (Oportunidades, Empresas, Estudiantes)
1. 🧠 **Logo** (MoirAI)
2. 🏠 **Inicio**
3. 💼 **Oportunidades** (active on /oportunidades)
4. 🏢 **Empresas** (active on /empresas)
5. 👨‍🎓 **Estudiantes** (active on /estudiantes)
6. 📊 **Admin**
7. Button: Inicia Sesión

---

## 🚀 How to Use

### Desktop Experience
1. Sidebar is always visible on the left
2. Click any link to navigate
3. Current page is highlighted
4. Button clicks work as expected

### Mobile Experience
1. Click the hamburger icon (☰) to open sidebar
2. Click any link to navigate (sidebar auto-closes)
3. Click outside sidebar to close it
4. Sidebar closes automatically on resize

### Admin Dashboard
1. The admin dashboard already has its own sidebar
2. Now integrates seamlessly with the main sidebar style
3. Both use same color scheme and icons

---

## 🔧 Technical Details

### CSS Variables Used
```css
--primary-color: #730f33         /* Sidebar background */
--primary-dark: #5a0a27          /* Gradient end */
--secondary-dark: #bc935b        /* Active border */
--shadow-lg: 0 20px 25px...      /* Shadow effects */
```

### JavaScript Functions
```javascript
initSidebar()           // Initialize on page load
setActiveLink()         // Highlight current page
smoothScroll(target)    // Smooth scroll to elements
```

### Responsive Breakpoints
- **Desktop**: 1024px+ (sidebar always visible)
- **Tablet**: 768px - 1023px (sidebar 250px)
- **Mobile**: < 768px (sidebar hidden, toggle to show)

---

## 📊 Media Queries

```css
/* Desktop (1024px+) */
.navbar { width: 280px; }
body { margin-left: 280px; }

/* Tablet (768px - 1023px) */
.navbar { width: 250px; }
body { margin-left: 250px; }

/* Mobile (< 768px) */
.navbar { width: 70vw; transform: translateX(-100%); }
.navbar.show { transform: translateX(0); }
body { margin-left: 0; }
.sidebar-toggle { display: block; }
```

---

## ✨ Interactions

### Hover Effects
- Links: Background color changes, border appears
- Buttons: Slight scale transform, shadow appears
- Smooth transitions (0.3s ease)

### Click Interactions
- Links: Active state highlights current page
- Toggle: Shows/hides sidebar on mobile
- Outside click: Closes sidebar on mobile

### Active States
- Left border: 3px solid gold (#bc935b)
- Background: Light white overlay (rgba(255,255,255,0.15))
- Text: Bright white

---

## 🔄 Compatibility

✅ **Chrome/Edge** (Latest)
✅ **Firefox** (Latest)
✅ **Safari** (Latest)
✅ **Mobile Safari** (iOS)
✅ **Mobile Chrome** (Android)

---

## 📱 Responsive Behavior

| Screen Size | Sidebar Width | Visibility | Toggle |
|-------------|---------------|-----------|--------|
| Desktop (1024px+) | 280px | Fixed visible | N/A |
| Tablet (768-1023px) | 250px | Fixed visible | N/A |
| Mobile (<768px) | 70vw | Hidden by default | Toggle button |

---

## 🎯 Benefits

✅ **Better Organization** - All navigation in one place
✅ **More Content Space** - Full width for landing/sub-sites
✅ **Professional Look** - Modern sidebar design
✅ **Easy Navigation** - Clear visual hierarchy
✅ **Mobile Friendly** - Hidden on small screens
✅ **Always Accessible** - Quick access to all pages
✅ **Consistent Design** - Same style across all pages

---

## 📞 Customization

### Change Sidebar Width
Edit in `styles.css`:
```css
.navbar {
    width: 300px;  /* Change from 280px to desired width */
}
body {
    margin-left: 300px;  /* Must match sidebar width */
}
```

### Add More Menu Items
Edit HTML files (index.html, oportunidades.html, etc.):
```html
<li class="nav-item">
    <a href="/new-page" class="nav-link">
        <i class="fas fa-icon-name"></i>
        <span>Menu Item</span>
    </a>
</li>
```

### Change Colors
Edit CSS variables in `styles.css`:
```css
.navbar {
    background: linear-gradient(180deg, #YOUR-COLOR-1 0%, #YOUR-COLOR-2 100%);
}
```

---

## 🐛 Troubleshooting

**Sidebar not showing on mobile?**
- Check if `sidebar.js` is loaded
- Clear browser cache and refresh
- Check browser console for errors

**Active link not highlighting?**
- Ensure link href matches current URL path
- Check that `sidebar.js` is loaded after HTML

**Sidebar overlapping content?**
- Check `body { margin-left: ... }` is applied
- Verify CSS file is loaded correctly

---

## 📚 Documentation Files

- **SIDEBAR_NAVIGATION_GUIDE.md** - This file
- **styles.css** - All sidebar styling
- **sidebar.js** - JavaScript functionality
- All HTML pages - Navigation structure

---

**Created**: November 12, 2025
**Version**: 1.0
**Status**: ✅ Complete & Production Ready

---

## 🚀 Next Steps

1. ✅ Sidebar implemented across all pages
2. ✅ Mobile toggle functionality working
3. ✅ Active link highlighting implemented
4. ⏳ Add sidebar animations (optional)
5. ⏳ Add submenu support (optional)
6. ⏳ Add notification badges (optional)

Enjoy your new sidebar navigation! 🎉
