import JSZip from "jszip";
import {
  buildMetadataJson,
  buildPubliccodeYaml,
  buildReadmeMd,
  buildDebugJson,
  downloadContextZip,
} from "@/lib/contextExport";
import type { ResultsData } from "@/types/main";

describe("buildMetadataJson", () => {
  it("wraps the SDG numbers under a UN SDGs key", () => {
    expect(JSON.parse(buildMetadataJson([1, 3, 7]))).toEqual({
      "UN SDGs": [1, 3, 7],
    });
  });

  it("handles an empty list", () => {
    expect(JSON.parse(buildMetadataJson([]))).toEqual({ "UN SDGs": [] });
  });
});

describe("buildPubliccodeYaml", () => {
  it("renders the same list as YAML", () => {
    expect(buildPubliccodeYaml([1, 3, 7])).toBe(
      "UN SDGs:\n  - 1\n  - 3\n  - 7\n",
    );
  });

  it("handles an empty list", () => {
    expect(buildPubliccodeYaml([])).toBe("UN SDGs: []\n");
  });
});

describe("buildReadmeMd", () => {
  it("opens with the attestation sentence", () => {
    const readme = buildReadmeMd([1]);
    expect(readme).toContain(
      'This project is "highly relevant" at addressing the following United Nation (UN) Sustainable Development Goals (SDGs):',
    );
  });

  it("includes a heading and description for every selected SDG", () => {
    const readme = buildReadmeMd([1, 13]);
    expect(readme).toContain("## SDG 1: No Poverty");
    expect(readme).toContain("Goal 1 calls for an end to poverty");
    expect(readme).toContain("## SDG 13: Climate Action");
    expect(readme).toContain("Climate change presents the single biggest threat");
  });

  it("excludes SDGs that were not selected", () => {
    const readme = buildReadmeMd([1]);
    expect(readme).not.toContain("SDG 13:");
  });
});

describe("buildDebugJson", () => {
  const results: ResultsData = {
    projectName: "example-repo",
    projectUrl: "https://github.com/example/repo",
    predictions: {
      a: { prediction: 0.9, sdg: "SDG 1: No Poverty" },
      b: { prediction: 0.5, sdg: "SDG 3: Good Health" },
      c: { prediction: 0.2, sdg: "SDG 6: Clean Water" },
    },
  };

  it("includes repository info, predictions, and confidence-band summary", () => {
    const debug = JSON.parse(buildDebugJson(results));

    expect(debug.sdg_analysis.repositoryName).toBe("example-repo");
    expect(debug.sdg_analysis.repositoryUrl).toBe(
      "https://github.com/example/repo",
    );
    expect(debug.sdg_analysis.predictions).toEqual(results.predictions);
    expect(debug.sdg_analysis.summary).toEqual({
      total_sdgs: 3,
      high_confidence: 1,
      medium_confidence: 1,
      low_confidence: 1,
    });
    expect(typeof debug.sdg_analysis.analyzed_at).toBe("string");
  });
});

function blobToArrayBuffer(blob: Blob): Promise<ArrayBuffer> {
  // jsdom's Blob doesn't implement arrayBuffer(); FileReader is the portable path.
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as ArrayBuffer);
    reader.onerror = () => reject(reader.error);
    reader.readAsArrayBuffer(blob);
  });
}

describe("downloadContextZip", () => {
  const results: ResultsData = {
    projectName: "example-repo",
    projectUrl: "https://github.com/example/repo",
    predictions: {
      a: { prediction: 0.9, sdg: "SDG 1: No Poverty" },
      b: { prediction: 0.5, sdg: "SDG 3: Good Health" },
    },
  };

  let clickSpy: jest.SpyInstance;

  beforeEach(() => {
    URL.createObjectURL = jest.fn(() => "blob:mock-url");
    URL.revokeObjectURL = jest.fn();
    clickSpy = jest
      .spyOn(HTMLAnchorElement.prototype, "click")
      .mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it("bundles all four files under a context/ folder and triggers a single download", async () => {
    await downloadContextZip(results);

    expect(clickSpy).toHaveBeenCalledTimes(1);
    expect(URL.createObjectURL).toHaveBeenCalledTimes(1);

    const blob = (URL.createObjectURL as jest.Mock).mock.calls[0][0] as Blob;
    const zip = await JSZip.loadAsync(await blobToArrayBuffer(blob));

    const metadata = JSON.parse(
      await zip.file("context/metadata.json")!.async("string"),
    );
    expect(metadata).toEqual({ "UN SDGs": [1, 3] });

    const publiccode = await zip.file("context/publiccode.yaml")!.async("string");
    expect(publiccode).toBe("UN SDGs:\n  - 1\n  - 3\n");

    const readme = await zip.file("context/README.md")!.async("string");
    expect(readme).toContain('This project is "highly relevant"');
    expect(readme).toContain("SDG 1: No Poverty");
    expect(readme).toContain("SDG 3: Good Health and Well-being");

    const debug = JSON.parse(
      await zip.file("context/debug.json")!.async("string"),
    );
    expect(debug.sdg_analysis.repositoryName).toBe("example-repo");
  });
});
