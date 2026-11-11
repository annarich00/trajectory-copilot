/**
 * select_rendezvous_model pi tool (TJC-23.3)
 *
 * Converts the retired `.pi/skills/orbital-model-selector/SKILL.md`'s
 * six-item assumption assessment and four-way CW/bounded-two-body/
 * UNSUPPORTED/NEEDS-MORE-INFORMATION selection into a registered,
 * LLM-callable pi tool, mirroring `solve_cw_rendezvous`
 * (`.pi/extensions/cw-rendezvous-tool/index.ts`) and
 * `formalize_rendezvous_problem`
 * (`.pi/extensions/orbital-problem-formalizer-tool/index.ts`)'s identical
 * pattern: a thin TypeScript wrapper that shells out (via `pi.exec`) to
 * `scripts/model_selector_tool_bridge.py`, which calls straight into the
 * already-audited `src/model_selector.py::ModelSelectionCase`/
 * `select_model`. No assumption-combination logic, numeric heuristic, or
 * selection rule is reimplemented here in TypeScript.
 *
 * Deciding each of the six required assumption items' ('supported'/
 * 'violated'/'boundary'/'unknown') value from the `formalize_rendezvous_problem`
 * tool's structured output (or from a natural-language request directly)
 * is itself LLM judgment -- the same judgment the retired SKILL.md asked an
 * agent to apply free-form. This tool does NOT parse Markdown or infer an
 * assessment itself: the calling LLM must reason over the formalizer's
 * output (and any other available case information) and supply its own
 * already-reasoned six-item assessment (plus the optional supporting
 * numeric/state fields `src/model_selector.py` can compute some signals
 * from) as this tool's structured input. The tool's job is strictly the
 * deterministic combination step `select_model` already performs: given
 * those assessments, decide `CW rendezvous`, `bounded two-body fallback`,
 * `UNSUPPORTED`, or `NEEDS MORE INFORMATION`, and name the deterministic
 * implementation handoff.
 */
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { StringEnum } from "@earendil-works/pi-ai";
import { existsSync } from "node:fs";
import { join, resolve } from "node:path";
import { Type } from "typebox";

const assessmentSchema = (item: string) =>
  StringEnum(["supported", "violated", "boundary", "unknown"] as const, {
    description: `Required assumption item '${item}': 'supported', 'violated', 'boundary', or 'unknown'. ` +
      "Must already be reasoned by the caller from the formalizer's output or other case information -- " +
      "this tool does not infer it from free text.",
  });

const optionalAssessmentSchema = (item: string, computableFrom: string) =>
  Type.Optional(
    StringEnum(["supported", "violated", "boundary", "unknown"] as const, {
      description: `Optional '${item}' assumption item: 'supported', 'violated', 'boundary', or 'unknown'. ` +
        `When omitted, computed from ${computableFrom} using src/cw.py's existing heuristics; an explicit ` +
        "value here always takes priority over a computed one.",
    }),
  );

const sixVectorSchema = (description: string) =>
  Type.Optional(Type.Array(Type.Number(), { minItems: 6, maxItems: 6, description }));

const selectRendezvousModelSchema = Type.Object({
  // 1. Circularity -- not numerically derivable; must be stated.
  circularity: assessmentSchema("circularity"),
  // 4. Frame / LVLH-RIC convention and state ordering -- not numerically derivable; must be stated.
  frame: assessmentSchema("frame"),
  // 5. Other physics: central-body dominance, negligible perturbations, small relative velocity.
  other_physics: assessmentSchema("other_physics"),
  // 6. Maneuver assumptions (impulsive-burn suitability).
  maneuver_assumptions: assessmentSchema("maneuver_assumptions"),

  // 2. Locality / separation vs. reference-orbit radius -- supply directly or via the numeric fields below.
  locality: optionalAssessmentSchema("locality", "reference_radius_m and relative_separation_m"),
  reference_radius_m: Type.Optional(Type.Number({
    description: "Chief/reference circular-orbit radius, m. Used to compute 'locality' when it is omitted.",
  })),
  relative_separation_m: Type.Optional(Type.Number({
    description: "Relative separation magnitude, m. Used to compute 'locality' when it is omitted.",
  })),

  // 3. Duration / regime -- supply directly or via the numeric fields below.
  duration_regime: optionalAssessmentSchema("duration_regime", "transfer_time_s and mean_motion_rad_s"),
  transfer_time_s: Type.Optional(Type.Number({
    description: "Fixed transfer duration, seconds. Used to compute 'duration_regime' and, together with " +
      "the relative-state fields below, the optional targeting_conditioning signal.",
  })),
  mean_motion_rad_s: Type.Optional(Type.Number({
    description: "Chief/reference circular-orbit mean motion, rad/s. Used to compute 'duration_regime' and " +
      "the optional targeting_conditioning signal.",
  })),

  // Optional 7th signal: CW two-impulse targeting conditioning.
  targeting_conditioning: optionalAssessmentSchema(
    "targeting_conditioning",
    "initial_relative_state, final_relative_state, transfer_time_s, and mean_motion_rad_s",
  ),
  initial_relative_state: sixVectorSchema(
    "Initial LVLH relative state [x, y, z, x_dot, y_dot, z_dot] in SI units. Used, with transfer_time_s and " +
      "mean_motion_rad_s, to compute the optional targeting_conditioning signal via src/cw.py's two_burn_targeting.",
  ),
  final_relative_state: sixVectorSchema(
    "Terminal/target LVLH relative state [x, y, z, x_dot, y_dot, z_dot] in SI units, for the optional " +
      "targeting_conditioning signal.",
  ),

  // Bounded two-body coast contract fields (src/twobody.py), used only to decide whether a CW-rejected case
  // may be routed to the fallback.
  inertial_cartesian_state: sixVectorSchema(
    "Six-element inertial Cartesian state [x, y, z, vx, vy, vz] in SI units, for the bounded two-body coast " +
      "contract check.",
  ),
  mu_m3_s2: Type.Optional(Type.Number({ description: "Central-body gravitational parameter, m^3/s^2, for the bounded two-body coast contract check." })),
  coast_duration_s: Type.Optional(Type.Number({ description: "Finite coast duration, seconds, for the bounded two-body coast contract check." })),
  rk4_steps: Type.Optional(Type.Integer({ description: "Positive fixed RK4 step count, for the bounded two-body coast contract check." })),
  is_coast_only_request: Type.Optional(Type.Boolean({
    description: "Whether the request is coast-only (no targeting/burns/optimization). Defaults to true.",
  })),

  notes: Type.Optional(Type.String({ description: "Free-text supporting notes, recorded verbatim." })),
});

/** Locate the project's own `.venv` Python, falling back to a bare `python3`
 * on PATH when no project-local venv exists. Mirrors
 * `.pi/extensions/cw-rendezvous-tool/index.ts`'s/
 * `.pi/extensions/gmat-verification-tool/index.ts`'s identical helper and
 * this repo's documented `.venv/bin/python` convention (see README.md's
 * "Reproducible setup").
 */
function resolvePythonExecutable(projectRoot: string): string {
  const venvPython = join(projectRoot, ".venv", "bin", "python");
  return existsSync(venvPython) ? venvPython : "python3";
}

export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "select_rendezvous_model",
    label: "Select Rendezvous Model",
    description:
      "Select which scoped deterministic model applies to a formalized rendezvous case -- `CW rendezvous` " +
      "(src/cw.py's fixed-duration local two-impulse targeting), `bounded two-body fallback` (src/twobody.py's " +
      "inertial Cartesian point-mass coast propagation), `UNSUPPORTED`, or `NEEDS MORE INFORMATION` -- using " +
      "src/model_selector.py's deterministic assumption-combination logic (the same combination the retired " +
      ".pi/skills/orbital-model-selector/SKILL.md documented). Never a learned or universal numeric threshold: " +
      "the selection rests on the six required assumption items (circularity, locality, duration/regime, " +
      "frame, other physics, maneuver assumptions) plus the optional targeting-conditioning signal.",
    promptSnippet: "Select the CW/bounded-two-body/UNSUPPORTED/NEEDS-MORE-INFORMATION model for a formalized rendezvous case",
    promptGuidelines: [
      "Use select_rendezvous_model only after formalize_rendezvous_problem has produced a READY TO SOLVE (or " +
        "the documented single-spacecraft-coast OUT OF SCOPE exception) case, to decide which deterministic " +
        "solver applies.",
      "Before calling select_rendezvous_model, reason over the formalizer's output yourself and assess each " +
        "of the six required items ('supported'/'violated'/'boundary'/'unknown'); this tool does not parse " +
        "Markdown or infer an assessment itself -- it only combines the assessments you supply.",
      "Do not declare a required item 'supported' from a single fixed percentage, orbit count, or learned " +
        "threshold; src/cw.py's validate_cw_use heuristics (used by this tool's optional computed " +
        "locality/duration_regime signals) are limited deterministic warnings, not a replacement for your " +
        "own documented assessment.",
      "A `CW rendezvous` or `bounded two-body fallback` selection from this tool is a model choice only, not a " +
        "verified result -- hand the selected case to solve_cw_rendezvous or the bounded-two-body path, then " +
        "to run_gmat_verification, before reporting PASS.",
    ],
    parameters: selectRendezvousModelSchema,

    async execute(_toolCallId, params, signal, _onUpdate, ctx) {
      const projectRoot = ctx.cwd;
      const bridgeScript = resolve(projectRoot, "scripts", "model_selector_tool_bridge.py");
      if (!existsSync(bridgeScript)) {
        throw new Error(
          `select_rendezvous_model's bridge script is missing: ${bridgeScript}. Expected ` +
            "scripts/model_selector_tool_bridge.py to exist.",
        );
      }
      const pythonExecutable = resolvePythonExecutable(projectRoot);

      // pi.exec() has no stdin option (it runs without a shell, argv only),
      // so the structured case is passed as a single --case-json argument
      // instead of over stdin; scripts/model_selector_tool_bridge.py accepts
      // either, mirroring scripts/cw_rendezvous_tool_bridge.py's/
      // scripts/gmat_tool_bridge.py's identical choice.
      const caseJson = JSON.stringify(params);
      const result = await pi.exec(pythonExecutable, [bridgeScript, "--case-json", caseJson], {
        cwd: projectRoot,
        signal,
        timeout: 60_000,
      });

      const stdout = result.stdout ?? "";
      const stderr = result.stderr ?? "";
      let parsed: unknown;
      try {
        parsed = JSON.parse(stdout);
      } catch (error) {
        throw new Error(
          `select_rendezvous_model's bridge script did not return valid JSON (exit ${result.code}): ` +
            `${error instanceof Error ? error.message : String(error)}\nstdout: ${stdout}\nstderr: ${stderr}`,
        );
      }

      if (parsed !== null && typeof parsed === "object" && "error" in (parsed as Record<string, unknown>)) {
        // A tool-input validation error from the bridge script itself (e.g.
        // an unrecognized field or an illegal assessment literal) --
        // distinct from any of the four selection outcomes, and never
        // reported as a selection result.
        return {
          content: [{ type: "text" as const, text: `select_rendezvous_model input error: ${(parsed as any).error}` }],
          details: parsed,
          isError: true,
        };
      }

      const resultRecord = parsed as Record<string, unknown>;
      const selection = resultRecord.selection ?? "UNKNOWN";
      const qualified = resultRecord.qualified === true;
      const modelSelected = selection === "CW rendezvous" || selection === "bounded two-body fallback";

      return {
        content: [
          {
            type: "text" as const,
            text:
              `Model selection: ${selection}${qualified ? " (qualified)" : ""}\n` +
              JSON.stringify(parsed, null, 2),
          },
        ],
        details: parsed,
        structuredContent: parsed,
        isError: !modelSelected,
      };
    },
  });
}
