/**
 * Deterministic core of the `formalize_rendezvous_problem` pi tool (TJC-23.2).
 *
 * This module contains NO natural-language reasoning. Parsing a free-text
 * rendezvous request into Scope/Participants/Reference-Orbit/Relative-
 * Frame-and-State/Terminal-Conditions/Timing-and-Maneuvers fields, and
 * choosing each field's provenance label, is the calling LLM's judgment
 * call -- it must do that reasoning itself (the same judgment
 * `.pi/skills/orbital-problem-formalizer/SKILL.md` used to ask an agent to
 * apply as free-form instructions) before calling the tool built on this
 * module (see `./index.ts`).
 *
 * What this module deterministically enforces instead:
 *
 *   1. Every field's provenance label is one of the skill's eight legal
 *      labels (`PROVENANCE_LABELS`); `./index.ts`'s TypeBox schema already
 *      rejects illegal labels at the tool-call boundary, and
 *      `validateFormalization` re-checks it so this module stays correct
 *      when exercised directly (e.g. by tests).
 *   2. Scope/Readiness/Blocking-Issues/Clarification-Questions are
 *      self-consistent with the supplied field provenances -- e.g. a
 *      request can never be reported READY TO SOLVE while a required
 *      field is still `missing`, `assumed`, `ambiguous`, `contradictory`,
 *      `unit-inconsistent`, or `out of scope`, matching the skill's rule
 *      that assumptions never satisfy required inputs or readiness.
 *   3. The final required Markdown-equivalent output is produced in
 *      exactly the skill's field order and labels.
 */

export const PROVENANCE_LABELS = [
  "specified",
  "derived",
  "assumed",
  "missing",
  "ambiguous",
  "contradictory",
  "unit-inconsistent",
  "out of scope",
] as const;

export type ProvenanceLabel = (typeof PROVENANCE_LABELS)[number];

/** Labels that satisfy a required field for READY TO SOLVE purposes. Every
 * other legal label (including `assumed`) leaves the field unresolved, per
 * the skill's provenance rules. */
const SATISFYING_LABELS: ReadonlySet<ProvenanceLabel> = new Set(["specified", "derived"]);

export type Readiness = "READY TO SOLVE" | "NEEDS CLARIFICATION" | "OUT OF SCOPE";

export const READINESS_VALUES: readonly Readiness[] = ["READY TO SOLVE", "NEEDS CLARIFICATION", "OUT OF SCOPE"];

export interface FieldInput {
  value: string;
  provenance: ProvenanceLabel;
}

export interface FormalizationInput {
  naturalLanguageRequest: string;
  scope: {
    classification: FieldInput; // value must be "supported" | "out of scope"
    reason: FieldInput;
  };
  participants: {
    centralBody: FieldInput;
    targetChief: FieldInput;
    chaserDeputy: FieldInput;
  };
  referenceOrbit: {
    circularity: FieldInput;
    altitude: FieldInput;
    radiusOrElements: FieldInput;
    gravitationalParameter: FieldInput;
    meanMotionOrPeriod: FieldInput;
  };
  relativeFrameAndState: {
    frame: FieldInput;
    lvlhConvention: FieldInput;
    initialRelativePosition: FieldInput;
    initialRelativeVelocity: FieldInput;
  };
  terminalConditions: {
    relativePosition: FieldInput;
    relativeVelocity: FieldInput;
    requestedOutputs: FieldInput;
  };
  timingAndManeuvers: {
    timeOfFlight: FieldInput;
    periodCount: FieldInput;
    maneuverAssumptions: FieldInput;
  };
  blockingIssues: string[]; // exactly ["None"] when there are none
  clarificationQuestions: string[]; // exactly ["None"] when there are none
  readiness: Readiness;
  formalizationSummary: string;
}

export interface FormalizationResult {
  valid: boolean;
  errors: string[];
  /** The skill's required Markdown rendering; empty when `valid` is false. */
  markdown: string;
  /** The input, echoed back unchanged. */
  structured: FormalizationInput;
}

function isSatisfied(field: FieldInput): boolean {
  return SATISFYING_LABELS.has(field.provenance);
}

/** Every `FieldInput` in the schema, labeled with its dotted path, in the
 * skill's required field order. Used for the generic provenance/value
 * legality checks and the Markdown renderer. */
function allFields(input: FormalizationInput): Array<[string, FieldInput]> {
  return [
    ["scope.classification", input.scope.classification],
    ["scope.reason", input.scope.reason],
    ["participants.centralBody", input.participants.centralBody],
    ["participants.targetChief", input.participants.targetChief],
    ["participants.chaserDeputy", input.participants.chaserDeputy],
    ["referenceOrbit.circularity", input.referenceOrbit.circularity],
    ["referenceOrbit.altitude", input.referenceOrbit.altitude],
    ["referenceOrbit.radiusOrElements", input.referenceOrbit.radiusOrElements],
    ["referenceOrbit.gravitationalParameter", input.referenceOrbit.gravitationalParameter],
    ["referenceOrbit.meanMotionOrPeriod", input.referenceOrbit.meanMotionOrPeriod],
    ["relativeFrameAndState.frame", input.relativeFrameAndState.frame],
    ["relativeFrameAndState.lvlhConvention", input.relativeFrameAndState.lvlhConvention],
    ["relativeFrameAndState.initialRelativePosition", input.relativeFrameAndState.initialRelativePosition],
    ["relativeFrameAndState.initialRelativeVelocity", input.relativeFrameAndState.initialRelativeVelocity],
    ["terminalConditions.relativePosition", input.terminalConditions.relativePosition],
    ["terminalConditions.relativeVelocity", input.terminalConditions.relativeVelocity],
    ["terminalConditions.requestedOutputs", input.terminalConditions.requestedOutputs],
    ["timingAndManeuvers.timeOfFlight", input.timingAndManeuvers.timeOfFlight],
    ["timingAndManeuvers.periodCount", input.timingAndManeuvers.periodCount],
    ["timingAndManeuvers.maneuverAssumptions", input.timingAndManeuvers.maneuverAssumptions],
  ];
}

/** Computes the Readiness value the supplied field provenances are
 * consistent with, independent of what the caller reported. Mirrors the
 * skill's "Evaluation and readiness rules" section:
 *
 * - `OUT OF SCOPE` whenever Scope is classified out of scope.
 * - `READY TO SOLVE` only when every required field is `specified` or
 *   `derived`, including the "altitude, radius, or complete elements"
 *   reference-orbit group, the terminal-condition group, and the
 *   "time of flight or period count" group, each satisfied by at least
 *   one specified/derived member (the skill itself allows either member
 *   of each pair to carry the required information).
 * - `NEEDS CLARIFICATION` otherwise.
 */
export function computeRequiredReadiness(input: FormalizationInput): Readiness {
  const classificationValue = input.scope.classification.value.trim().toLowerCase();
  if (classificationValue === "out of scope" || input.scope.classification.provenance === "out of scope") {
    return "OUT OF SCOPE";
  }

  const singleRequired: FieldInput[] = [
    input.participants.centralBody,
    input.participants.targetChief,
    input.participants.chaserDeputy,
    input.referenceOrbit.circularity,
    input.referenceOrbit.gravitationalParameter,
    input.relativeFrameAndState.frame,
    input.relativeFrameAndState.lvlhConvention,
    input.relativeFrameAndState.initialRelativePosition,
    input.relativeFrameAndState.initialRelativeVelocity,
    input.timingAndManeuvers.maneuverAssumptions,
    input.terminalConditions.requestedOutputs,
  ];
  const allSingleSatisfied = singleRequired.every(isSatisfied);

  // "Circular reference orbit through altitude, radius, or complete elements."
  const referenceOrbitSizeSatisfied =
    isSatisfied(input.referenceOrbit.altitude) || isSatisfied(input.referenceOrbit.radiusOrElements);

  // "One or more complete terminal conditions."
  const terminalConditionSatisfied =
    isSatisfied(input.terminalConditions.relativePosition) || isSatisfied(input.terminalConditions.relativeVelocity);

  // "A time of flight or period count."
  const timingSatisfied =
    isSatisfied(input.timingAndManeuvers.timeOfFlight) || isSatisfied(input.timingAndManeuvers.periodCount);

  const ready = allSingleSatisfied && referenceOrbitSizeSatisfied && terminalConditionSatisfied && timingSatisfied;
  return ready ? "READY TO SOLVE" : "NEEDS CLARIFICATION";
}

function isNoneOnly(list: string[]): boolean {
  return list.length === 1 && list[0].trim().toLowerCase() === "none";
}

/** Validates a caller-supplied formalization for structural and label
 * legality and for Readiness/Blocking-Issues/Clarification-Questions
 * self-consistency, then renders the skill's required Markdown when valid.
 * Field-by-field judgment (what each value and provenance label should be)
 * is never performed here -- only the deterministic checks described in
 * this module's header comment. */
export function validateFormalization(input: FormalizationInput): FormalizationResult {
  const errors: string[] = [];

  for (const [path, field] of allFields(input)) {
    if (!(PROVENANCE_LABELS as readonly string[]).includes(field.provenance)) {
      errors.push(`${path}.provenance: illegal provenance label '${field.provenance}'`);
    }
    if (field.value.trim().length === 0) {
      errors.push(`${path}.value: must not be empty (use 'unknown' when the field was not supplied)`);
    }
  }

  const classificationValue = input.scope.classification.value.trim().toLowerCase();
  if (classificationValue !== "supported" && classificationValue !== "out of scope") {
    errors.push(
      `scope.classification.value: must be 'supported' or 'out of scope', got '${input.scope.classification.value}'`,
    );
  }

  if (!READINESS_VALUES.includes(input.readiness)) {
    errors.push(`readiness: illegal value '${input.readiness}'`);
  }

  const requiredReadiness = computeRequiredReadiness(input);
  if (input.readiness !== requiredReadiness) {
    errors.push(
      `readiness: caller reported '${input.readiness}' but the supplied field provenances are only ` +
        `consistent with '${requiredReadiness}' (READY TO SOLVE requires every required field's provenance ` +
        "to be 'specified' or 'derived'; 'assumed' never satisfies a required field, per the skill's " +
        "provenance rules).",
    );
  }

  if (requiredReadiness === "READY TO SOLVE") {
    if (!isNoneOnly(input.blockingIssues)) {
      errors.push("blockingIssues: must be exactly ['None'] when every required field is specified/derived.");
    }
    if (!isNoneOnly(input.clarificationQuestions)) {
      errors.push("clarificationQuestions: must be exactly ['None'] when there are no blocking issues.");
    }
  } else {
    if (isNoneOnly(input.blockingIssues)) {
      errors.push(`blockingIssues: must list at least one concrete issue when readiness is '${requiredReadiness}'.`);
    }
    if (requiredReadiness === "NEEDS CLARIFICATION" && isNoneOnly(input.clarificationQuestions)) {
      errors.push(
        "clarificationQuestions: must ask at least one focused question when readiness is 'NEEDS CLARIFICATION'.",
      );
    }
  }

  const sentenceCount = input.formalizationSummary
    .split(/[.!?]+/)
    .map((sentence) => sentence.trim())
    .filter(Boolean).length;
  if (sentenceCount > 2) {
    errors.push(`formalizationSummary: must be at most two sentences (counted ${sentenceCount}).`);
  }

  return {
    valid: errors.length === 0,
    errors,
    markdown: errors.length === 0 ? renderMarkdown(input) : "",
    structured: input,
  };
}

function renderField(field: FieldInput): string {
  return `${field.value} — ${field.provenance}`;
}

function renderList(items: string[]): string {
  return items.map((item) => `- ${item}`).join("\n");
}

/** Renders the skill's required Markdown schema (Scope through
 * Formalization Summary), preserving all field names and order exactly as
 * `.pi/skills/orbital-problem-formalizer/SKILL.md` specified them. */
function renderMarkdown(input: FormalizationInput): string {
  return `### Scope
- Classification: ${renderField(input.scope.classification)}
- Reason: ${renderField(input.scope.reason)}

### Participants
- Central body: ${renderField(input.participants.centralBody)}
- Target/chief: ${renderField(input.participants.targetChief)}
- Chaser/deputy: ${renderField(input.participants.chaserDeputy)}

### Reference Orbit
- Circularity: ${renderField(input.referenceOrbit.circularity)}
- Altitude: ${renderField(input.referenceOrbit.altitude)}
- Radius or orbital elements: ${renderField(input.referenceOrbit.radiusOrElements)}
- Gravitational parameter: ${renderField(input.referenceOrbit.gravitationalParameter)}
- Mean motion or period: ${renderField(input.referenceOrbit.meanMotionOrPeriod)}

### Relative Frame and State
- Frame: ${renderField(input.relativeFrameAndState.frame)}
- LVLH convention: ${renderField(input.relativeFrameAndState.lvlhConvention)}
- Initial relative position: ${renderField(input.relativeFrameAndState.initialRelativePosition)}
- Initial relative velocity: ${renderField(input.relativeFrameAndState.initialRelativeVelocity)}

### Terminal Conditions
- Relative position: ${renderField(input.terminalConditions.relativePosition)}
- Relative velocity: ${renderField(input.terminalConditions.relativeVelocity)}
- Requested outputs: ${renderField(input.terminalConditions.requestedOutputs)}

### Timing and Maneuvers
- Time of flight: ${renderField(input.timingAndManeuvers.timeOfFlight)}
- Period count: ${renderField(input.timingAndManeuvers.periodCount)}
- Maneuver assumptions: ${renderField(input.timingAndManeuvers.maneuverAssumptions)}

### Blocking Issues
${renderList(input.blockingIssues)}

### Clarification Questions
${renderList(input.clarificationQuestions)}

### Readiness
${input.readiness}

### Formalization Summary
${input.formalizationSummary}`;
}
