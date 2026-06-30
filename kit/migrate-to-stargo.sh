#!/usr/bin/env bash
#
# migrate-to-stargo.sh
# Relocate the STARGO upgrade kit into the official website (Next.js) repo.
#
# HOW TO USE (in the nickwei5050/stargo repo):
#   1. Get the `kit/` folder into the stargo repo root. Either:
#        a) Download this branch as a ZIP from GitHub (PR #2) and copy its
#           `kit/` folder into the stargo repo root, OR
#        b) In a Claude Code session connected to stargo, ask Claude to copy
#           the kit from PR #2 of alibaba-ai-customer-service.
#   2. From the stargo repo root, run:  bash kit/migrate-to-stargo.sh
#   3. Review import paths (the `@/` alias), then delete the leftover `kit/`.
#
set -euo pipefail

ROOT="$(pwd)"
KIT="$ROOT/kit"

if [ ! -d "$KIT" ]; then
  echo "ERROR: kit/ not found in $ROOT. Copy the kit/ folder here first."
  exit 1
fi

# Prefer src/ layout if present, else root-level (app router at repo root).
if [ -d "$ROOT/src" ]; then BASE="src"; else BASE="."; fi
echo "Using base directory: $BASE"

mkdir -p "$BASE/lib" "$BASE/components" public

echo "→ Copying lib/ (companyFacts, schema, seo, products, content, hooks)"
cp -R "$KIT/lib/." "$BASE/lib/"

echo "→ Copying components/ (KnowledgePageView reference renderer)"
cp -R "$KIT/components/." "$BASE/components/"

echo "→ Copying public/llms.txt"
cp "$KIT/public/llms.txt" "public/llms.txt"

# Locate the app/ directory for the optional /llms.txt route.
APP=""
if [ -d "$BASE/app" ]; then APP="$BASE/app"; elif [ -d "app" ]; then APP="app"; fi
if [ -n "$APP" ]; then
  echo "→ Copying app/llms.txt/route.ts into $APP (optional)"
  mkdir -p "$APP/llms.txt"
  cp "$KIT/app/llms.txt/route.ts" "$APP/llms.txt/route.ts"
  echo "  NOTE: keep EITHER public/llms.txt OR app/llms.txt/route.ts — not both."
fi

cat <<'NEXT'

Migration copy complete. Next steps (manual):
  1. Check the "@/" path alias resolves to your base dir (tsconfig paths).
  2. Wire metadata: in each page.tsx add
       export const metadata = buildMetadata({ ... })   // from lib/seo
  3. Add JSON-LD from lib/schema (Organization+WebSite on home, Breadcrumb on
     inner pages, Product on product pages, FAQPage where FAQs show).
  4. Build the product grid from lib/products (productsBySeries / products).
  5. Create the 5 GEO pages from lib/content/* at each page's `path`.
  6. Replace inconsistent claims using kit/NORMALIZATION.md (model count = 84).
  7. Run: npm run lint && npm run typecheck && npm run build
  8. Delete the leftover kit/ folder once everything is wired.
NEXT

echo "Done."
