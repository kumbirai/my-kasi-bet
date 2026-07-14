# MyKasiBets Mini App Design System

## Scene and theme

A player checks a bet in a Telegram WebView while commuting or standing outdoors,
with changing ambient light and one thumb available. Telegram theme values are the
primary palette, with high-contrast light and dark fallbacks rather than a forced
theme.

## Color strategy

Use a restrained product shell with semantic game colors. All values use OKLCH.

- Canvas: `oklch(97% 0.008 85)` light, `oklch(18% 0.012 270)` dark fallback.
- Surface: `oklch(93% 0.012 85)` light, `oklch(23% 0.014 270)` dark fallback.
- Text: `oklch(22% 0.015 270)` light, `oklch(94% 0.008 85)` dark fallback.
- Muted text: `oklch(50% 0.018 270)` light, `oklch(72% 0.018 270)` dark fallback.
- Primary action: Telegram button color, fallback `oklch(56% 0.18 32)`.
- Success: `oklch(61% 0.15 150)`; error: `oklch(58% 0.19 25)`.
- Game colors pair hue with text labels and selection marks, never hue alone.

## Typography

Use the native system sans stack. Body is 1rem with 1.5 line height. Screen titles
are 1.5rem/700, section titles 1.125rem/700, labels 0.875rem/650, and supporting
copy 0.875rem/1.45. Numeric balances use tabular figures.

## Layout

- Design from 320px upward with 16px side gutters and Telegram stable viewport
  height variables.
- Keep primary content in one vertical flow. Avoid nested cards.
- Use 12px, 16px, 24px, and 32px rhythm with deliberate larger gaps between tasks.
- Reserve bottom space for Telegram MainButton and device safe-area insets.

## Components

- Header: balance and compact context, no decorative hero metric.
- Game list: full-width rows with distinct game information and explicit
  availability, not identical promotional cards.
- Choice tiles: minimum 56px, visible label, check state, focus ring, and pressed
  transform.
- Stake field: native numeric input with currency prefix, limits, inline error, and
  no silent coercion.
- Result: an inline status region using icon, text, and color. It remains in the
  game flow and never opens a modal.
- Errors: concise inline recovery states for auth, account, wallet, and network.

## Motion

Use 180–240ms ease-out-quart transitions. The confirmed color reveal may pulse
once for 500ms. Under `prefers-reduced-motion`, skip interpolation and render the
final state immediately. Never animate layout properties or start game outcome
motion before the API response arrives.
