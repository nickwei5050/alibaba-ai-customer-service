/**
 * Optional: serve /llms.txt dynamically from Next.js App Router instead of
 * (or in addition to) the static public/llms.txt. Delete one of the two so
 * you don't ship both. This version reads the static file at build/runtime.
 *
 * If you prefer fully static, just keep public/llms.txt and delete this route.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";

export const dynamic = "force-static";

export function GET() {
  const body = readFileSync(join(process.cwd(), "public", "llms.txt"), "utf8");
  return new Response(body, {
    headers: { "content-type": "text/plain; charset=utf-8" },
  });
}
