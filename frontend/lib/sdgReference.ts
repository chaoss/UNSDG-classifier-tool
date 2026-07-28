import SDG from "@/components/sdg";
import type { SDGValue } from "@/types/main";

/*
SDG Reference
- Canonical SDG number -> description lookup (mirrors backend/sdg_constants.py's SDG_LABELS)
- parsePrediction/getSelectedSdgNumbers are the single source of truth for turning a raw
  predictions map into the SDG numbers a repo actually matched, shared by CardGrid and the
  context-folder export so the on-screen cards and the downloaded files can never drift apart.
*/

export const SDG_DESCRIPTIONS: Record<number, string> = {
  1: "Goal 1 calls for an end to poverty in all its manifestations, including extreme poverty, over the next 15 years. All people everywhere, including the poorest and most vulnerable, should enjoy a basic standard of living and social protection benefits.",
  2: "Goal 2 seeks to end hunger and all forms of malnutrition and to achieve sustainable food production by 2030. It is premised on the idea that everyone should have access to sufficient nutritious food, which will require widespread promotion of sustainable agriculture, a doubling of agricultural productivity, increased investments and properly functioning food markets.",
  3: "Goal 3 aims to ensure health and well-being for all at all ages by improving reproductive, maternal and child health; ending the epidemics of major communicable diseases; reducing non-communicable and environmental diseases; achieving universal health coverage; and ensuring access to safe, affordable and effective medicines and vaccines for all.",
  4: "Goal 4 focuses on the acquisition of foundational and higher-order skills; greater and more equitable access to technical and vocational education and training and higher education; training throughout life; and the knowledge, skills and values needed to function well and contribute to society.",
  5: "Goal 5 aims to empower women and girls to reach their full potential, which requires eliminating all forms of discrimination and violence against them, including harmful practices. It seeks to ensure that they have every opportunity for sexual and reproductive health and reproductive rights; receive due recognition for their unpaid work; have full access to productive resources; and enjoy equal participation with men in political, economic and public life.",
  6: "Goal 6 goes beyond drinking water, sanitation and hygiene to also address the quality and sustainability of water resources. Achieving this Goal, which is critical to the survival of people and the planet, means expanding international cooperation and garnering the support of local communities in improving water and sanitation management.",
  7: "Goal 7 seeks to promote broader energy access and increased use of renewable energy, including through enhanced international cooperation and expanded infrastructure and technology for clean energy.",
  8: "Goal 8 aims to provide opportunities for full and productive employment and decent work for all while eradicating forced labour, human trafficking and child labour.",
  9: "Goal 9 focuses on the promotion of infrastructure development, industrialization and innovation. This can be accomplished through enhanced international and domestic financial, technological and technical support, research and innovation, and increased access to information and communication technology.",
  10: "Goal 10 calls for reducing inequalities in income, as well as those based on sex, age, disability, race, class, ethnicity, religion and opportunity—both within and among countries. It also aims to ensure safe, orderly and regular migration and addresses issues related to representation of developing countries in global decision-making and development assistance.",
  11: "Goal 11 aims to renew and plan cities and other human settlements in a way that fosters community cohesion and personal security while stimulating innovation and employment.",
  12: "Goal 12 aims to promote sustainable consumption and production patterns through measures such as specific policies and international agreements on the management of materials that are toxic to the environment.",
  13: "Climate change presents the single biggest threat to development, and its widespread, unprecedented effects disproportionately burden the poorest and the most vulnerable. Urgent action is needed not only to combat climate change and its impacts, but also to build resilience in responding to climate-related hazards and natural disasters.",
  14: "Goal 14 seeks to promote the conservation and sustainable use of marine and coastal ecosystems, prevent marine pollution and increase the economic benefits to small island developing States and LDCs from the sustainable use of marine resources.",
  15: "Goal 15 focuses on managing forests sustainably, restoring degraded lands and successfully combating desertification, reducing degraded natural habitats and ending biodiversity loss. All of these efforts in combination will help ensure that livelihoods are preserved for those that depend directly on forests and other ecosystems, that biodiversity will thrive, and that the benefits of these natural resources will be enjoyed for generations to come.",
  16: "Goal 16 envisages peaceful and inclusive societies based on respect for human rights, the rule of law, good governance at all levels, and transparent, effective and accountable institutions. Many countries still face protracted violence and armed conflict, and far too many people are poorly supported by weak institutions and lack access to justice, information and other fundamental freedoms.",
  17: "The 2030 Agenda requires a revitalized and enhanced global partnership that mobilizes all available resources from Governments, civil society, the private sector, the United Nations system and other actors. Increasing support to developing countries, in particular LDCs, landlocked developing countries and small island developing States is fundamental to equitable progress for all.",
};

export type ParsedPrediction = {
  number: string;
  name: string;
  score: number;
};

export const getSdgName = (sdgNumber: number): string =>
  SDG[sdgNumber as keyof typeof SDG] ?? `SDG ${sdgNumber}`;

export const getSdgDescription = (sdgNumber: number): string =>
  SDG_DESCRIPTIONS[sdgNumber] ?? "";

export function parsePrediction(
  sourceKey: string,
  item: SDGValue | number,
): ParsedPrediction | null {
  const value: SDGValue = typeof item === "number" ? { prediction: item } : item;
  const score = Number(value.prediction ?? 0);

  if (value.sdg == null || score <= 0) return null;

  const fallbackNumberFromKey = sourceKey.match(/\d+/)?.[0];
  const number =
    typeof value.sdg === "string"
      ? value.sdg.match(/\d+/)?.[0] || fallbackNumberFromKey
      : value.sdg.code || fallbackNumberFromKey;

  if (!number) return null;

  const name =
    typeof value.sdg === "string"
      ? value.sdg.replace(/^SDG\s*\d+\s*:?\s*/i, "").trim() || value.sdg
      : value.sdg.name ||
        value.sdg.label ||
        sourceKey.replace(/^SDG\s*\d+\s*:?\s*/i, "").trim() ||
        `SDG ${number}`;

  return { number, name, score };
}

export function getSelectedSdgNumbers(
  predictions:
    | SDGValue[]
    | Record<string, SDGValue>
    | Record<string, number>
    | undefined,
): number[] {
  const entries: Array<[string, SDGValue | number]> = Array.isArray(predictions)
    ? predictions.map((item, index) => [String(index), item])
    : Object.entries(predictions ?? {});

  const numbers = new Set<number>();
  for (const [sourceKey, item] of entries) {
    const parsed = parsePrediction(sourceKey, item);
    if (parsed) {
      const n = Number(parsed.number);
      if (Number.isFinite(n)) numbers.add(n);
    }
  }

  return Array.from(numbers).sort((a, b) => a - b);
}
