import { spawn, type ChildProcess } from "node:child_process";
import { readdir } from "node:fs/promises";
import { homedir } from "node:os";
import { join } from "node:path";
import { Plugin } from "@opencode/plugin";

const AUDIO = join(homedir(), "Audio/agents");

export default Plugin.define({
  id: "adam.notifications",
  setup(ctx) {
    const controller = new AbortController();
    const players = new Set<ChildProcess>();

    function play(file: string) {
      if (controller.signal.aborted) return;
      const player = spawn("ffplay", ["-v", "0", "-nodisp", "-autoexit", file], {
        stdio: "ignore",
      });
      players.add(player);
      player.once("error", () => players.delete(player));
      player.once("close", () => players.delete(player));
    }

    async function alert() {
      const directory = join(AUDIO, "notification");
      const entries = await readdir(directory, { withFileTypes: true });
      const files = entries.filter((entry) => entry.isFile());
      if (files.length) {
        play(join(directory, files[Math.floor(Math.random() * files.length)].name));
      }
    }

    const listening = (async () => {
      for await (const event of ctx.event.subscribe({ signal: controller.signal })) {
        if (event.location && event.location.directory !== ctx.location.directory) continue;
        try {
          switch (event.type) {
            case "session.created":
              play(join(
                AUDIO, "session-start",
                event.data.parentID ? "smb3_vine.wav" : "smb3_powerup.wav",
              ));
              break;
            case "session.compacted":
              play(join(AUDIO, "session-start/smb3_pipe.wav"));
              break;
            case "session.execution.succeeded": {
              const session = await ctx.session.get({ sessionID: event.data.sessionID });
              play(join(AUDIO, "stop", session.parentID ? "smb3_pipe.wav" : "smb3_1-up.wav"));
              break;
            }
            case "session.execution.failed":
            case "permission.asked":
              await alert();
              break;
          }
        } catch (error) {
          if (!controller.signal.aborted) console.warn("Notification sound failed:", error);
        }
      }
    })().catch((error) => {
      if (!controller.signal.aborted) console.warn("Notification event stream failed:", error);
    });

    return async () => {
      controller.abort();
      for (const player of players) player.kill();
      players.clear();
      await listening;
    };
  },
});
