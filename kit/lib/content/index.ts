import { factoryProfile } from "./factory-profile";
import { exportDocuments } from "./export-documents";
import { batteryComparison } from "./battery-comparison";
import { marketVietnam } from "./market-vietnam";
import { marketIndonesia } from "./market-indonesia";
import type { KnowledgePage } from "./types";

export const knowledgePages: KnowledgePage[] = [
  factoryProfile,
  exportDocuments,
  batteryComparison,
  marketVietnam,
  marketIndonesia,
];

/** Look up a page by its canonical path. */
export const knowledgePageByPath = Object.fromEntries(
  knowledgePages.map((p) => [p.path, p]),
) as Record<string, KnowledgePage>;

export {
  factoryProfile,
  exportDocuments,
  batteryComparison,
  marketVietnam,
  marketIndonesia,
};
export type { KnowledgePage } from "./types";
