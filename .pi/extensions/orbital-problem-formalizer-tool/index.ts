/**
 * formalize_rendezvous_problem pi tool (TJC-23.2)
 *
 * Registers `.pi/skills/orbital-problem-formalizer/SKILL.md`'s required
 * output schema and provenance-label rules as an explicit, auditable pi
 * tool call, mirroring `run_gmat_verification`
 * (`.pi/extensions/gmat-verification-tool/index.ts`)'s pattern: a thin
 * TypeScript wrapper around a deterministic core, rather than free-form
 * skill instructions the agent applies invisibly.
 *
 * Formalizing a natural-language rendezvous request -- parsing it into the
 * Scope/Participants/Reference-Orbit/Relative-Frame-and-State/Terminal-
 * Conditions/Timing-and-Maneuvers fields and choosing each field's
 * provenance label -- is fundamentally LLM judgment, not a deterministic
 * calculation. This tool does NOT perform that judgment. The calling LLM
 * must do its own reasoning over `natural_language_request` first (exactly
 * the reasoning the old SKILL.md asked an agent to do free-form) and pass
 * its already-reasoned field values and provenance labels as this tool's
 * structured input. The tool's job -- performed by
 * `./formalizer.ts::validateFormalization` -- is strictly the deterministic
 * part: enforcing the eight-label provenance vocabulary, enforcing that
 * Readiness/Blocking-Issues/Clarification-Questions stay consistent with
 * the supplied field provenances (e.g. rejecting a caller-reported
 * READY TO SOLVE when a required field is still `assumed`/`missing`/
 * `ambiguous`/`contradictory`/`unit-inconsistent`/`out of scope`), and
 * rendering the skill's required Markdown-equivalent output in its exact
 * field order. A caller that gets a field's judgment wrong (the wrong
 * provenance label for a given fact) is not caught here -- only
 * structural/legality mistakes are.
 */
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { StringEnum } from "@earendil-works/pi-ai";
import { Type } from "typebox";
import {
  PROVENANCE_LABELS,
  READINESS_VALUES,
  validateFormalization,
  type FormalizationInput,
} from "./formalizer.ts";

const provenanceSchema = StringEnum(PROVENANCE_LABELS);

function fieldSchema(description: string) {
  return Type.Object({
    value: Type.String({ description: `${description} Use 'unknown' when not supplied.` }),
    provenance: provenanceSchema,
  });
}

const formalizeRendezvousProblemSchema = Type.Object({
  natural_language_request: Type.String({
    description:
      "The operator's original free-text rendezvous request. Recorded for audit/traceability; this tool does " +
        "not parse it -- the caller must already have derived every field below from it.",
  }),
  scope: Type.Object({
    classification: fieldSchema("'supported' or 'out of scope'."),
    reason: fieldSchema("Concise reason for the classification."),
  }),
  participants: Type.Object({
    central_body: fieldSchema("Central body name."),
    target_chief: fieldSchema("Target/chief identifier."),
    chaser_deputy: fieldSchema("Chaser/deputy identifier."),
  }),
  reference_orbit: Type.Object({
    circularity: fieldSchema("'circular', 'non-circular', or 'unknown'."),
    altitude: fieldSchema("Reference-orbit altitude, with units."),
    radius_or_elements: fieldSchema("Orbital radius or complete orbital elements, with units."),
    gravitational_parameter: fieldSchema("Central-body gravitational parameter, with units."),
    mean_motion_or_period: fieldSchema("Mean motion or orbital period, with units."),
  }),
  relative_frame_and_state: Type.Object({
    frame: fieldSchema("'LVLH/Hill' or 'unknown'."),
    lvlh_convention: fieldSchema("x/y/z axis directions and signs."),
    initial_relative_position: fieldSchema("[x, y, z] with units."),
    initial_relative_velocity: fieldSchema("[xdot, ydot, zdot] with units."),
  }),
  terminal_conditions: Type.Object({
    relative_position: fieldSchema("[x, y, z] with units."),
    relative_velocity: fieldSchema("[xdot, ydot, zdot] with units."),
    requested_outputs: fieldSchema("e.g. burn vectors, final state."),
  }),
  timing_and_maneuvers: Type.Object({
    time_of_flight: fieldSchema("Time of flight, with units."),
    period_count: fieldSchema("Period count."),
    maneuver_assumptions: fieldSchema("Impulsive burn count, timing, and constraints."),
  }),
  blocking_issues: Type.Array(Type.String(), {
    description: "One entry per missing/ambiguous/contradictory/unit-inconsistent/out-of-scope required field. " +
      "Exactly ['None'] when there are none.",
    minItems: 1,
  }),
  clarification_questions: Type.Array(Type.String(), {
    description: "One focused question per blocking issue. Exactly ['None'] when there are none.",
    minItems: 1,
  }),
  readiness: StringEnum(READINESS_VALUES as unknown as readonly [string, ...string[]]),
  formalization_summary: Type.String({
    description: "At most two sentences. Must not solve or calculate values.",
  }),
});

function toFormalizationInput(params: Record<string, any>): FormalizationInput {
  return {
    naturalLanguageRequest: params.natural_language_request,
    scope: {
      classification: params.scope.classification,
      reason: params.scope.reason,
    },
    participants: {
      centralBody: params.participants.central_body,
      targetChief: params.participants.target_chief,
      chaserDeputy: params.participants.chaser_deputy,
    },
    referenceOrbit: {
      circularity: params.reference_orbit.circularity,
      altitude: params.reference_orbit.altitude,
      radiusOrElements: params.reference_orbit.radius_or_elements,
      gravitationalParameter: params.reference_orbit.gravitational_parameter,
      meanMotionOrPeriod: params.reference_orbit.mean_motion_or_period,
    },
    relativeFrameAndState: {
      frame: params.relative_frame_and_state.frame,
      lvlhConvention: params.relative_frame_and_state.lvlh_convention,
      initialRelativePosition: params.relative_frame_and_state.initial_relative_position,
      initialRelativeVelocity: params.relative_frame_and_state.initial_relative_velocity,
    },
    terminalConditions: {
      relativePosition: params.terminal_conditions.relative_position,
      relativeVelocity: params.terminal_conditions.relative_velocity,
      requestedOutputs: params.terminal_conditions.requested_outputs,
    },
    timingAndManeuvers: {
      timeOfFlight: params.timing_and_maneuvers.time_of_flight,
      periodCount: params.timing_and_maneuvers.period_count,
      maneuverAssumptions: params.timing_and_maneuvers.maneuver_assumptions,
    },
    blockingIssues: params.blocking_issues,
    clarificationQuestions: params.clarification_questions,
    readiness: params.readiness,
    formalizationSummary: params.formalization_summary,
  };
}

export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "formalize_rendezvous_problem",
    label: "Formalize Rendezvous Problem",
    // This description carries forward the retired
    // `.pi/skills/orbital-problem-formalizer/SKILL.md`'s own `description`
    // ("Formalize only a two-spacecraft, primarily circular-LEO, impulsive
    // LVLH rendezvous request into a provenance-labeled specification
    // before any solver is used."), extended with this tool's structural
    // contract.
    description:
      "Formalize only a two-spacecraft, primarily circular-LEO, impulsive LVLH rendezvous request into a " +
      "provenance-labeled specification before any solver is used. Validates and renders a provenance-labeled " +
      "formalization into the Scope/Participants/Reference-Orbit/Relative-Frame-and-State/Terminal-Conditions/" +
      "Timing-and-Maneuvers/Blocking-Issues/Clarification-Questions/Readiness/Formalization-Summary schema the " +
      "retired orbital-problem-formalizer skill defined. The caller must already have reasoned each field's " +
      "value and provenance label (specified/derived/assumed/missing/ambiguous/contradictory/unit-inconsistent/" +
      "out of scope) from the natural-language request; this tool enforces the provenance vocabulary, checks " +
      "Readiness/Blocking-Issues/Clarification-Questions consistency, and formats the required " +
      "Markdown-equivalent output -- it does not parse free text or choose labels itself.",
    promptSnippet: "Formalize a two-spacecraft LVLH rendezvous request into a provenance-labeled specification",
    promptGuidelines: [
      "Use formalize_rendezvous_problem as the first step of the rendezvous pipeline, before any model " +
        "selection or solver call, instead of applying the retired orbital-problem-formalizer skill's " +
        "free-form instructions.",
      "Before calling formalize_rendezvous_problem, reason over the request yourself and fill in each field's " +
        "value and provenance label; formalize_rendezvous_problem only validates structure and renders output, " +
        "it does not do that reasoning for you.",
      "If formalize_rendezvous_problem reports readiness 'OUT OF SCOPE' or 'NEEDS CLARIFICATION', halt the " +
        "rendezvous pipeline there and surface its Blocking Issues/Clarification Questions instead of " +
        "proceeding to model selection.",
    ],
    parameters: formalizeRendezvousProblemSchema,

    async execute(_toolCallId, params) {
      const input = toFormalizationInput(params as Record<string, any>);
      const result = validateFormalization(input);

      if (!result.valid) {
        return {
          content: [
            {
              type: "text" as const,
              text: `formalize_rendezvous_problem input error:\n${result.errors.map((e) => `- ${e}`).join("\n")}`,
            },
          ],
          details: { errors: result.errors },
          isError: true,
        };
      }

      return {
        content: [{ type: "text" as const, text: result.markdown }],
        details: { markdown: result.markdown },
        structuredContent: { markdown: result.markdown, readiness: input.readiness },
        isError: false,
      };
    },
  });
}
