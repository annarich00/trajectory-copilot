/**
 * Tests for `.pi/extensions/orbital-problem-formalizer-tool/formalizer.ts`
 * (TJC-23.2). Covers one READY TO SOLVE case and one NEEDS CLARIFICATION
 * case per the task's acceptance criteria, plus the deterministic
 * structural/legality checks the tool is responsible for (illegal
 * provenance labels, readiness/blocking-issue/clarification-question
 * consistency with the supplied field provenances).
 *
 * Run with: node --experimental-strip-types --test
 *   .pi/extensions/orbital-problem-formalizer-tool/formalizer.test.ts
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { validateFormalization, type FormalizationInput, type FieldInput } from "./formalizer.ts";

function specified(value: string): FieldInput {
  return { value, provenance: "specified" };
}

function derived(value: string): FieldInput {
  return { value, provenance: "derived" };
}

function missing(): FieldInput {
  return { value: "unknown", provenance: "missing" };
}

/** A fully specified two-spacecraft circular-LEO LVLH rendezvous request:
 * every required field is 'specified' or 'derived', so it should validate
 * as READY TO SOLVE. */
const readyToSolveInput: FormalizationInput = {
  naturalLanguageRequest:
    "Chaser starts 1 km behind the chief (LVLH -x) with no relative velocity, 400 km circular LEO orbit, " +
    "rendezvous (zero relative position and velocity) in 2700 s using two impulsive burns.",
  scope: {
    classification: specified("supported"),
    reason: specified("Two spacecraft, circular LEO, impulsive LVLH rendezvous with a stated time of flight."),
  },
  participants: {
    centralBody: specified("Earth"),
    targetChief: specified("Chief"),
    chaserDeputy: specified("Chaser"),
  },
  referenceOrbit: {
    circularity: specified("circular"),
    altitude: specified("400 km"),
    radiusOrElements: derived("6778137 m (Earth radius 6378137 m + altitude 400 km)"),
    gravitationalParameter: specified("398600441800000 m^3/s^2 (Earth mu)"),
    meanMotionOrPeriod: derived("period ~5553 s via sqrt(radius^3/mu)"),
  },
  relativeFrameAndState: {
    frame: specified("LVLH/Hill"),
    lvlhConvention: specified("x radial outward, y along-track, z cross-track (right-handed)"),
    initialRelativePosition: specified("[-1000, 0, 0] m"),
    initialRelativeVelocity: specified("[0, 0, 0] m/s"),
  },
  terminalConditions: {
    relativePosition: specified("[0, 0, 0] m"),
    relativeVelocity: specified("[0, 0, 0] m/s"),
    requestedOutputs: specified("burn vectors and final relative state"),
  },
  timingAndManeuvers: {
    timeOfFlight: specified("2700 s"),
    periodCount: missing(),
    maneuverAssumptions: specified("two impulsive burns, no plume/attitude constraints stated"),
  },
  blockingIssues: ["None"],
  clarificationQuestions: ["None"],
  readiness: "READY TO SOLVE",
  formalizationSummary: "A fully specified circular-LEO LVLH rendezvous with a stated time of flight and burn count.",
};

/** The same request but missing the LVLH convention and terminal relative
 * velocity, and with an ambiguous time-of-flight phrase -- should validate
 * as NEEDS CLARIFICATION. */
const needsClarificationInput: FormalizationInput = {
  naturalLanguageRequest: "Chaser is behind the chief in a 400 km circular orbit; bring it in soon.",
  scope: {
    classification: specified("supported"),
    reason: specified("Two spacecraft, circular LEO, impulsive LVLH rendezvous, but key fields are unresolved."),
  },
  participants: {
    centralBody: specified("Earth"),
    targetChief: specified("Chief"),
    chaserDeputy: specified("Chaser"),
  },
  referenceOrbit: {
    circularity: specified("circular"),
    altitude: specified("400 km"),
    radiusOrElements: derived("6778137 m (Earth radius 6378137 m + altitude 400 km)"),
    gravitationalParameter: specified("398600441800000 m^3/s^2 (Earth mu)"),
    meanMotionOrPeriod: derived("period ~5553 s via sqrt(radius^3/mu)"),
  },
  relativeFrameAndState: {
    frame: specified("LVLH/Hill"),
    lvlhConvention: { value: "unknown", provenance: "missing" },
    initialRelativePosition: { value: "'behind' is not a vector", provenance: "ambiguous" },
    initialRelativeVelocity: missing(),
  },
  terminalConditions: {
    relativePosition: specified("[0, 0, 0] m (rendezvous at the chief)"),
    relativeVelocity: { value: "'bring it in' does not state a terminal velocity", provenance: "ambiguous" },
    requestedOutputs: specified("burn vectors and final relative state"),
  },
  timingAndManeuvers: {
    timeOfFlight: { value: "'soon' is not a duration", provenance: "ambiguous" },
    periodCount: missing(),
    maneuverAssumptions: missing(),
  },
  blockingIssues: [
    "LVLH convention (axis directions/signs) was not supplied.",
    "Initial relative position is only described qualitatively ('behind'), not as a vector.",
    "Initial relative velocity was not supplied.",
    "Terminal relative velocity is ambiguous ('bring it in').",
    "Time of flight is ambiguous ('soon').",
    "Maneuver assumptions (burn count/timing/constraints) were not supplied.",
  ],
  clarificationQuestions: [
    "What LVLH axis convention (directions and signs) should be used?",
    "What is the chaser's initial relative position as an [x, y, z] vector with units?",
    "What is the chaser's initial relative velocity as an [xdot, ydot, zdot] vector with units?",
    "Should the terminal relative velocity be zero, or some other specific value?",
    "What numeric time of flight (or period count) is requested?",
    "How many impulsive burns are expected, and are there timing or attitude constraints?",
  ],
  readiness: "NEEDS CLARIFICATION",
  formalizationSummary: "The request names a circular-LEO LVLH rendezvous but leaves several required fields unresolved.",
};

test("READY TO SOLVE: fully specified request validates with no errors and renders all required sections", () => {
  const result = validateFormalization(readyToSolveInput);
  assert.equal(result.valid, true, result.errors.join("; "));
  assert.deepEqual(result.errors, []);
  assert.match(result.markdown, /### Readiness\nREADY TO SOLVE/);
  assert.match(result.markdown, /### Blocking Issues\n- None/);
  assert.match(result.markdown, /### Scope\n- Classification: supported — specified/);
  for (const heading of [
    "Scope",
    "Participants",
    "Reference Orbit",
    "Relative Frame and State",
    "Terminal Conditions",
    "Timing and Maneuvers",
    "Blocking Issues",
    "Clarification Questions",
    "Readiness",
    "Formalization Summary",
  ]) {
    assert.match(result.markdown, new RegExp(`### ${heading}`), `missing section: ${heading}`);
  }
});

test("NEEDS CLARIFICATION: under-specified request validates with no errors and lists blocking issues", () => {
  const result = validateFormalization(needsClarificationInput);
  assert.equal(result.valid, true, result.errors.join("; "));
  assert.deepEqual(result.errors, []);
  assert.match(result.markdown, /### Readiness\nNEEDS CLARIFICATION/);
  assert.match(result.markdown, /LVLH convention \(axis directions\/signs\) was not supplied\./);
  assert.match(result.markdown, /What LVLH axis convention/);
});

test("rejects a caller-reported READY TO SOLVE when a required field is only 'assumed'", () => {
  const input: FormalizationInput = structuredClone(readyToSolveInput);
  input.relativeFrameAndState.lvlhConvention = {
    value: "x radial outward, y along-track, z cross-track",
    provenance: "assumed",
  };
  const result = validateFormalization(input);
  assert.equal(result.valid, false);
  assert.ok(
    result.errors.some((e) => e.startsWith("readiness:")),
    `expected a readiness-consistency error, got: ${result.errors.join("; ")}`,
  );
});

test("rejects an illegal provenance label", () => {
  const input: FormalizationInput = structuredClone(readyToSolveInput);
  // @ts-expect-error -- intentionally illegal for this test
  input.participants.centralBody = { value: "Earth", provenance: "guessed" };
  const result = validateFormalization(input);
  assert.equal(result.valid, false);
  assert.ok(result.errors.some((e) => e.includes("illegal provenance label")));
});

test("rejects READY TO SOLVE reported with non-'None' blocking issues", () => {
  const input: FormalizationInput = structuredClone(readyToSolveInput);
  input.blockingIssues = ["Some leftover issue"];
  const result = validateFormalization(input);
  assert.equal(result.valid, false);
  assert.ok(result.errors.some((e) => e.startsWith("blockingIssues:")));
});

test("rejects NEEDS CLARIFICATION reported with 'None' blocking issues", () => {
  const input: FormalizationInput = structuredClone(needsClarificationInput);
  input.blockingIssues = ["None"];
  const result = validateFormalization(input);
  assert.equal(result.valid, false);
  assert.ok(result.errors.some((e) => e.startsWith("blockingIssues:")));
});

test("OUT OF SCOPE classification short-circuits readiness regardless of other fields", () => {
  const input: FormalizationInput = structuredClone(readyToSolveInput);
  input.scope.classification = { value: "out of scope", provenance: "out of scope" };
  input.scope.reason = { value: "Three spacecraft requested; only two-spacecraft cases are supported.", provenance: "specified" };
  input.readiness = "OUT OF SCOPE";
  input.blockingIssues = ["Request involves three spacecraft, which is outside the supported class."];
  input.clarificationQuestions = ["Please restate the request as a two-spacecraft rendezvous, if applicable."];
  const result = validateFormalization(input);
  assert.equal(result.valid, true, result.errors.join("; "));
  assert.match(result.markdown, /### Readiness\nOUT OF SCOPE/);
});
