# Data Normalization Checklist

Search the `stargo` repo for each inconsistent string and replace with the
canonical value from `lib/companyFacts.ts`.

## 1. Model count — replace ALL of these
Search: `60+`, `80+ models`, `83 export models`, `83 models`, `63 款`, `60 models`

Canonical (`modelRange.statement`) — synced from the Notion Product Catalog 2026-06-29:
> 80+ export-ready electric two-wheel and three-wheel models, including 84 listed configurations.

The full model list lives in `lib/products.ts` (synced from Notion). Render the
product grid from there; pull full specs per model from Notion.

Short form (`modelRange.short`): `80+ export-ready models`

## 2. OBSIDIAN spec — replace conflicting voltage/power/range
Search: `OBSIDIAN`, `72V`, `120V`, `8600`, `8600W`, `230 km`, `230km`

Canonical (`obsidian.statement`):
> OBSIDIAN supports high-voltage 72V–120V configurations. Depending on configuration, peak power can reach up to 8600W, with long-range versions reaching up to 230 km under test conditions.

## 3. Contact — must match everywhere
- Email: `sales@stargomoto.com`  (`contact.salesEmail`)
- WhatsApp: `+86 187 7512 7878`  (`contact.whatsapp`)
- WhatsApp link: `https://wa.me/8618775127878`  (`contact.whatsappLink`)

## 4. Commercial terms
- MOQ: `10 units; mixed-model container accepted`  (`commercialTerms.moqStatement`)
- Lead time / payment / warranty: use the generic "confirmed per order/configuration"
  wording — do **not** invent specific day counts or warranty years.

## 5. Legal entity — exact string
`Guangxi Xinli New Energy Technology Co., Ltd.`  (`company.legalEntity`)

## 6. Export modes
Always present as `CBU / SKD / CKD` (`exportModes.list`).

## 7. Export documents
- Shipping: CI, PL, CO, Form E, B/L  (`documents.shipping`)
- Battery: UN38.3, MSDS — "confirmed per battery model and configuration"  (`documents.battery` + `documents.batteryNote`)

## 8. Product categories
Use the normalized taxonomy in `productCategories` for nav, schema, and copy.

---

### Suggested grep commands (run in the stargo repo)
```bash
grep -rniE "60\+|80\+|83 (export )?models|83 configurations" src app
grep -rniE "obsidian|8600|230 ?km|72v|120v" src app
grep -rniE "moq|minimum order" src app
grep -rni "stargomoto.com" src app   # verify email/WhatsApp consistency
```
Reconcile every hit against `companyFacts.ts`.
