-- Learn how to configure Hyprland: https://wiki.hypr.land/Configuring/Start/

-- Omarchy's bootstrap keeps path setup out of this user config.
dofile((os.getenv("OMARCHY_PATH") or "/usr/share/omarchy") .. "/default/hypr/bootstrap.lua")

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

hl.unbind("SUPER + SPACE")
o.bind("SUPER + SPACE", "oma-cast launcher", hl.dsp.global("oma-cast:toggle"))

hl.unbind("SUPER + F")
hl.unbind("SUPER + ALT + F")
o.bind("SUPER + F", "Full width", hl.dsp.window.fullscreen({ mode = "maximized" }))
o.bind("SUPER + ALT + F", "Full screen", hl.dsp.window.fullscreen({ mode = "fullscreen" }))

local function get_active_workspace()
  return hl.get_active_special_workspace() or hl.get_active_workspace()
end

hl.unbind("SUPER + J")
o.bind("SUPER + J", "Toggle window split", function()
  local workspace = get_active_workspace()

  if not workspace then
    return
  end

  if workspace.tiled_layout == "scrolling" then
    hl.dispatch(hl.dsp.layout("consume_or_expel prev"))
  elseif workspace.tiled_layout == "dwindle" then
    hl.dispatch(hl.dsp.layout("togglesplit"))
  end
end)

local altswitch_path = os.getenv("HOME") .. "/.config/omarchy/plugins/adam.altswitch/altswitch.lua"
local altswitch_file = io.open(altswitch_path, "r")
if altswitch_file then
  altswitch_file:close()
  dofile(altswitch_path)
end

local camera_path = os.getenv("HOME") .. "/.config/omarchy/plugins/adam.camera/camera.lua"
local camera_file = io.open(camera_path, "r")
if camera_file then
  camera_file:close()
  dofile(camera_path)
end

hl.env("SSH_AUTH_SOCK", os.getenv("XDG_RUNTIME_DIR") .. "/gcr/ssh")
hl.env("QT_LOGGING_RULES", "qt.multimedia.*=false")

-- Toggle config flags dynamically.
require("default.hypr.toggles")
require("hypr.scratchpad-layout")
require("hypr.qconsole")

hl.workspace_rule({ workspace = "special:scratchpad", gaps_out = 40 })
