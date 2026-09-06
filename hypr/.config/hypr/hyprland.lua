-- Learn how to configure Hyprland: https://wiki.hypr.land/Configuring/Start/

-- Omarchy's bootstrap keeps path setup out of this user config.
dofile((os.getenv("OMARCHY_PATH") or "/usr/share/omarchy") .. "/default/hypr/bootstrap.lua")

-- Disable all Omarchy default bindings. Add your own in hypr/bindings.lua.
-- omarchy_default_bindings = false
--
-- Or disable only bindings for Omarchy's preinstalled apps/web apps while
-- keeping core window-manager bindings:
-- omarchy_preinstalled_bindings = false

-- Load Omarchy defaults.
require("default.hypr.omarchy")

-- Put your personal overrides in these files. They're loaded after Omarchy's
-- defaults so package updates can improve the defaults without rewriting your
-- ~/.config/hypr files.
require("hypr.monitors")
require("hypr.input")
require("hypr.bindings")
require("hypr.looknfeel")
require("hypr.autostart")

hl.unbind("SUPER + J")
o.bind("SUPER + J", "Toggle window split", function()
  local workspace = hl.get_active_special_workspace() or hl.get_active_workspace()

  if not workspace then
    return
  end

  if workspace.tiled_layout == "scrolling" then
    hl.dispatch(hl.dsp.layout("consume_or_expel prev"))
  elseif workspace.tiled_layout == "dwindle" then
    hl.dispatch(hl.dsp.layout("togglesplit"))
  end
end)

dofile(os.getenv("HOME") .. "/.config/omarchy/plugins/adam.altswitch/altswitch.lua")

hl.env("SSH_AUTH_SOCK", os.getenv("XDG_RUNTIME_DIR") .. "/gcr/ssh")

-- Toggle config flags dynamically.
require("default.hypr.toggles")

-- Add any other personal Hyprland configuration below.
-- o.window("qemu", { workspace = "5" })

o.window({ workspace = "special:scratchpad" }, { opacity = "1.0 override 1.0 override", dim_around = true })
hl.workspace_rule({ workspace = "special:scratchpad", gaps_out = 40 })
hl.workspace_rule({ workspace = "f[1] s[true] w[2-2147483647]", gaps_out = 60 })
