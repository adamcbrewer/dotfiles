import { afterEach, expect, mock, test } from "bun:test";
import { EventEmitter } from "node:events";

const players: Array<EventEmitter & { kill: ReturnType<typeof mock> }> = [];
const spawn = mock(() => {
  const player = Object.assign(new EventEmitter(), { kill: mock(() => true) });
  players.push(player);
  return player;
});
const readdir = mock(async () => [
  { name: "alert.wav", isFile: () => true },
  { name: "directory", isFile: () => false },
]);
mock.module("node:child_process", () => ({ spawn }));
mock.module("node:fs/promises", () => ({ readdir }));
mock.module("node:os", () => ({ homedir: () => "/test-home" }));
mock.module("@opencode/plugin", () => ({ Plugin: { define: (plugin: unknown) => plugin } }));

const { default: plugin } = await import("../opencode/.config/opencode/plugins/notifications.ts");
const cleanups: Array<() => Promise<void>> = [];

afterEach(async () => {
  for (const cleanup of cleanups.splice(0)) await cleanup();
  players.length = 0;
  spawn.mockClear();
  readdir.mockClear();
});

async function run(
  events: object[],
  get: (input: { sessionID: string }) => Promise<{ parentID?: string }> = async () => ({}),
) {
  let signal!: AbortSignal;
  let finish!: () => void;
  const consumed = new Promise<void>((resolve) => { finish = resolve; });
  const cleanup = plugin.setup({
    location: { directory: "/project" },
    session: { get },
    event: {
      async *subscribe(options: { signal: AbortSignal }) {
        signal = options.signal;
        for (const event of events) yield event;
        finish();
        if (!signal.aborted) await new Promise<void>((resolve) => signal.addEventListener("abort", () => resolve(), { once: true }));
      },
    },
  } as Parameters<typeof plugin.setup>[0]);
  if (typeof cleanup !== "function") throw new Error("Missing plugin cleanup");
  cleanups.push(async () => { await cleanup(); });
  await consumed;
  return { cleanup, signal };
}

function event(type: string, data: object = {}, directory = "/project") {
  return { type, data, location: { directory } };
}

function files() {
  return spawn.mock.calls.map((call) => (call as unknown as [string, string[]])[1].at(-1));
}

test("plays distinct root, child, and compaction cues from v2 event data", async () => {
  await run([
    event("session.created"),
    event("session.created", { parentID: "root" }),
    event("session.compacted"),
  ]);
  expect(files()).toEqual([
    "/test-home/Audio/agents/session-start/smb3_powerup.wav",
    "/test-home/Audio/agents/session-start/smb3_vine.wav",
    "/test-home/Audio/agents/session-start/smb3_pipe.wav",
  ]);
});

test("completion uses the v2 session lookup and does not also play on legacy idle", async () => {
  const get = mock(async ({ sessionID }: { sessionID: string }) => ({ parentID: sessionID === "child" ? "root" : undefined }));
  await run([
    event("session.execution.succeeded", { sessionID: "root" }),
    event("session.idle", { sessionID: "root" }),
    event("session.execution.succeeded", { sessionID: "child" }),
  ], get);
  expect(get.mock.calls).toEqual([[{ sessionID: "root" }], [{ sessionID: "child" }]]);
  expect(files()).toEqual([
    "/test-home/Audio/agents/stop/smb3_1-up.wav",
    "/test-home/Audio/agents/stop/smb3_pipe.wav",
  ]);
});

test("errors and permission requests pick files, ignoring directories", async () => {
  await run([event("session.execution.failed"), event("permission.asked")]);
  expect(files()).toEqual(Array(2).fill("/test-home/Audio/agents/notification/alert.wav"));
});

test("events from another location and interruptions do not play success sounds", async () => {
  await run([event("session.created", {}, "/other"), event("session.execution.interrupted")]);
  expect(spawn).not.toHaveBeenCalled();
});

test("missing sound directory does not stop subsequent notifications", async () => {
  readdir.mockRejectedValueOnce(new Error("ENOENT"));
  const warn = mock(() => {});
  const original = console.warn;
  console.warn = warn;
  try {
    await run([event("permission.asked"), event("session.created")]);
    expect(warn).toHaveBeenCalledTimes(1);
    expect(files()).toEqual(["/test-home/Audio/agents/session-start/smb3_powerup.wav"]);
  } finally {
    console.warn = original;
  }
});

test("cleanup aborts subscription and kills only unfinished players", async () => {
  const { cleanup, signal } = await run([event("session.created"), event("session.compacted")]);
  players[0].emit("close", 0);
  await cleanup();
  expect(signal.aborted).toBe(true);
  expect(players[0].kill).not.toHaveBeenCalled();
  expect(players[1].kill).toHaveBeenCalledTimes(1);
});

test("missing ffplay is handled without an uncaught child-process error", async () => {
  await run([event("session.created")]);
  expect(() => players[0].emit("error", new Error("ENOENT"))).not.toThrow();
});
