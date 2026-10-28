local M = {}
local workspace_name = "special:scratchpad"
local floated_tag = "adam-scratchpad-floated"
local state_home = os.getenv("XDG_STATE_HOME") or os.getenv("HOME") .. "/.local/state"
local state_file = state_home .. "/omarchy/scratchpad-layout"
local modes = { "dwindle", "scrolling", "floating" }
local function read_mode()
  local file = io.open(state_file, "r")
  if file then
    local saved = file:read("*l")
    file:close()
    for _, candidate in ipairs(modes) do
      if saved == candidate then return saved end
    end
  end
  return "scrolling"
end
local mode = read_mode()

local function has_tag(window, tag)
  for _, value in ipairs(window.tags or {}) do
    if value == tag or value == tag .. "*" then return true end
  end
  return false
end

local function sync_window(window)
  if not window.mapped then return end

  local scratchpad = window.workspace and window.workspace.name == workspace_name
  if scratchpad and mode == "floating" then
    if not window.floating and (window.fullscreen or 0) == 0 then
      hl.dispatch(hl.dsp.window.tag({ tag = "+" .. floated_tag, window = window }))
      hl.dispatch(hl.dsp.window.float({ action = "on", window = window }))
    end
  elseif has_tag(window, floated_tag) then
    hl.dispatch(hl.dsp.window.tag({ tag = "-" .. floated_tag, window = window }))
    if not window.pinned and not has_tag(window, "omarchy-floating-workspace") then
      hl.dispatch(hl.dsp.window.float({ action = "off", window = window }))
    end
  end
end

local function apply()
  hl.workspace_rule({
    workspace = workspace_name,
    layout = mode == "floating" and "scrolling" or mode,
  })
  local windows = hl.get_windows()
  if mode == "floating" then
    for _, window in ipairs(windows) do
      if window.mapped and window.workspace and window.workspace.name == workspace_name
        and not window.floating and (window.fullscreen or 0) == 0 then
        hl.dispatch(hl.dsp.window.tag({ tag = "+" .. floated_tag, window = window }))
      end
    end
  end
  for _, window in ipairs(windows) do sync_window(window) end
end

function M.cycle(direction)
  mode = read_mode()
  local index = 1
  for i, candidate in ipairs(modes) do
    if candidate == mode then index = i end
  end
  local next_mode = modes[(index - 1 + direction) % #modes + 1]
  local state, error = io.open(state_file, "w")
  if not state then
    hl.exec_cmd(o.notify("Could not save scratchpad layout: " .. tostring(error)))
    return
  end
  local written, write_error = state:write(next_mode .. "\n")
  local closed, close_error = state:close()
  if not written or not closed then
    hl.exec_cmd(o.notify("Could not save scratchpad layout: " .. tostring(write_error or close_error)))
    return
  end
  mode = next_mode
  apply()
  hl.exec_cmd(o.notify("Scratchpad layout: " .. mode))
end

local function sync_later(window)
  local address = window.address
  hl.timer(function()
    local current = hl.get_window("address:" .. address)
    if current then sync_window(current) end
  end, { type = "oneshot", timeout = 1 })
end

hl.on("window.open", sync_later)
hl.on("window.move_to_workspace", sync_later)
hl.on("window.fullscreen", sync_later)

local function cycle(direction)
  local workspace = hl.get_active_special_workspace()
  if workspace and workspace.name == workspace_name then
    M.cycle(direction)
  elseif not workspace then
    hl.exec_cmd("omarchy-hyprland-workspace-layout-toggle" .. (direction < 0 and " back" or ""))
  end
end

o.rebind("SUPER + L", "Cycle workspace layout", function() cycle(1) end)
o.rebind("SUPER + ALT + L", "Cycle workspace layout back", function() cycle(-1) end)
apply()

return M
