local lime80 = "2.4g-iqunix-receiver-keyboard"
local function lime80_fn(key, function_key)
  hl.bind(key, hl.dsp.send_shortcut({ mods = "", key = function_key }), {
    description = "Fn+" .. function_key,
    device = { list = { lime80 } },
  })
end

for number = 1, 12 do
  hl.unbind("F" .. number)
end
o.bind("F7", "Previous track", "omarchy-shell media previous", { locked = true })
o.bind("F8", "Play/pause", "omarchy-shell media playPause", { locked = true })
o.bind("F9", "Next track", "omarchy-shell media next", { locked = true })
o.bind("F10", "Mute", "omarchy-audio-output-volume mute-toggle", { locked = true })
o.bind("F11", "Volume down", "omarchy-audio-output-volume lower", { locked = true, repeating = true })
o.bind("F12", "Volume up", "omarchy-audio-output-volume raise", { locked = true, repeating = true })

hl.unbind("CTRL + ALT + DELETE")
o.bind("CTRL + ALT + DELETE", "Close all windows", "omarchy-hyprland-window-close-all", {
  device = { inclusive = false, list = { lime80 } },
})
lime80_fn("XF86Explorer", "F5")
lime80_fn("XF86HomePage", "F6")
lime80_fn("CTRL + ALT + DELETE", "F7")
hl.unbind("XF86Calculator")
lime80_fn("XF86Calculator", "F8")

hl.unbind("XF86AudioMute")
hl.unbind("XF86AudioLowerVolume")
hl.unbind("XF86AudioRaiseVolume")
o.bind("XF86AudioMute", "Mute", "omarchy-audio-output-volume mute-toggle", {
  locked = true,
  device = { inclusive = false, list = { lime80 } },
})
o.bind("XF86AudioLowerVolume", "Volume down", "omarchy-audio-output-volume lower", {
  locked = true,
  repeating = true,
  device = { inclusive = false, list = { lime80 } },
})
o.bind("XF86AudioRaiseVolume", "Volume up", "omarchy-audio-output-volume raise", {
  locked = true,
  repeating = true,
  device = { inclusive = false, list = { lime80 } },
})
lime80_fn("XF86AudioMute", "F9")
lime80_fn("XF86AudioLowerVolume", "F10")
lime80_fn("XF86AudioRaiseVolume", "F11")
-- strata-installer: file-manager start
hl.unbind("SUPER + SHIFT + F")
hl.unbind("SUPER + ALT + SHIFT + F")
o.bind("SUPER + SHIFT + F", "File manager", { launch = "/home/adam/.local/bin/strata" })
o.bind("SUPER + ALT + SHIFT + F", "File manager (cwd)",
  "uwsm-app -- /home/adam/.local/bin/strata \"$(omarchy-cmd-terminal-cwd)\"")
-- strata-installer: file-manager end
