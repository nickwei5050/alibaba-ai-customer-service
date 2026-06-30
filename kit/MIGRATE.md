# 迁移指南：把 kit 从错误仓库搬到官网 stargo 仓库

这些文件目前在 **错误的仓库** `nickwei5050/alibaba-ai-customer-service`(PR #2)。
官网真正的代码在 **`nickwei5050/stargo`**。下面是把它们搬过去的步骤。

> 我（当前会话）无法替你新开对话，也无法直接写进 stargo —— 那个仓库不在本会话
> 授权范围内。所以迁移必须在一个 **连了 stargo 的新会话** 里完成。

## 步骤

### 1. 在 Claude Code 网页端新开一个会话，仓库选 `nickwei5050/stargo`

### 2. 把下面这段提示词整段粘贴进去

```
You are working in the nickwei5050/stargo repo (the official www.stargomoto.com codebase).

I previously generated a "STARGO upgrade kit" by mistake in the WRONG repo
nickwei5050/alibaba-ai-customer-service, on branch
claude/stargo-seo-conversion-upgrade-7hd4d7 (PR #2), inside a top-level kit/ folder.

Goal: migrate that kit into THIS repo and wire it in, WITHOUT removing or weakening
any existing GSAP / animation / 3D / premium visual code.

Do this:
1. Bring the kit/ files into this repo. If you can access the alibaba repo via the
   GitHub tools, read the files from PR #2's branch; otherwise tell me to download
   the branch ZIP and drop the kit/ folder in, then run kit/migrate-to-stargo.sh.
2. Place files at standard Next.js paths: lib/ (companyFacts, schema, seo, products,
   content/, useReducedMotion), components/ (KnowledgePageView), public/llms.txt.
3. Normalize all model-count claims to "84 listed configurations" (see NORMALIZATION.md).
4. Wire SEO metadata (lib/seo), JSON-LD (lib/schema), the product grid (lib/products),
   and create the 5 GEO pages from lib/content/*.
5. Run lint, typecheck, build. Report what changed and anything needing my confirmation.
Keep the cinematic design intact; performance only via lazy-load / dynamic import /
image compression / mobile-lite.
```

### 3. 如果那个新会话连不到 alibaba 仓库读文件

就用 ZIP 方式把 `kit/` 拿过去：

1. 打开 PR 分支：`https://github.com/nickwei5050/alibaba-ai-customer-service/tree/claude/stargo-seo-conversion-upgrade-7hd4d7`
2. 「Code → Download ZIP」，解压后把里面的 `kit/` 整个文件夹复制到 stargo 仓库根目录。
3. 在 stargo 仓库根目录执行：`bash kit/migrate-to-stargo.sh`
4. 按脚本结尾提示接线，最后删掉 `kit/`。

## 文件落位对照表

| kit 里的文件 | stargo 里的目标位置 |
|---|---|
| `kit/lib/companyFacts.ts` | `src/lib/companyFacts.ts`（无 src/ 则 `lib/`） |
| `kit/lib/schema.ts` | `src/lib/schema.ts` |
| `kit/lib/seo.ts` | `src/lib/seo.ts` |
| `kit/lib/products.ts` | `src/lib/products.ts` |
| `kit/lib/useReducedMotion.ts` | `src/lib/useReducedMotion.ts` |
| `kit/lib/content/*` | `src/lib/content/*` |
| `kit/components/KnowledgePageView.tsx` | `src/components/KnowledgePageView.tsx` |
| `kit/public/llms.txt` | `public/llms.txt` |
| `kit/app/llms.txt/route.ts` | `app/llms.txt/route.ts`（与上面二选一） |

迁移脚本 `migrate-to-stargo.sh` 会自动做这张表的复制。
