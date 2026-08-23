import QtQuick
import QtQuick.Layouts
import Quickshell.Hyprland
import qs.Commons
import qs.Ui

BarWidget {
  id: root
  moduleName: "omarchy.workspaces"

  function workspaceById(id) {
    var values = Hyprland.workspaces.values
    for (var i = 0; i < values.length; i++) {
      if (values[i].id === id) return values[i]
    }

    return null
  }

  function workspaceIds() {
    var ids = [1, 2]
    var values = Hyprland.workspaces.values
    var scratchpadId = null

    for (var i = 0; i < values.length; i++) {
      var workspace = values[i]
      var id = workspace.id
      if (id > 0 && id <= 10 && ids.indexOf(id) === -1) ids.push(id)
      if (workspace.name === "special:scratchpad" && workspace.toplevels.values.length > 0) scratchpadId = id
    }

    ids.sort(function(left, right) { return left - right })
    if (scratchpadId !== null) ids.unshift(scratchpadId)
    return ids
  }

  function focusWorkspace(id) {
    if (!root.bar) return
    root.bar.run("hyprctl dispatch " + Util.shellQuote("hl.dsp.focus({ workspace = \"" + id + "\" })"))
  }

  function toggleScratchpad() {
    if (!root.bar) return
    root.bar.run("hyprctl dispatch " + Util.shellQuote("hl.dsp.workspace.toggle_special(\"scratchpad\")"))
  }

  readonly property real trailingGap: root.vertical ? 0 : Style.spaceReal(1.5)

  implicitWidth: grid.implicitWidth + trailingGap
  implicitHeight: grid.implicitHeight

  GridLayout {
    id: grid
    anchors.fill: parent
    anchors.rightMargin: root.trailingGap
    columns: root.vertical ? 1 : root.workspaceIds().length
    columnSpacing: root.vertical ? 0 : Style.space(1)
    rowSpacing: root.vertical ? Style.space(2) : 0

    Repeater {
      model: root.workspaceIds()

      WidgetButton {
        id: button
        required property int modelData

        readonly property var workspace: root.workspaceById(modelData)
        readonly property bool occupied: workspace !== null && workspace.toplevels.values.length > 0
        readonly property bool focused: modelData < 0
          ? Hyprland.activeToplevel !== null && Hyprland.activeToplevel.workspace === workspace
          : Hyprland.focusedWorkspace !== null && Hyprland.focusedWorkspace.id === modelData

        bar: root.bar
        text: modelData < 0 ? "S" : (modelData === 10 ? "0" : String(modelData)) + (workspace !== null && workspace.hasFullscreen ? "·" : "")
        opacity: occupied || focused ? 1 : 0.5
        horizontalMargin: 6
        verticalPadding: 6
        fixedWidth: root.vertical ? root.barSize : Style.space(20)
        fixedHeight: root.barSize
        onPressed: function() {
          if (modelData < 0) root.toggleScratchpad()
          else root.focusWorkspace(modelData)
        }

        Rectangle {
          anchors.bottom: parent.bottom
          anchors.bottomMargin: 3
          anchors.horizontalCenter: parent.horizontalCenter
          width: Math.max(button.labelWidth, 8)
          height: 2
          radius: 1
          color: button.foreground
          visible: button.focused
          z: 1
        }
      }
    }
  }
}
