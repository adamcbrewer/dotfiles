import QtQuick
import Quickshell
import Quickshell.Io
import qs.Commons
import qs.Ui

BarWidget {
  id: root
  moduleName: "adam.nordvpn"

  readonly property string connectionUuid: String(setting("connectionUuid", ""))
  readonly property string scriptPath: String(Qt.resolvedUrl("vpn.py")).replace(/^file:\/\//, "")
  property bool available: false
  property bool connected: false
  property bool loading: true
  property string connectionName: "NordVPN"
  property string errorMessage: ""

  function applyStatus(text) {
    try {
      var status = JSON.parse(String(text || "{}"))
      available = Boolean(status.available)
      connected = Boolean(status.connected)
      connectionName = String(status.name || "NordVPN")
      errorMessage = String(status.error || "")
    } catch (_error) {
      errorMessage = "Invalid VPN status response"
    }
    loading = false
  }

  function refresh() {
    if (statusProcess.running || toggleProcess.running) return
    statusProcess.running = true
  }

  function toggle() {
    if (statusProcess.running || toggleProcess.running) return
    loading = true
    errorMessage = ""
    toggleProcess.running = true
  }

  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  Component.onCompleted: Qt.callLater(refresh)

  Process {
    id: statusProcess
    command: ["/usr/bin/env", "python3", root.scriptPath, "status", root.connectionUuid]

    stdout: StdioCollector {
      waitForEnd: true
      onStreamFinished: root.applyStatus(text)
    }
  }

  Process {
    id: toggleProcess
    command: ["/usr/bin/env", "python3", root.scriptPath, "toggle", root.connectionUuid]

    stdout: StdioCollector {
      waitForEnd: true
      onStreamFinished: root.applyStatus(text)
    }
  }

  Timer {
    interval: 5000
    running: true
    repeat: true
    onTriggered: root.refresh()
  }

  WidgetButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: root.loading ? "VPN..." : (root.connected ? "VPN ON" : "VPN")
    active: root.connected || root.errorMessage !== ""
    tooltipText: root.errorMessage !== ""
      ? root.errorMessage
      : root.connectionName + (root.connected ? " connected" : " disconnected")
    horizontalMargin: 8.5

    onPressed: function(buttonCode) {
      if (buttonCode === Qt.RightButton) root.refresh()
      else root.toggle()
    }
  }
}
