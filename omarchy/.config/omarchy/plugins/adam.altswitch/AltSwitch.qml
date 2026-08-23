import Quickshell
import Quickshell.Io
import Quickshell.Wayland
import QtQuick
import QtQuick.Layouts
import qs.Commons
import qs.Ui

Item {
  id: root

  property var shell: null
  property bool opened: false
  property var windows: []
  property int selectedIndex: 0

  readonly property var appLibrary: shell ? shell.appLibrary : null
  readonly property var mainScreen: screenByName("DP-2")
  readonly property int rowHeight: Style.space(66)
  readonly property int headerHeight: Style.space(52)
  readonly property int footerHeight: Style.space(38)
  readonly property int cardWidth: Math.min(Style.space(680), panel.width - Style.gapsOut * 2)
  readonly property int maxCardHeight: panel.height - Style.gapsOut * 2

  function screenByName(name) {
    for (var i = 0; i < Quickshell.screens.length; i++) {
      if (Quickshell.screens[i].name === name) return Quickshell.screens[i]
    }
    return Quickshell.screens.length ? Quickshell.screens[0] : null
  }

  function normalized(value) {
    return String(value || "")
      .toLowerCase()
      .replace(/\.desktop$/, "")
      .replace(/[^a-z0-9]+/g, "")
  }

  function tail(value) {
    var parts = String(value || "").toLowerCase().replace(/\.desktop$/, "").split(/[.\/_-]+/)
    return parts.length ? parts[parts.length - 1] : ""
  }

  function entryScore(entry, appClass) {
    var app = root.normalized(appClass)
    var id = root.normalized(entry.id)
    var startup = ""
    try { startup = root.normalized(entry.startupWmClass || entry.startupWMClass) } catch (e) { }
    if (app && (app === id || app === startup)) return 100
    if (app && root.tail(appClass) === root.tail(entry.id)) return 80
    if (app && (app.indexOf(id) >= 0 || id.indexOf(app) >= 0)) return 60
    return 0
  }

  function iconForClass(appClass) {
    if (!root.appLibrary) return ""
    var entries = DesktopEntries.applications.values || []
    var best = null
    var bestScore = 0
    for (var i = 0; i < entries.length; i++) {
      var score = root.entryScore(entries[i], appClass)
      if (score > bestScore) {
        best = entries[i]
        bestScore = score
      }
    }
    return best && best.icon ? root.appLibrary.iconSource(best.icon) : ""
  }

  function initials(value) {
    var parts = String(value || "?").replace(/^.*\./, "").split(/[^A-Za-z0-9]+/).filter(function(part) { return part.length > 0 })
    if (!parts.length) return "?"
    if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
    return (parts[0].charAt(0) + parts[1].charAt(0)).toUpperCase()
  }

  function show(payloadJson) {
    watchdog.restart()
    var payload
    try {
      payload = JSON.parse(payloadJson)
    } catch (error) {
      console.warn("adam-altswitch: unreadable payload:", error)
      root.hide()
      return
    }

    var sourceWindows = Array.isArray(payload.windows) ? payload.windows : []
    var enriched = []
    for (var i = 0; i < sourceWindows.length; i++) {
      var window = sourceWindows[i]
      enriched.push({
        title: String(window.title || "Untitled window"),
        appClass: String(window.appClass || "Unknown"),
        workspace: String(window.workspace || "?"),
        icon: root.iconForClass(window.appClass)
      })
    }

    root.windows = enriched
    root.selectedIndex = Math.max(0, Math.min(Number(payload.index) || 0, enriched.length - 1))
    root.opened = enriched.length > 0
  }

  function select(index) {
    root.selectedIndex = Math.max(0, Math.min(Number(index) || 0, root.windows.length - 1))
    watchdog.restart()
  }

  function hide() {
    watchdog.stop()
    root.opened = false
  }

  Timer {
    id: watchdog
    interval: 10000
    onTriggered: {
      root.hide()
      Quickshell.execDetached(["hyprctl", "eval", "__adam_altswitch_cancel()"])
    }
  }

  IpcHandler {
    target: "adam-altswitch"

    function show(payloadJson: string): string {
      root.show(payloadJson)
      return "ok"
    }

    function select(index: int): string {
      root.select(index)
      return "ok"
    }

    function hide(): string {
      root.hide()
      return "ok"
    }

    function state(): string {
      return root.opened ? "open" : "closed"
    }
  }

  PanelWindow {
    id: panel

    screen: root.mainScreen
    visible: root.opened
    anchors { top: true; bottom: true; left: true; right: true }
    color: "transparent"
    WlrLayershell.namespace: "adam-altswitch"
    WlrLayershell.layer: WlrLayer.Overlay
    WlrLayershell.keyboardFocus: WlrKeyboardFocus.None
    exclusionMode: ExclusionMode.Ignore

    Rectangle {
      anchors.fill: parent
      color: Color.menu.scrim
    }

    BorderSurface {
      id: card

      width: root.cardWidth
      height: Math.min(
        root.maxCardHeight,
        root.headerHeight + root.footerHeight + root.windows.length * root.rowHeight
          + card.contentTopInset + card.contentBottomInset
      )
      anchors.centerIn: parent
      radius: Style.cornerRadius
      color: Color.menu.background
      borderSpec: Border.surfaceSpec("menu", "border", Color.menu.border, Math.max(1, Style.space(2)))
      padding: Style.spacing.panelPadding

      ColumnLayout {
        anchors.fill: parent
        anchors.topMargin: card.contentTopInset
        anchors.bottomMargin: card.contentBottomInset
        anchors.leftMargin: card.contentLeftInset
        anchors.rightMargin: card.contentRightInset
        spacing: 0

        RowLayout {
          Layout.fillWidth: true
          Layout.preferredHeight: root.headerHeight
          Layout.leftMargin: Style.spacing.controlPaddingX
          Layout.rightMargin: Style.spacing.controlPaddingX

          Text {
            text: "Switch window"
            color: Color.menu.text
            font.family: Style.font.menuFamily
            font.pixelSize: Style.font.body
            font.weight: Font.DemiBold
          }

          Item { Layout.fillWidth: true }

          Text {
            text: root.windows.length + (root.windows.length === 1 ? " WINDOW" : " WINDOWS")
            color: Color.muted
            font.family: Style.font.menuFamily
            font.pixelSize: Style.font.caption
            font.letterSpacing: 0.8
          }
        }

        Rectangle {
          Layout.fillWidth: true
          Layout.preferredHeight: Style.spacing.hairline
          color: Util.alpha(Color.menu.text, 0.12)
        }

        ListView {
          id: list

          Layout.fillWidth: true
          Layout.fillHeight: true
          clip: true
          interactive: false
          model: root.windows
          currentIndex: root.selectedIndex
          highlightMoveDuration: 0
          preferredHighlightBegin: 0
          preferredHighlightEnd: height
          highlightRangeMode: ListView.ApplyRange

          delegate: Rectangle {
            id: row

            required property int index
            required property var modelData

            width: list.width
            height: root.rowHeight
            radius: Style.cornerRadius
            color: index === root.selectedIndex ? Color.menu.selectedBackground : "transparent"

            Rectangle {
              visible: row.index === root.selectedIndex
              width: Style.space(3)
              height: parent.height - Style.space(20)
              radius: width / 2
              color: Color.accent
              anchors.left: parent.left
              anchors.verticalCenter: parent.verticalCenter
            }

            RowLayout {
              anchors.fill: parent
              anchors.leftMargin: Style.spacing.controlPaddingX + Style.space(8)
              anchors.rightMargin: Style.spacing.controlPaddingX
              spacing: Style.spacing.md

              Rectangle {
                Layout.preferredWidth: Style.space(40)
                Layout.preferredHeight: Style.space(40)
                radius: Style.cornerRadius
                color: Util.alpha(Color.menu.text, row.index === root.selectedIndex ? 0.12 : 0.07)

                Image {
                  id: appIcon
                  anchors.centerIn: parent
                  width: Style.space(28)
                  height: Style.space(28)
                  sourceSize.width: width * Screen.devicePixelRatio
                  sourceSize.height: height * Screen.devicePixelRatio
                  fillMode: Image.PreserveAspectFit
                  source: row.modelData.icon || ""
                  asynchronous: true
                  visible: source.toString().length > 0 && status !== Image.Error
                }

                Text {
                  anchors.centerIn: parent
                  visible: !appIcon.visible
                  text: root.initials(row.modelData.appClass)
                  color: row.index === root.selectedIndex ? Color.menu.selectedText : Color.menu.text
                  font.family: Style.font.menuFamily
                  font.pixelSize: Style.font.caption
                  font.weight: Font.DemiBold
                }
              }

              ColumnLayout {
                Layout.fillWidth: true
                spacing: Style.space(3)

                Text {
                  Layout.fillWidth: true
                  elide: Text.ElideRight
                  text: row.modelData.title
                  color: row.index === root.selectedIndex ? Color.menu.selectedText : Color.menu.text
                  font.family: Style.font.menuFamily
                  font.pixelSize: Style.font.body
                  font.weight: row.index === root.selectedIndex ? Font.DemiBold : Font.Normal
                }

                Text {
                  Layout.fillWidth: true
                  elide: Text.ElideRight
                  text: row.modelData.appClass
                  color: Color.muted
                  font.family: Style.font.menuFamily
                  font.pixelSize: Style.font.caption
                }
              }

              Rectangle {
                Layout.preferredWidth: workspaceLabel.implicitWidth + Style.space(16)
                Layout.preferredHeight: Style.space(26)
                radius: height / 2
                color: Util.alpha(Color.menu.text, 0.08)

                Text {
                  id: workspaceLabel
                  anchors.centerIn: parent
                  text: "WS " + row.modelData.workspace
                  color: row.index === root.selectedIndex ? Color.menu.selectedText : Color.muted
                  font.family: Style.font.menuFamily
                  font.pixelSize: Style.font.caption
                  font.weight: Font.DemiBold
                }
              }
            }
          }
        }

        Rectangle {
          Layout.fillWidth: true
          Layout.preferredHeight: Style.spacing.hairline
          color: Util.alpha(Color.menu.text, 0.12)
        }

        RowLayout {
          Layout.fillWidth: true
          Layout.preferredHeight: root.footerHeight
          Layout.leftMargin: Style.spacing.controlPaddingX
          Layout.rightMargin: Style.spacing.controlPaddingX

          Text {
            text: "TAB  NEXT    SHIFT+TAB  PREVIOUS"
            color: Color.muted
            font.family: Style.font.menuFamily
            font.pixelSize: Style.font.caption
          }

          Item { Layout.fillWidth: true }

          Text {
            text: "RELEASE ALT TO OPEN"
            color: Color.muted
            font.family: Style.font.menuFamily
            font.pixelSize: Style.font.caption
          }
        }
      }
    }
  }

  Component.onCompleted: if (root.appLibrary) root.appLibrary.refreshIcons()
}
