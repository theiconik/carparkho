# Car Parkho UI - Design System

This document outlines the core visual primitives and component states for the "Find your right car" widget.

## 1. Color Palette

### Brand & Interactive Colors

| Color Name        | Hex Code  | Usage                                                     |
| :---------------- | :-------- | :-------------------------------------------------------- |
| **Primary Coral** | `#F05C35` | Primary buttons, active radio buttons, active state text. |
| **Charcoal Dark** | `#2A2C32` | Active tab background, primary headings.                  |

### Neutrals (Surfaces & Text)

| Color Name         | Hex Code  | Usage                                              |
| :----------------- | :-------- | :------------------------------------------------- |
| **Surface White**  | `#FFFFFF` | Card background, input backgrounds, inactive tabs. |
| **Text Secondary** | `#7A7D82` | Placeholder text, inactive text, secondary links.  |
| **Border Light**   | `#D1D4D7` | Input borders, tab borders, inactive radio rings.  |

---

## 2. Typography

**Font Family:** `Inter`, `Proxima Nova`, or similar modern Sans-Serif.

### Type Scale & Usage

- **Heading 2 (H2):** 24px, Bold (700), Color: `Charcoal Dark`
  - _Usage:_ Widget Title ("Find your right car")
- **Button Text:** 16px, Bold (700), Color: `Surface White`
  - _Usage:_ Primary CTA ("Search")
- **Tab Text:** 14px, Semi-Bold (600)
  - _Active:_ Color: `Surface White`
  - _Inactive:_ Color: `Text Secondary`
- **Label Text:** 14px, Semi-Bold (600)
  - _Active:_ Color: `Primary Coral` ("By Budget")
  - _Inactive:_ Color: `Text Secondary` ("By Brand")
- **Input Text:** 14px, Regular (400), Color: `Text Secondary`
  - _Usage:_ Dropdown placeholders, secondary links.

---

## 3. UI Components

### 3.1 Buttons

**Primary Button (Search)**

- **Background:** `Primary Coral` (`#F05C35`)
- **Text:** `Surface White`, Bold
- **Border-Radius:** 8px (approx)
- **Padding:** 12px 24px (full width of container)

### 3.2 Segmented Controls / Tabs

- **Container:** Flex row, 8px gap.
- **Active Tab:**
  - Background: `Charcoal Dark`
  - Text: `Surface White`
  - Border: None
  - Shape: Rounded corners (approx 8px) with a downward-pointing caret at the bottom center.
- **Inactive Tab:**
  - Background: `Surface White`
  - Text: `Text Secondary`
  - Border: 1px solid `Border Light`
  - Shape: Rounded corners (approx 8px).

### 3.3 Inputs & Selects

**Dropdown Menus**

- **Background:** `Surface White`
- **Border:** 1px solid `Border Light` (overlapping borders on stacked inputs)
- **Border-Radius:** 8px (Top input has rounded top corners, bottom input has rounded bottom corners)
- **Text:** `Text Secondary`
- **Icon:** Downward chevron on the right side.

### 3.4 Radio Buttons

- **Active State:** \* Outer Ring: 1px solid `Primary Coral`
  - Inner Dot: `Primary Coral`
  - Label: `Primary Coral`, Semi-Bold
- **Inactive State:**
  - Outer Ring: 1px solid `Border Light`
  - Inner Dot: None
  - Label: `Text Secondary`, Semi-Bold

### 3.5 Links

**Secondary Link (Advanced Search)**

- **Text:** `Text Secondary`, 14px, Regular
- **Icon:** Right-pointing arrow (`→`) next to the text.
- **Hover State (Implied):** Underline or color shift to `Charcoal Dark`.
