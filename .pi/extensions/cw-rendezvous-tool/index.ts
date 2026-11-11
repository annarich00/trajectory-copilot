/**
 * solve_cw_rendezvous pi tool (TJC-23.4)
 *
 * Converts the retired `.pi/skills/orbital-targeting-planner/SKILL.md`'s
 * deterministic CW two-impulse targeting handoff into a registered,
 * LLM-callable pi tool that wraps `src/cw.py`'s `mean_motion` and
 * `two_burn_targeting` the same way `run_gmat_verification`
 * (`.pi/extensions/gmat-verification-tool`) wraps GMAT execution. This tool
 * is a THIN wrapper: it shells out (via `pi.exec`) to
 * `scripts/cw_rendezvous_tool_bridge.py`, which calls straight into the
 * already-audited `src/cw.py::mean_motion`/`two_burn_targeting`. No CW
 * physics, retiming, or least-squares approximation logic is reimplemented
 * here in TypeScript.
 *
 * The tool's input schema requires the same structured inputs the retired
 * skill documented: a reference radius or mean motion, mu, an explicit
 * LVLH/RIC convention confirmation, initial/terminal relative states (SI
 * units, 6-vectors), a fixed positive transfer duration, and a
 * model-selection note recording that CW's assumptions were checked. No
 * free-text request field exists on this schema at all.
 *
 * `CWSingularTransferError` and an infeasible singular boundary condition
 * are both surfaced as a structured rejection (`feasible: false`, no
 * fabricated `dv0_mps`/`dv1_mps`/`final_state`), never approximated with a
 * least-squares substitute -- mirroring the retired skill's explicit "treat
 * CWSingularTransferError as a rejected transfer time, not a reason to
 * approximate" instruction, now enforced by this tool's structured output
 * instead of relying on the LLM to honor that instruction itself.
 */
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { existsSync } from "node:fs";
import { join, resolve } from "node:path";
import { Type } from "typebox";

const sixVectorSchema = (description: string) =>
  Type.Array(Type.Number(), { minItems: 6, maxItems: 6, description });

const solveCwRendezvousSchema = Type.Object({
  mu_m3_s2: Type.Number({ description: "Central-body gravitational parameter, m^3/s^2 (e.g. Earth's mu)." }),
  reference_radius_m: Type.Optional(Type.Number({
    description: "Chief/reference circular-orbit radius, m. Provide exactly one of reference_radius_m or mean_motion_rad_s.",
  })),
  mean_motion_rad_s: Type.Optional(Type.Number({
    description: "Chief/reference circular-orbit mean motion, rad/s. Provide exactly one of reference_radius_m or mean_motion_rad_s.",
  })),
  lvlh_convention_confirmed: Type.Boolean({
    description:
      "Must be true: explicit confirmation of the right-handed LVLH/RIC convention -- x radial outward, " +
      "y along-track in the chief's direction of motion, z cross-track/orbit-normal -- matching src/cw.py's " +
      "convention. Never assumed; the caller must confirm it explicitly.",
  }),
  initial_relative_state: sixVectorSchema(
    "Initial LVLH relative state [x, y, z, x_dot, y_dot, z_dot] in SI units (m, m/s), matching src/cw.py's convention.",
  ),
  final_relative_state: sixVectorSchema(
    "Terminal/target LVLH relative state [x, y, z, x_dot, y_dot, z_dot] in SI units (m, m/s).",
  ),
  transfer_time_s: Type.Number({ description: "Fixed, positive two-impulse transfer duration, seconds." }),
  model_selection_note: Type.String({
    description:
      "Assumption-based model-selection evidence that CW's assumptions were checked: circularity, " +
      "locality/separation relative to reference radius, duration/regime, frame, negligible perturbations, " +
      "and impulsive-burn suitability. Must be non-empty.",
  }),
});

/** Locate the project's own `.venv` Python, falling back to a bare `python3`
 * on PATH when no project-local venv exists. Mirrors
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
    name: "solve_cw_rendezvous",
    label: "Solve CW Rendezvous",
    description:
      "Solve a fully specified, assumption-qualified fixed-duration two-impulse Clohessy-Wiltshire rendezvous " +
      "using src/cw.py's deterministic mean_motion/two_burn_targeting (the same implementation the retired " +
      ".pi/skills/orbital-targeting-planner/SKILL.md documented). Returns the two impulses and final state for a " +
      "feasible solve, or a structured rejection -- never a least-squares approximation -- when the transfer " +
      "time is singular/unreachable.",
    promptSnippet: "Solve a structured fixed-duration CW two-impulse rendezvous case",
    promptGuidelines: [
      "Use solve_cw_rendezvous only after problem formalization and assumption-based model selection have " +
        "established that the case is a local circular-chief relative-motion problem.",
      "solve_cw_rendezvous requires the same structured mu/reference-radius-or-mean-motion/LVLH-convention-" +
        "confirmation/initial-and-final-relative-state/transfer-time/model-selection-note fields the retired " +
        "orbital-targeting-planner skill documented -- never call it with a free-text description instead.",
      "Do not invent any missing input or coordinate convention; if a required field is unknown, obtain it " +
        "before calling this tool rather than guessing a value.",
      "A feasible result from this tool is a CW candidate only, not a verified result -- hand it to " +
        "run_gmat_verification before reporting PASS.",
    ],
    parameters: solveCwRendezvousSchema,

    async execute(_toolCallId, params, signal, _onUpdate, ctx) {
      const projectRoot = ctx.cwd;
      const bridgeScript = resolve(projectRoot, "scripts", "cw_rendezvous_tool_bridge.py");
      if (!existsSync(bridgeScript)) {
        throw new Error(
          `solve_cw_rendezvous's bridge script is missing: ${bridgeScript}. Expected ` +
            "scripts/cw_rendezvous_tool_bridge.py to exist.",
        );
      }
      const pythonExecutable = resolvePythonExecutable(projectRoot);

      // pi.exec() has no stdin option (it runs without a shell, argv only),
      // so the structured case is passed as a single --case-json argument
      // instead of over stdin; scripts/cw_rendezvous_tool_bridge.py accepts
      // either, mirroring scripts/gmat_tool_bridge.py's identical choice.
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
          `solve_cw_rendezvous's bridge script did not return valid JSON (exit ${result.code}): ` +
            `${error instanceof Error ? error.message : String(error)}\nstdout: ${stdout}\nstderr: ${stderr}`,
        );
      }

      if (parsed !== null && typeof parsed === "object" && "error" in (parsed as Record<string, unknown>)) {
        // A tool-input validation error from the bridge script itself (e.g.
        // a missing required field or an unconfirmed LVLH convention) --
        // distinct from a CW targeting rejection, and never reported as a
        // feasible result.
        return {
          content: [{ type: "text" as const, text: `solve_cw_rendezvous input error: ${(parsed as any).error}` }],
          details: parsed,
          isError: true,
        };
      }

      const resultRecord = parsed as Record<string, unknown>;
      const feasible = resultRecord.feasible === true;
      const status = resultRecord.status ?? "UNKNOWN";
      const reason = resultRecord.reason ?? null;

      return {
        content: [
          {
            type: "text" as const,
            text:
              `CW rendezvous solve: status=${status} feasible=${feasible}\n` +
              (reason ? `reason=${reason}\n` : "") +
              JSON.stringify(parsed, null, 2),
          },
        ],
        details: parsed,
        structuredContent: parsed,
        isError: !feasible,
      };
    },
  });
}
