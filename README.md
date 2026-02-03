# APPDRAFT Brand Assets

Official brand assets for APPDRAFT Salesforce Consulting.

## Quick Reference

### CDN URLs (after GitHub push)

```
Logo (Blue):  https://cdn.jsdelivr.net/gh/draftrepo/appdraft-brand-assets@main/logos/appdraft-logo-blue.png
Logo (White): https://cdn.jsdelivr.net/gh/draftrepo/appdraft-brand-assets@main/logos/appdraft-logo-white.png
Colors CSS:   https://cdn.jsdelivr.net/gh/draftrepo/appdraft-brand-assets@main/colors/colors.css
Inter Font:   https://cdn.jsdelivr.net/gh/draftrepo/appdraft-brand-assets@main/fonts/inter.css
```

### Brand Colors

| Color | Hex | Usage |
|-------|-----|-------|
| Primary (Cyan) | `#3cd6bf` | Buttons, links, accents |
| Primary Hover | `#2bc4ad` | Hover states |
| Bright Accent | `#56FFDD` | Footer links, highlights |
| Background | `#f7f9fb` | Page backgrounds |
| Border | `#dce3ea` | Dividers |
| Text | `#1f2d3d` | Main text |
| Text Muted | `#6b778c` | Secondary text |
| Dark (CTA) | `#0f172a` | Dark buttons, headers |

### Quick CSS

```css
:root {
  --appdraft-primary: #3cd6bf;
  --appdraft-primary-hover: #2bc4ad;
  --appdraft-bright: #56FFDD;
  --appdraft-background: #f7f9fb;
  --appdraft-border: #dce3ea;
  --appdraft-text: #1f2d3d;
  --appdraft-text-muted: #6b778c;
  --appdraft-dark: #0f172a;
}
```

## Directory Structure

```
appdraft-brand-assets/
├── README.md
├── logos/
│   ├── appdraft-logo-blue.png    # For light backgrounds
│   └── appdraft-logo-white.png   # For dark backgrounds
├── colors/
│   ├── colors.json               # JSON color definitions
│   └── colors.css                # CSS variables & utilities
├── fonts/
│   ├── inter.css                 # Inter font with variables
│   └── typography-guide.md       # Typography documentation
└── guidelines/
    └── brand-guidelines.md       # Complete brand guidelines
```

## Usage

### HTML

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/draftrepo/appdraft-brand-assets@main/colors/colors.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/draftrepo/appdraft-brand-assets@main/fonts/inter.css">

<img src="https://cdn.jsdelivr.net/gh/draftrepo/appdraft-brand-assets@main/logos/appdraft-logo-blue.png" alt="APPDRAFT" height="40">
```

### React/JavaScript

```jsx
const BRAND = {
  logo: {
    blue: 'https://cdn.jsdelivr.net/gh/draftrepo/appdraft-brand-assets@main/logos/appdraft-logo-blue.png',
    white: 'https://cdn.jsdelivr.net/gh/draftrepo/appdraft-brand-assets@main/logos/appdraft-logo-white.png'
  },
  colors: {
    primary: '#3cd6bf',
    primaryHover: '#2bc4ad',
    bright: '#56FFDD',
    background: '#f7f9fb',
    border: '#dce3ea',
    text: '#1f2d3d',
    textMuted: '#6b778c',
    dark: '#0f172a'
  }
};
```

### Tailwind CSS (arbitrary values)

```jsx
// Primary button
className="bg-[#3cd6bf] hover:bg-[#2bc4ad] text-white"

// Text accent
className="text-[#3cd6bf]"

// Footer links (dark bg)
className="text-gray-400 hover:text-[#56FFDD]"

// Dark CTA button
className="bg-slate-900 hover:bg-slate-800 text-white"
```

## Logo Files Needed

Add to the `logos/` folder:
- `appdraft-logo-blue.png` - Blue logo for light backgrounds
- `appdraft-logo-white.png` - White logo for dark backgrounds

You can export these from your existing logo source files.

## License

Copyright APPDRAFT. All rights reserved.
