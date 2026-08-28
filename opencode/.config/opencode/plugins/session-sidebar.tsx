/** @jsxImportSource @opentui/solid */

import type { Session } from "@opencode-ai/sdk/v2"
import type { TuiPlugin, TuiPluginApi, TuiPluginModule } from "@opencode-ai/plugin/tui"
import { createMemo, createSignal, For, onCleanup, Show } from "solid-js"

const SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

function isBusy(api: TuiPluginApi, sessionID: string) {
  const status = api.state.session.status(sessionID)
  return status?.type === "busy" || status?.type === "retry"
}

function startOfToday() {
  const start = new Date()
  start.setHours(0, 0, 0, 0)
  return start.getTime()
}

function SessionSidebar(props: {
  api: TuiPluginApi
  session_id: string
  sessions: () => Session[]
}) {
  const [open, setOpen] = createSignal(true)
  const [todayStart, setTodayStart] = createSignal(startOfToday())
  const [spinnerFrame, setSpinnerFrame] = createSignal(0)
  const dayTimer = setInterval(() => setTodayStart(startOfToday()), 60_000)
  const spinnerTimer = setInterval(() => setSpinnerFrame((frame) => (frame + 1) % SPINNER_FRAMES.length), 80)
  onCleanup(() => {
    clearInterval(dayTimer)
    clearInterval(spinnerTimer)
  })
  const theme = () => props.api.theme.current
  const sessions = createMemo(() => {
    const selected = props.api.state.session.get(props.session_id)
    const project = selected?.projectID
    const listed = props.sessions()
    const all =
      selected && !listed.some((session) => session.id === selected.id) ? [...listed, selected] : listed
    return all
      .filter((session) => !session.parentID && (!project || session.projectID === project))
      .toSorted((a, b) => b.time.updated - a.time.updated)
  })
  const active = createMemo(() =>
    sessions().filter((session) => session.id === props.session_id || isBusy(props.api, session.id)),
  )
  const today = createMemo(() => {
    const activeIDs = new Set(active().map((session) => session.id))
    return sessions().filter((session) => session.time.updated >= todayStart() && !activeIDs.has(session.id))
  })

  const renderRows = (list: () => Session[], showStatus: boolean) => (
    <For each={list()}>
      {(session) => {
        const selected = () => session.id === props.session_id
        const busy = () => isBusy(props.api, session.id)
        return (
          <box
            flexDirection="row"
            gap={1}
            paddingLeft={1}
            backgroundColor={selected() ? theme().backgroundElement : undefined}
            onMouseDown={() => props.api.route.navigate("session", { sessionID: session.id })}
          >
            <Show when={showStatus}>
              <text fg={theme().textMuted}>{busy() ? SPINNER_FRAMES[spinnerFrame()] : "•"} </text>
            </Show>
            <text fg={selected() ? theme().primary : theme().text}>
              <Show when={selected()} fallback={session.title}>
                <b>{session.title}</b>
              </Show>
            </text>
          </box>
        )
      }}
    </For>
  )

  const renderGroup = (title: string, list: () => Session[], showStatus: boolean) => (
    <box>
      <text fg={theme().text}>
        <b>{title}</b> <span style={{ fg: theme().textMuted }}>({list().length})</span>
      </text>
      {renderRows(list, showStatus)}
    </box>
  )

  return (
    <box>
      <box flexDirection="row" gap={1} onMouseDown={() => setOpen((value) => !value)}>
        <text fg={theme().text}>{open() ? "▼" : "▶"}</text>
        <text fg={theme().text}>
          <b>Sessions</b> <span style={{ fg: theme().textMuted }}>({active().length + today().length})</span>
        </text>
      </box>
      <Show when={open()}>
        <box gap={1} paddingTop={1}>
          {renderGroup("Active", active, true)}
          {renderGroup("Today", today, false)}
        </box>
      </Show>
    </box>
  )
}

const tui: TuiPlugin = async (api) => {
  const result = await api.client.session.list({ roots: true, limit: 100 })
  const [sessions, setSessions] = createSignal<Session[]>(result.data ?? [])

  const upsert = (session: Session) => {
    setSessions((current) => {
      const index = current.findIndex((item) => item.id === session.id)
      if (index === -1) return [...current, session]
      return current.toSpliced(index, 1, session)
    })
  }

  api.event.on("session.created", (event) => upsert(event.properties.info))
  api.event.on("session.updated", (event) => upsert(event.properties.info))
  api.event.on("session.deleted", (event) => {
    setSessions((current) => current.filter((session) => session.id !== event.properties.info.id))
  })

  api.slots.register({
    order: 50,
    slots: {
      sidebar_content(_ctx, props) {
        return <SessionSidebar api={api} session_id={props.session_id} sessions={sessions} />
      },
    },
  })
}

const plugin: TuiPluginModule & { id: string } = {
  id: "adam.session-sidebar",
  tui,
}

export default plugin
