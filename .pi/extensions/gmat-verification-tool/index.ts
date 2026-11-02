/**
 * run_gmat_verification pi tool (TJC-12)
 *
 * Registers GMAT execution/parsing/comparison as an explicit, LLM-callable
 * pi tool instead of it only happening invisibly inside
 * `src/workflow.py::run_rendezvous_workflow`. This tool is a THIN wrapper:
 * it shells out (via `pi.exec`) to `scripts/gmat_tool_bridge.py`, which
 * itself calls straight into the already-audited
 * `scripts/run_cw_gmat_slice.py::run_cw_rendezvous_gmat_verification` core
 * (the exact same function `src/workflow.py::_run_cw_path` calls) and
 * `src/verification_report.py`'s `UnifiedVerificationReport`. No GMAT
 * script generation, execution, parsing, or comparison logic is
 * reimplemented here in TypeScript, and `src/workflow.py::
 * run_rendezvous_workflow` itself is never modified or called by this tool
 * -- this is strictly an additive, parallel entry point (AC4).
 *
 * The tool's input schema requires the same structured case-identity and
 * tolerance fields `src/workflow.py::RendezvousCase`'s CW path already
 * requires (AC2): no free-text request field exists on this schema at all.
 *
 * The tool's output is the bridge script's stdout JSON relayed verbatim
 * (parsed and re-serialized, not reinterpreted): `verified`,
 * `verification_status`, `failure_mode`, and the embedded
 * `unified_verification_report.comparison.status` keep exactly the
 * PASS/WARNING/FAIL/INCOMPLETE and MISSING_GMAT/EXECUTION_ERROR/
 * MALFORMED_OUTPUT/NUMERICAL_DISAGREEMENT/SCREENSHOT_FAILURE/
 * CW_TARGETING_INFEASIBLE vocabulary `src/gmat_verify.py`/
 * `src/verification_report.py` already define (AC3). This tool never sets
 * `verified: true` itself and never overrides a failure_mode it receives
 * from the bridge script -- there is no new silent-PASS path.
 */
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { existsSync } from "node:fs";
import { join, resolve } from "node:path";
import { Type } from "typebox";

const runGmatVerificationSchema = Type.Object({
  case_id: Type.String({ description: "Unique identifier for this rendezvous case (used in the GMAT run ID and artifacts)." }),
  mu_m3_s2: Type.Number({ description: "Central-body gravitational parameter, m^3/s^2 (e.g. Earth's mu)." }),
  reference_radius_m: Type.Number({ description: "Chief/reference circular-orbit radius, m." }),
  initial_relative_state: Type.Array(Type.Number(), {
    minItems: 6, maxItems: 6,
    description: "Pre-burn-1 LVLH relative state [x, y, z, x_dot, y_dot, z_dot] in SI units (m, m/s), matching src/cw.py's convention.",
  }),
  final_relative_state: Type.Optional(Type.Array(Type.Number(), {
    minItems: 6, maxItems: 6,
    description: "Target LVLH relative state [x, y, z, x_dot, y_dot, z_dot] in SI units. Defaults to the zero vector (rendezvous at the chief) when omitted.",
  })),
  transfer_time_s: Type.Number({ description: "Fixed two-impulse transfer duration, seconds." }),
  pos_tol_m: Type.Optional(Type.Number({ description: "Position comparison tolerance, m. Defaults to 1.0." })),
  vel_tol_mps: Type.Optional(Type.Number({ description: "Velocity comparison tolerance, m/s. Defaults to 0.001." })),
  dv_tol_mps: Type.Optional(Type.Number({ description: "Delta-v tolerance, m/s (recorded alongside the comparison; not itself compared). Defaults to 0.001." })),
  output_dir: Type.Optional(Type.String({ description: "Directory for the generated GMAT script, ReportFile output, and screenshot artifacts. Defaults to a fresh temp directory if omitted." })),
  gmat_executable: Type.Optional(Type.String({ description: "Console-mode GMAT executable for numeric verification. Defaults to 'GmatConsole-R2026a'." })),
  gmat_gui_executable: Type.Optional(Type.String({ description: "GUI-mode GMAT executable for the optional screenshot attempt. Defaults to 'GMAT-R2026a'." })),
  attempt_gui_screenshot: Type.Optional(Type.Boolean({ description: "Attempt a real GMAT GUI (OrbitView/OpenFrames) screenshot before falling back to the deterministic SVG plot. Defaults to false (off) for this tool." })),
});

/** Locate the project's own `.venv` Python, falling back to a bare `python3`
 * on PATH when no project-local venv exists (e.g. a different checkout
 * that relies on a system/managed interpreter with the required deps
 * already installed). Mirrors this repo's documented `.venv/bin/python`
 * convention (see README.md's "Reproducible setup").
 */
function resolvePythonExecutable(projectRoot: string): string {
  const venvPython = join(projectRoot, ".venv", "bin", "python");
  return existsSync(venvPython) ? venvPython : "python3";
}

export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "run_gmat_verification",
    label: "Run GMAT Verification",
    description:
      "Run the CW rendezvous case through GMAT's independent numerical verification " +
      "(src/gmat_verify.py's execution/parsing/comparison pipeline, via scripts/run_cw_gmat_slice.py's " +
      "reusable core) and return its PASS/WARNING/FAIL/INCOMPLETE comparison status plus any " +
      "MISSING_GMAT/EXECUTION_ERROR/MALFORMED_OUTPUT/NUMERICAL_DISAGREEMENT/SCREENSHOT_FAILURE/" +
      "CW_TARGETING_INFEASIBLE failure mode. This makes the previously-invisible GMAT execution step " +
      "an explicit, auditable tool call instead of it only happening inside src/workflow.py.",
    promptSnippet: "Run GMAT's independent numerical verification for a structured CW rendezvous case",
    promptGuidelines: [
      "Use run_gmat_verification to independently verify a CW rendezvous case's candidate solution with GMAT, " +
        "instead of treating a solver success alone as verified.",
      "run_gmat_verification requires the same structured case_id/mu_m3_s2/reference_radius_m/" +
        "initial_relative_state/transfer_time_s/tolerance fields src/workflow.py::RendezvousCase already " +
        "requires -- never call it with a free-text description instead of those fields.",
    ],
    parameters: runGmatVerificationSchema,

    async execute(_toolCallId, params, signal, _onUpdate, ctx) {
      const projectRoot = ctx.cwd;
      const bridgeScript = resolve(projectRoot, "scripts", "gmat_tool_bridge.py");
      if (!existsSync(bridgeScript)) {
        throw new Error(
          `run_gmat_verification's bridge script is missing: ${bridgeScript}. Expected ` +
            "scripts/gmat_tool_bridge.py to exist alongside scripts/run_cw_gmat_slice.py.",
        );
      }
      const pythonExecutable = resolvePythonExecutable(projectRoot);

      // pi.exec() has no stdin option (it runs without a shell, argv only),
      // so the structured case is passed as a single --case-json argument
      // instead of over stdin; scripts/gmat_tool_bridge.py accepts either.
      const caseJson = JSON.stringify(params);
      const result = await pi.exec(pythonExecutable, [bridgeScript, "--case-json", caseJson], {
        cwd: projectRoot,
        signal,
        timeout: 200_000,
      });

      const stdout = result.stdout ?? "";
      const stderr = result.stderr ?? "";
      let parsed: unknown;
      try {
        parsed = JSON.parse(stdout);
      } catch (error) {
        throw new Error(
          `run_gmat_verification's bridge script did not return valid JSON (exit ${result.code}): ` +
            `${error instanceof Error ? error.message : String(error)}\nstdout: ${stdout}\nstderr: ${stderr}`,
        );
      }

      if (parsed !== null && typeof parsed === "object" && "error" in (parsed as Record<string, unknown>)) {
        // A tool-input validation error from the bridge script itself (e.g.
        // a missing required field) -- distinct from any GMAT failure mode,
        // and never reported as a verified result.
        return {
          content: [{ type: "text" as const, text: `run_gmat_verification input error: ${(parsed as any).error}` }],
          details: parsed,
          isError: true,
        };
      }

      const resultRecord = parsed as Record<string, unknown>;
      const verified = resultRecord.verified === true;
      const failureMode = resultRecord.failure_mode ?? null;
      const verificationStatus = resultRecord.verification_status ?? "UNKNOWN";

      return {
        content: [
          {
            type: "text" as const,
            text:
              `GMAT verification for case '${(params as any).case_id}': ${verificationStatus}\n` +
              `verified=${verified} failure_mode=${failureMode}\n\n` +
              JSON.stringify(parsed, null, 2),
          },
        ],
        details: parsed,
        structuredContent: parsed,
        isError: !verified,
      };
    },
  });
}
