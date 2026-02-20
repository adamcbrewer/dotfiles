import type { Plugin } from "@opencode-ai/plugin";

const HOME = process.env.HOME ?? "";

async function playRandomFile($: any, dir: string, ext: string): Promise<void> {
  try {
    const result =
      await $`find ${dir} -maxdepth 1 -type f -name "*.${ext}"`.text();
    const files = result.trim().split("\n").filter(Boolean);
    if (files.length === 0) return;
    const file = files[Math.floor(Math.random() * files.length)];
    await $`ffplay -v 0 -nodisp -autoexit ${file}`.quiet();
  } catch {}
}

async function playFile($: any, file: string): Promise<void> {
  try {
    await $`ffplay -v 0 -nodisp -autoexit ${file}`.quiet();
  } catch {}
}

async function notify($: any, title: string, body: string): Promise<void> {
  try {
    await $`notify-send ${title} ${body} --icon=dialog-information -t 10000`.quiet();
  } catch {}
}

async function isSubagent(client: any, sessionID: string): Promise<boolean> {
  try {
    const session = await client.session.get({ path: { id: sessionID } });
    return !!session.data?.parentID;
  } catch {
    return false;
  }
}

export const NotificationPlugin: Plugin = async ({ $, directory, client }) => {
  const project = directory.split("/").pop() ?? "unknown";

  return {
    event: async ({ event }) => {
      if (event.type === "session.compacted") {
        await playFile($, `${HOME}/Audio/agents/session-start/smb3_pipe.wav`);
      }

      if (event.type === "session.created") {
        if (event.properties.info.parentID) {
          // subagent session created
          await playFile($, `${HOME}/Audio/agents/session-start/smb3_vine.wav`);
        } else {
          // main session created
          await playFile(
            $,
            `${HOME}/Audio/agents/session-start/smb3_powerup.wav`,
          );
        }
      }

      if (event.type === "session.idle") {
        const sub = await isSubagent(client, event.properties.sessionID);
        if (sub) {
          await playFile($, `${HOME}/Audio/agents/stop/smb3_pipe.wav`);
        } else {
          // main session finished
          await Promise.all([
            playFile($, `${HOME}/Audio/agents/stop/smb3_fortress_clear.wav`),
            notify($, `OpenCode · ${project}`, "✅ Done!"),
          ]);
        }
      }

      if (event.type === "session.error") {
        await Promise.all([
          playRandomFile($, `${HOME}/Audio/agents/notification`, "*"),
          notify($, `OpenCode · ${project}`, "💥 Session error!"),
        ]);
      }

      if (event.type === "permission.asked") {
        await Promise.all([
          playRandomFile($, `${HOME}/Audio/agents/notification`, "*"),
          notify($, `OpenCode · ${project}`, "🔐 Needs your attention"),
        ]);
      }
    },
  };
};
