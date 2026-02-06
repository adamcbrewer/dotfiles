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

async function notify($: any, title: string, body: string): Promise<void> {
  try {
    await $`notify-send ${title} ${body} --icon=dialog-information -t 10000`.quiet();
  } catch {}
}

export const NotificationPlugin: Plugin = async ({ $, directory }) => {
  const project = directory.split("/").pop() ?? "unknown";

  return {
    event: async ({ event }) => {
      if (event.type === "session.created") {
        await playRandomFile($, `${HOME}/Audio/claude/session-start`, "*");
      }

      if (event.type === "session.idle") {
        await Promise.all([
          playRandomFile($, `${HOME}/Audio/claude/stop`, "*"),
          notify($, `OpenCode · ${project}`, "✅ Done!"),
        ]);
      }

      if (event.type === "session.error") {
        await Promise.all([
          playRandomFile($, `${HOME}/Audio/claude/notification`, "*"),
          notify($, `OpenCode · ${project}`, "💥 Session error!"),
        ]);
      }

      if (event.type === "permission.asked") {
        await Promise.all([
          playRandomFile($, `${HOME}/Audio/claude/notification`, "*"),
          notify($, `OpenCode · ${project}`, "🔐 Needs your attention"),
        ]);
      }
    },
  };
};
