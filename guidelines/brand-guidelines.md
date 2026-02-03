# APPDRAFT Brand Guidelines

## Brand Overview

**Company:** APPDRAFT
**Industry:** Salesforce Consulting
**Tagline:** Salesforce consulting excellence

---

## Logo

### Primary Logo
- **Text:** APPDRAFT (uppercase)
- **Font:** Eurostile BQ Extended
- **Color:** Dark teal on light backgrounds

### Logo Variations
1. **Colour Logo** - For light backgrounds (#f7f9fb, white)
2. **White Logo** - For dark backgrounds, primary color backgrounds

### Clear Space
Maintain minimum clear space around the logo equal to the height of the "A" in APPDRAFT.

### Minimum Size
- Digital: 100px width minimum
- Print: 1 inch width minimum

---

## Color Palette

### Primary Colors

| Color | Hex | RGB | Usage |
|-------|-----|-----|-------|
| Primary Cyan | #3cd6bf | 60, 214, 191 | Buttons, links, accents |
| Primary Hover | #2bc4ad | 43, 196, 173 | Hover states |
| Bright Cyan | #56FFDD | 86, 255, 221 | Footer links, dark bg highlights |

### Dark Colors

| Color | Hex | RGB | Usage |
|-------|-----|-----|-------|
| Dark (Slate) | #0f172a | 15, 23, 42 | CTA buttons, headers |
| Dark Hover | #1e293b | 30, 41, 59 | Hover states |

### Neutral Colors

| Color | Hex | RGB | Usage |
|-------|-----|-----|-------|
| Background | #f7f9fb | 247, 249, 251 | Page backgrounds |
| Border | #dce3ea | 220, 227, 234 | Borders, dividers |
| Main Text | #1f2d3d | 31, 45, 61 | Headings, body text |
| Muted Text | #6b778c | 107, 119, 140 | Captions, metadata |

---

## Typography

### Primary Font: Inter

A modern, highly readable sans-serif font for all UI and body text.

```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

### Font Weights
- **Light (300):** Large display text
- **Regular (400):** Body text
- **Medium (500):** Buttons, labels
- **Semibold (600):** Headings
- **Bold (700):** Strong emphasis

---

## UI Components

### Buttons

**Primary Button (Cyan)**
```css
background: #3cd6bf;
color: white;
border-radius: 8px;
font-weight: 500;
```
```css
/* Hover */
background: #2bc4ad;
```

**Dark CTA Button**
```css
background: #0f172a;
color: white;
border-radius: 8px;
font-weight: 500;
```
```css
/* Hover */
background: #1e293b;
```

**Secondary Button**
```css
background: #f7f9fb;
color: #1f2d3d;
border: 1px solid #dce3ea;
border-radius: 8px;
```

### Cards
```css
background: white;
border: 1px solid #dce3ea;
border-radius: 12px;
box-shadow: 0 1px 3px rgba(0,0,0,0.1);
```

### Links

**On light backgrounds:**
```css
color: #3cd6bf;
/* Hover */
color: #2bc4ad;
```

**On dark backgrounds (footer):**
```css
color: #6b778c;
/* Hover */
color: #56FFDD;
```

---

## Applications

### Website
- `appdraft.com`
- Light theme with cyan accents
- Dark CTA buttons
- Bright cyan for footer links

### Recordings Viewer
- `recordings.appdraft.com`
- Light header with logo
- Primary cyan buttons

### AppDraft Hub
- `hub.appdraft.com`
- Admin portal styling
- Full brand palette

### Chrome Extension
- Jeeves sidebar
- Compact brand elements

---

## Do's and Don'ts

### Do
- Use official logo files
- Maintain clear space around logo
- Use brand colors consistently
- Use Inter font for all text
- Use bright cyan (#56FFDD) on dark backgrounds

### Don't
- Stretch or distort the logo
- Change logo colors arbitrarily
- Use low-resolution logo files
- Mix brand fonts with others
- Use the standard cyan (#3cd6bf) on dark backgrounds (use #56FFDD instead)

---

## Changelog

### v2.0.0 (February 2026)
- Updated primary color from teal (#19779b) to vibrant cyan (#3cd6bf)
- Added bright cyan variant (#56FFDD) for dark backgrounds
- Replaced coral accent (#f25c54) with dark slate (#0f172a) for CTA buttons
- Updated border radius from 6px to 8px

### v1.0.0 (Initial)
- Original brand colors with teal primary
