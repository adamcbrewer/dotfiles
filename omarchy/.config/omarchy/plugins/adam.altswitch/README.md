# Alt Switch dependencies

- Omarchy 4 shell and its Hyprland Lua runtime
- `omarchy-shell` and `hyprctl`
- `$HOME`, used to locate this plugin from the Hyprland configuration

No Lime80-specific binding or package is required. The preferred `DP-2`
display falls back to the first available display.

## Shortcuts

- Hold Super and press Tab to cycle windows in recent-focus order.
- Super+Shift+Tab cycles backwards; release Super to focus the selection.
- Super+Shift+Escape cancels the selection (Super+Escape opens Omarchy's system menu).
- Move the pointer over a row to select it; click to focus it immediately.

The overlay appears after holding the shortcut for 150 ms and has no fade or
slide animation. Quick taps still switch windows without showing the overlay.
The pointer must move to select a row, so opening under a stationary pointer
does not replace the keyboard selection.

Super+Tab and Super+Shift+Tab override Omarchy's next/previous workspace
bindings. Icons resolve from desktop entries through Quickshell directly;
Omarchy 4.0.3 only exposes `shell.appLibrary` to menu plugins.
