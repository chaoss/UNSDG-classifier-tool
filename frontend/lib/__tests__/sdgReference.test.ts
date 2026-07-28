import { parsePrediction, getSelectedSdgNumbers } from "@/lib/sdgReference";

describe("parsePrediction", () => {
  it("extracts number and name from a string sdg field", () => {
    const result = parsePrediction("SDG 3: Good Health and Well-being", {
      prediction: 0.8,
      sdg: "SDG 3: Good Health and Well-being",
    });

    expect(result).toEqual({
      number: "3",
      name: "Good Health and Well-being",
      score: 0.8,
    });
  });

  it("extracts number/name from an object sdg field with code/name", () => {
    const result = parsePrediction("goal_9", {
      prediction: 0.65,
      sdg: { code: "9", name: "Industry, Innovation and Infrastructure" },
    });

    expect(result).toEqual({
      number: "9",
      name: "Industry, Innovation and Infrastructure",
      score: 0.65,
    });
  });

  it("falls back to label when object sdg has no name", () => {
    const result = parsePrediction("goal_5", {
      prediction: 0.5,
      sdg: { code: "5", label: "Gender Equality" },
    });

    expect(result?.name).toBe("Gender Equality");
  });

  it("falls back to the numeric part of sourceKey when sdg has no digits", () => {
    const result = parsePrediction("SDG 7", {
      prediction: 0.9,
      sdg: { name: "Affordable and Clean Energy" },
    });

    expect(result?.number).toBe("7");
  });

  it("accepts a bare number as the prediction value", () => {
    const result = parsePrediction("SDG 1: No Poverty", 0.42);
    expect(result).toBeNull();
  });

  it("returns null when score is zero or negative", () => {
    expect(
      parsePrediction("SDG 2: Zero Hunger", {
        prediction: 0,
        sdg: "SDG 2: Zero Hunger",
      }),
    ).toBeNull();

    expect(
      parsePrediction("SDG 2: Zero Hunger", {
        prediction: -0.1,
        sdg: "SDG 2: Zero Hunger",
      }),
    ).toBeNull();
  });

  it("returns null when sdg is missing entirely", () => {
    expect(parsePrediction("SDG 4", { prediction: 0.7 })).toBeNull();
  });

  it("returns null when no number can be derived at all", () => {
    const result = parsePrediction("no-digits-here", {
      prediction: 0.5,
      sdg: { name: "Mystery Goal" },
    });
    expect(result).toBeNull();
  });
});

describe("getSelectedSdgNumbers", () => {
  it("dedupes and sorts ascending", () => {
    const predictions = {
      a: { prediction: 0.9, sdg: "SDG 9: Industry" },
      b: { prediction: 0.3, sdg: "SDG 1: No Poverty" },
      c: { prediction: 0.5, sdg: "SDG 9: Industry" },
    };

    expect(getSelectedSdgNumbers(predictions)).toEqual([1, 9]);
  });

  it("ignores entries with zero or negative scores", () => {
    const predictions = {
      a: { prediction: 0, sdg: "SDG 3: Health" },
      b: { prediction: 0.6, sdg: "SDG 4: Education" },
    };

    expect(getSelectedSdgNumbers(predictions)).toEqual([4]);
  });

  it("handles a Record<string, number> shape (no sdg field, always empty)", () => {
    const predictions = { "SDG 1": 0.8, "SDG 2": 0.4 };
    expect(getSelectedSdgNumbers(predictions)).toEqual([]);
  });

  it("handles an array shape", () => {
    const predictions = [
      { prediction: 0.7, sdg: "SDG 13: Climate Action" },
      { prediction: 0.2, sdg: "SDG 6: Clean Water" },
    ];
    expect(getSelectedSdgNumbers(predictions)).toEqual([6, 13]);
  });

  it("returns an empty array for undefined predictions", () => {
    expect(getSelectedSdgNumbers(undefined)).toEqual([]);
  });
});
