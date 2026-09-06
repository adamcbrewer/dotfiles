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

hl.unbind("SUPER + L")
o.bind("SUPER + L", "Toggle workspace layout", function()
  local workspace = get_active_workspace()

  if not workspace then
    return
  elseif not workspace.special then
    hl.exec_cmd("omarchy-hyprland-workspace-layout-toggle")
    return
  end

  local layout = workspace.tiled_layout == "dwindle" and "scrolling" or "dwindle"
  local layouts_dir = (os.getenv("XDG_STATE_HOME") or os.getenv("HOME") .. "/.local/state") .. "/omarchy/workspace-layouts"

  os.execute("mkdir -p " .. o.shell_quote(layouts_dir))

  local file = io.open(layouts_dir .. "/" .. workspace.id .. ".lua", "w")
  if file then
    file:write(string.format("hl.workspace_rule({ workspace = %q, layout = %q })\n", workspace.name, layout))
    file:close()
  end

  hl.workspace_rule({ workspace = workspace.name, layout = layout })
  hl.exec_cmd(o.notify("Workspace layout set to " .. layout))
end)

dofile(os.getenv("HOME") .. "/.config/omarchy/plugins/adam.altswitch/altswitch.lua")

hl.env("SSH_AUTH_SOCK", os.getenv("XDG_RUNTIME_DIR") .. "/gcr/ssh")

-- Toggle config flags dynamically.
require("default.hypr.toggles")

-- Add any other personal Hyprland configuration below.
-- o.window("qemu", { workspace = "5" })

hl.workspace_rule({ workspace = "special:scratchpad", gaps_out = 40 })
hl.workspace_rule({ workspace = "f[1] s[true] w[2-2147483647]", gaps_out = 60 })
