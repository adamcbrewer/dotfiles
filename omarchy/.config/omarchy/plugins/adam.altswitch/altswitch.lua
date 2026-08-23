local switcher = { windows = {}, index = 1, active = false }

local function shell_quote(value)
  return "'" .. tostring(value):gsub("'", "'\\''") .. "'"
end

local function send(method, argument)
  local command = "omarchy-shell -q adam-altswitch " .. method
  if argument then
    command = command .. " " .. shell_quote(argument)
  end
  hl.exec_cmd(command)
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
    '{"windows":[%s],"index":%d}',
    table.concat(rows, ","),
    switcher.index - 1
  )
end

local function teardown()
  switcher.active = false
  switcher.windows = {}
  send("hide")
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
    send("select", tostring(switcher.index - 1))
    return
  end

  switcher.windows = snapshot()
  if #switcher.windows < 2 then return end

  switcher.index = delta % #switcher.windows + 1
  switcher.active = true
  send("show", payload())
end

_G.__adam_altswitch_cancel = teardown

hl.unbind("ALT + TAB")
hl.unbind("ALT + SHIFT + TAB")
hl.bind("ALT + TAB", function() step(1) end, { description = "Switch window" })
hl.bind("ALT + SHIFT + TAB", function() step(-1) end, { description = "Switch window (reverse)" })
hl.bind("ALT + ESCAPE", teardown, { non_consuming = true, description = "Cancel window switch" })

local ALT_KEYCODES = {
  [37] = true,
  [64] = true,
  [105] = true,
  [108] = true,
}

hl.on("input.keyboard.key", function(keycode, _, state)
  if state == 0 and switcher.active and ALT_KEYCODES[keycode] then
    commit()
  end
end)
