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
| Primary | `#19779b` | Buttons, links |
| Primary Hover | `#14698c` | Hover states |
| Accent | `#f25c54` | CTAs, alerts |
| Background | `#f7f9fb` | Page backgrounds |
| Border | `#dce3ea` | Dividers |
| Text | `#1f2d3d` | Main text |
| Text Muted | `#6b778c` | Secondary text |
| Logo | `#0b3d52` | Logo color |

### Quick CSS

```css
:root {
  --appdraft-primary: #19779b;
  --appdraft-primary-hover: #14698c;
  --appdraft-accent: #f25c54;
  --appdraft-background: #f7f9fb;
  --appdraft-border: #dce3ea;
  --appdraft-text: #1f2d3d;
  --appdraft-text-muted: #6b778c;
  --appdraft-logo: #0b3d52;
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
    primary: '#19779b',
    primaryHover: '#14698c',
    accent: '#f25c54',
    background: '#f7f9fb',
    border: '#dce3ea',
    text: '#1f2d3d',
    textMuted: '#6b778c',
    logo: '#0b3d52'
  }
};
```

## Logo Files Needed

Add to the `logos/` folder:
- `appdraft-logo-blue.png` - Blue logo for light backgrounds
- `appdraft-logo-white.png` - White logo for dark backgrounds

You can export these from your existing logo source files.

## License

Copyright APPDRAFT. All rights reserved.
