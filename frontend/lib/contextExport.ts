import JSZip from "jszip";
import type { ResultsData, SDGValue } from "@/types/main";
import { getSdgDescription, getSdgName, getSelectedSdgNumbers } from "@/lib/sdgReference";

/*
Context folder export
- Builds the four files that ship in the downloadable "context" folder:
  metadata.json (machine-readable SDG list), publiccode.yaml (same list, YAML),
  README.md (human-readable attestation + descriptions), debug.json (full analysis detail).
- Bundled into a single context.zip client-side since browsers can't write a folder directly.
*/

const getScore = (v: number | SDGValue | null | undefined): number =>
  typeof v === "number" ? Number(v) : Number((v as SDGValue)?.prediction ?? 0);

export function buildMetadataJson(sdgNumbers: number[]): string {
  return JSON.stringify({ "UN SDGs": sdgNumbers }, null, 2);
}

export function buildPubliccodeYaml(sdgNumbers: number[]): string {
  if (sdgNumbers.length === 0) {
    return "UN SDGs: []\n";
  }
  const items = sdgNumbers.map((n) => `  - ${n}`).join("\n");
  return `UN SDGs:\n${items}\n`;
}

export function buildReadmeMd(sdgNumbers: number[]): string {
  const lines = [
    "# UN Sustainable Development Goals",
    "",
    'This project is "highly relevant" at addressing the following United Nation (UN) Sustainable Development Goals (SDGs):',
    "",
  ];

  for (const number of sdgNumbers) {
    lines.push(`## SDG ${number}: ${getSdgName(number)}`, "", getSdgDescription(number), "");
  }

  return lines.join("\n");
}

export function buildDebugJson(results: ResultsData): string {
  const predictions = (results.predictions ?? {}) as Record<
    string,
    number | SDGValue
  >;

  const unsdgData = {
    sdg_analysis: {
      analyzed_at: new Date().toISOString(),
      repositoryName: results.projectName,
      repositoryUrl: results.projectUrl,
      predictions,
      summary: {
        total_sdgs: Object.keys(predictions).length,
        high_confidence: Object.values(predictions).filter(
          (score) => getScore(score) >= 0.7,
        ).length,
        medium_confidence: Object.values(predictions).filter(
          (score) => getScore(score) >= 0.4 && getScore(score) < 0.7,
        ).length,
        low_confidence: Object.values(predictions).filter(
          (score) => getScore(score) < 0.4,
        ).length,
      },
    },
  };

  return JSON.stringify(unsdgData, null, 2);
}

function triggerBlobDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export async function downloadContextZip(results: ResultsData): Promise<void> {
  const sdgNumbers = getSelectedSdgNumbers(
    results.predictions as
      | SDGValue[]
      | Record<string, SDGValue>
      | Record<string, number>
      | undefined,
  );

  const zip = new JSZip();
  const folder = zip.folder("context");
  if (!folder) {
    throw new Error("Failed to create context folder in zip archive");
  }

  folder.file("metadata.json", buildMetadataJson(sdgNumbers));
  folder.file("publiccode.yaml", buildPubliccodeYaml(sdgNumbers));
  folder.file("README.md", buildReadmeMd(sdgNumbers));
  folder.file("debug.json", buildDebugJson(results));

  const blob = await zip.generateAsync({ type: "blob" });
  triggerBlobDownload(blob, "context.zip");
}
