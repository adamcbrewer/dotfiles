local M = {}
local console = "special:qconsole"
local scratchpad = "special:scratchpad"
local return_to_scratchpad = {}
local launch = "omarchy-launch-terminal --app-id=org.adam.qconsole --title='Quake console' fish -C fastfetch"

-- Keep this override after stock Quake sizing updates.
hl.workspace_rule({
  workspace = "name:" .. console,
  no_border = true,
  no_rounding = true,
  on_created_empty = "[workspace " .. console .. " silent] " .. launch,
})

function M.toggle()
  local monitor = hl.get_active_monitor()
  if not monitor then return end
  local active = hl.get_active_special_workspace(monitor)

  if active and active.name == console then
    local restore = return_to_scratchpad[monitor.name]
    return_to_scratchpad[monitor.name] = nil
    hl.dispatch(hl.dsp.workspace.toggle_special("qconsole"))

    local workspace = hl.get_workspace(scratchpad)
    if restore and workspace and not workspace.visible
      and #hl.get_workspace_windows(scratchpad) > 0 then
      hl.dispatch(hl.dsp.workspace.toggle_special("scratchpad"))
    end
  else
    return_to_scratchpad[monitor.name] = active and active.name == scratchpad or false
    hl.dispatch(hl.dsp.workspace.toggle_special("qconsole"))
  end
end

o.rebind("SUPER + grave", "Toggle Quake console and restore scratchpad", M.toggle)

return M
