local switcher = { windows = {}, index = 1, active = false, session = 0, revision = 0 }
local controller = tostring(switcher)

local function shell_quote(value)
  return "'" .. tostring(value):gsub("'", "'\\''") .. "'"
end

local function json_string(value)
  local escaped = tostring(value or "")
    :gsub("\\", "\\\\")
    :gsub('"', '\\"')
    :gsub("[%c]", function(control)
      return string.format("\\u%04x", control:byte())
    end)
  return '"' .. escaped .. '"'
end

local function payload()
  local rows = {}
  for _, window in ipairs(switcher.windows) do
    rows[#rows + 1] = string.format(
      '{"title":%s,"appClass":%s,"workspace":%s}',
      json_string(window.title),
      json_string(window.class),
      json_string(window.workspace and window.workspace.name or "")
    )
  end

  return string.format(
    '{"controller":%s,"revision":%d,"session":%d,"active":%s,"windows":[%s],"index":%d}',
    json_string(controller),
    switcher.revision,
    switcher.session,
    tostring(switcher.active),
    table.concat(rows, ","),
    switcher.index - 1
  )
end

local function send()
  switcher.revision = switcher.revision + 1
  hl.exec_cmd("omarchy-shell -q adam-altswitch sync " .. shell_quote(payload()))
end

local function teardown()
  switcher.active = false
  switcher.windows = {}
  send()
end

local function commit()
  if not switcher.active then return end

  local target = switcher.windows[switcher.index]
  local address = target and target.address
  teardown()

  if address then
    local focus = string.format('hl.dsp.focus({ window = "address:%s" })', address)
    hl.exec_cmd("hyprctl dispatch " .. shell_quote(focus))
  end
end

local function snapshot()
  local windows = {}
  for _, window in ipairs(hl.get_windows()) do
    local workspace = window.workspace
    if window.mapped and workspace and not workspace.special then
      windows[#windows + 1] = window
    end
  end

  table.sort(windows, function(a, b)
    return a.focus_history_id < b.focus_history_id
  end)
  return windows
end

local function step(delta)
  if switcher.active then
    switcher.index = (switcher.index - 1 + delta) % #switcher.windows + 1
    send()
    return
  end

  switcher.windows = snapshot()
  if #switcher.windows < 2 then return end

  switcher.index = delta % #switcher.windows + 1
  switcher.session = switcher.session + 1
  switcher.active = true
  send()
end

_G.__adam_altswitch_cancel = function(session, owner)
  if session == switcher.session and owner == controller then teardown() end
end

_G.__adam_altswitch_choose = function(index, session, owner, activate)
  if not switcher.active or session ~= switcher.session or owner ~= controller then return end
  if type(index) ~= "number" or index % 1 ~= 0 or index < 0 or index >= #switcher.windows then return end

  switcher.index = index + 1
  if activate then commit() else send() end
end

hl.layer_rule({ match = { namespace = "^adam-altswitch$" }, no_anim = true, animation = "none" })

hl.unbind("SUPER + TAB")
hl.unbind("SUPER + SHIFT + TAB")
hl.bind("SUPER + TAB", function() step(1) end, { description = "Switch window" })
hl.bind("SUPER + SHIFT + TAB", function() step(-1) end, { description = "Switch window (reverse)" })
hl.bind("SUPER + SHIFT + ESCAPE", teardown, { non_consuming = true, description = "Cancel window switch" })

local SUPER_KEYCODES = {
  [125] = true,
  [126] = true,
  [133] = true,
  [134] = true,
}

hl.on("input.keyboard.key", function(keycode, _, state)
  if state == 0 and switcher.active and SUPER_KEYCODES[keycode] then
    commit()
  end
end)
