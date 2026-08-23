import QtQuick
import Quickshell
import Quickshell.Io
import qs.Commons
import qs.Ui

BarWidget {
  id: root
  moduleName: "adam.codex-usage"

  readonly property string scriptPath: String(Qt.resolvedUrl("usage.py")).replace(/^file:\/\//, "")
  property var usage: ({ available: false, buckets: [] })
  property string errorMessage: ""
  property bool loading: true
  property bool opened: false
  property double nowMs: Date.now()

  readonly property var headline: usage.headline || null
  readonly property int remaining: headline ? Number(headline.remaining) : -1
  readonly property string pace: headline ? paceIndicator(headline) : ""

  function open() { opened = true }
  function close() { opened = false }
  function toggle() { opened = !opened }
  function refresh() {
    if (!usageProcess.running) {
      loading = true
      usageProcess.running = true
    }
  }

  function duration(unixSeconds) {
    var seconds = Math.max(0, Number(unixSeconds) - nowMs / 1000)
    if (seconds === 0) return "now"
    var minutes = Math.floor(seconds / 60)
    var hours = Math.floor(minutes / 60)
    var days = Math.floor(hours / 24)
    if (days > 0) return days + "d " + (hours % 24) + "h"
    if (hours > 0) return hours + "h " + (minutes % 60) + "m"
    return Math.max(1, minutes) + "m"
  }

  function daysRemaining(unixSeconds) {
    var days = Math.max(0, Number(unixSeconds) - nowMs / 1000) / 86400
    return days.toFixed(1) + "d"
  }

  function paceIndicator(window) {
    var durationSeconds = Number(window.duration_minutes) * 60
    var secondsRemaining = Number(window.resets_at) - nowMs / 1000
    if (durationSeconds <= 0 || Number(window.resets_at) <= 0) return ""
    var timeRemaining = Math.max(0, Math.min(100, secondsRemaining / durationSeconds * 100))
    var difference = Math.round(Number(window.remaining) - timeRemaining)
    if (difference === 0) return "0◇"
    return Math.abs(difference) + (difference > 0 ? "△" : "▽")
  }

  function date(unixSeconds) {
    return new Date(Number(unixSeconds) * 1000).toLocaleDateString(Qt.locale(), "MMMM d")
  }

  function planLabel() {
    return usage.plan ? "ChatGPT " + usage.plan : "ChatGPT"
  }

  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  Component.onCompleted: Qt.callLater(refresh)
  onOpenedChanged: if (opened) nowMs = Date.now()

  Process {
    id: usageProcess
    command: ["/usr/bin/env", "python3", root.scriptPath]

    stdout: StdioCollector {
      waitForEnd: true
      onStreamFinished: {
        try {
          var next = JSON.parse(String(text || "{}"))
          if (next.available) {
            root.usage = next
            root.nowMs = Date.now()
            root.errorMessage = ""
          } else {
            root.errorMessage = String(next.error || "Usage unavailable")
          }
        } catch (_error) {
          root.errorMessage = "Invalid usage response"
        }
        root.loading = false
      }
    }
  }

  Timer {
    interval: 300000
    running: true
    repeat: true
    onTriggered: root.refresh()
  }

  Timer {
    interval: 30000
    running: root.opened
    repeat: true
    onTriggered: root.nowMs = Date.now()
  }

  WidgetButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: root.remaining >= 0
      ? "GPT " + root.remaining + "%"
        + (root.headline && Number(root.headline.resets_at) > 0 ? " " + root.daysRemaining(root.headline.resets_at) : "")
        + (root.pace ? " " + root.pace : "")
      : "GPT --"
    active: root.errorMessage !== "" || (root.remaining >= 0 && root.remaining <= 20)
    tooltipText: root.errorMessage !== ""
      ? root.errorMessage
      : (root.remaining >= 0 ? root.planLabel() + " · " + root.remaining + "% left" : "Codex usage")
    horizontalMargin: 8.5

    onPressed: function(buttonCode) {
      if (buttonCode === Qt.RightButton) root.refresh()
      else root.toggle()
    }
  }

  PopupCard {
    id: popup
    anchorItem: button
    bar: root.bar
    owner: root
    open: root.opened
    triggerMode: "click"
    contentWidth: popup.fittedContentWidth(Style.space(330))
    contentHeight: popup.fittedContentHeight(content.implicitHeight)

    Column {
      id: content
      anchors.fill: parent
      spacing: Style.space(10)

      Row {
        width: parent.width

        Text {
          text: root.planLabel()
          color: root.bar.foreground
          font.family: root.bar.fontFamily
          font.pixelSize: Style.font.subtitle
          font.bold: true
        }

        Text {
          width: parent.width - x
          text: usageProcess.running ? "Refreshing" : "Right-click to refresh"
          color: Qt.darker(root.bar.foreground, 1.45)
          font.family: root.bar.fontFamily
          font.pixelSize: Style.font.caption
          horizontalAlignment: Text.AlignRight
          anchors.verticalCenter: parent.verticalCenter
        }
      }

      Text {
        visible: root.errorMessage !== ""
        width: parent.width
        text: root.errorMessage + (root.usage.available ? " · showing previous data" : "")
        textFormat: Text.PlainText
        color: Color.urgent
        font.family: root.bar.fontFamily
        font.pixelSize: Style.font.caption
        wrapMode: Text.WordWrap
      }

      Repeater {
        model: root.usage.buckets || []

        Column {
          required property var modelData
          width: content.width
          spacing: Style.space(7)

          PanelSeparator {
            width: parent.width
            foreground: root.bar.foreground
          }

          Text {
            text: modelData.name
            textFormat: Text.PlainText
            color: root.bar.foreground
            font.family: root.bar.fontFamily
            font.pixelSize: Style.font.caption
            font.bold: true
          }

          Repeater {
            model: modelData.windows || []

            Column {
              required property var modelData
              width: content.width
              spacing: Style.space(4)

              Row {
                width: parent.width

                Text {
                  text: modelData.label
                  color: root.bar.foreground
                  font.family: root.bar.fontFamily
                  font.pixelSize: Style.font.bodySmall
                }

                Text {
                  width: parent.width - x
                  text: modelData.remaining + "% left"
                    + (Number(modelData.resets_at) > 0 ? " · " + root.daysRemaining(modelData.resets_at) : "")
                  color: modelData.remaining <= 20 ? Color.urgent : root.bar.foreground
                  font.family: root.bar.fontFamily
                  font.pixelSize: Style.font.bodySmall
                  font.bold: true
                  horizontalAlignment: Text.AlignRight
                }
              }

              Rectangle {
                width: parent.width
                height: Style.space(4)
                radius: height / 2
                color: Qt.rgba(root.bar.foreground.r, root.bar.foreground.g, root.bar.foreground.b, 0.12)

                Rectangle {
                  width: parent.width * Number(modelData.remaining) / 100
                  height: parent.height
                  radius: parent.radius
                  color: modelData.remaining <= 20 ? Color.urgent : Color.accent
                }
              }

              Text {
                visible: Number(modelData.resets_at) > 0
                text: "Resets in " + root.duration(modelData.resets_at)
                color: Qt.darker(root.bar.foreground, 1.45)
                font.family: root.bar.fontFamily
                font.pixelSize: Style.font.caption
              }
            }
          }

          Text {
            readonly property var credits: modelData.credits || ({})
            visible: credits.unlimited || credits.has_credits
            text: credits.unlimited ? "Credits: unlimited" : "Credits: " + (credits.balance || "available")
            textFormat: Text.PlainText
            color: Qt.darker(root.bar.foreground, 1.25)
            font.family: root.bar.fontFamily
            font.pixelSize: Style.font.caption
          }
        }
      }

      Text {
        visible: Number(root.usage.reset_credits || 0) > 0
        text: "Reset credits: " + root.usage.reset_credits
          + (Number(root.usage.reset_credits_expires_at) > 0
            ? " · expires " + root.date(root.usage.reset_credits_expires_at)
            : "")
        color: Qt.darker(root.bar.foreground, 1.25)
        font.family: root.bar.fontFamily
        font.pixelSize: Style.font.caption
      }
    }
  }
}
