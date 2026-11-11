/**
 * propagate_two_body_coast pi tool (TJC-23.5)
 *
 * Registers `.pi/skills/orbital-two-body-rendezvous/SKILL.md`'s bounded
 * deterministic inertial Cartesian point-mass two-body coast fallback as an
 * explicit, LLM-callable pi tool instead of free-form skill instructions.
 * This tool is a THIN wrapper: it shells out (via `pi.exec`) to
 * `scripts/two_body_tool_bridge.py`, which itself calls straight into the
 * already-audited `src/twobody.py::propagate_cartesian_state`. No
 * propagation, validation, or singularity-handling logic is reimplemented
 * here in TypeScript, mirroring `.pi/extensions/gmat-verification-tool`'s
 * pattern exactly.
 *
 * The tool's input schema requires the same structured fields the retired
 * skill documented: an initial SI inertial Cartesian state
 * `[x, y, z, vx, vy, vz]`, a positive `mu`, a finite coast duration, and a
 * positive fixed RK4 step count, plus an optional epoch (AC1). Non-finite
 * inputs, non-positive mu/steps, and the zero-radius point-mass singularity
 * are rejected by the bridge script's `ValueError` propagation -- never
 * improvised into a fabricated result (AC2).
 *
 * The tool's output relays the bridge script's stdout JSON verbatim
 * (parsed and re-serialized, not reinterpreted): the final SI inertial
 * Cartesian state plus the stable `frame="inertial-cartesian"`,
 * `central_body="Earth"`, `dynamics="point-mass-two-body"`,
 * `integrator="fixed-step-rk4"` metadata `src/twobody.py::TwoBodyCase`
 * already defines.
 */
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { existsSync } from "node:fs";
import { join, resolve } from "node:path";
import { Type } from "typebox";

const propagateTwoBodyCoastSchema = Type.Object({
  initial_state_m_mps: Type.Array(Type.Number(), {
    minItems: 6, maxItems: 6,
    description: "Initial inertial Cartesian state [x, y, z, vx, vy, vz] in SI units (position in m, velocity in m/s).",
  }),
  mu_m3_s2: Type.Number({ description: "Positive central-body gravitational parameter, m^3/s^2." }),
  duration_s: Type.Number({ description: "Finite coast duration, seconds. May be negative to propagate backward." }),
  steps: Type.Integer({ description: "Positive fixed RK4 step count.", minimum: 1 }),
  epoch: Type.Optional(Type.String({ description: "Optional epoch accompanying the case, for external verification only; not used in propagation." })),
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
    name: "propagate_two_body_coast",
    label: "Propagate Two-Body Coast",
    description:
      "Propagate one supplied SI inertial Cartesian state through a bounded, deterministic point-mass " +
      "two-body coast arc (src/twobody.py::propagate_cartesian_state via a fixed-step RK4 integrator) and " +
      "return the final state in the same frame. This is coast propagation only: it does not target " +
      "rendezvous, plan maneuvers, optimize a trajectory, or model perturbations (J2, drag, third bodies, " +
      "solar radiation pressure, thrust). Non-finite inputs, non-positive mu/steps, and the zero-radius " +
      "point-mass singularity are rejected explicitly, never improvised into a result.",
    promptSnippet: "Propagate a bounded SI inertial Cartesian two-body coast arc",
    promptGuidelines: [
      "Use propagate_two_body_coast only for the bounded deterministic point-mass coast fallback -- after " +
        "the model selector has rejected or not selected CW for the stated assumptions.",
      "propagate_two_body_coast requires the same structured initial_state_m_mps/mu_m3_s2/duration_s/steps " +
        "fields the retired orbital-two-body-rendezvous skill documented -- never call it with a free-text " +
        "description instead of those fields.",
      "propagate_two_body_coast does not solve rendezvous targeting, select maneuvers, or model " +
        "perturbations; treat those requests as unsupported rather than asking this tool to improvise them.",
    ],
    parameters: propagateTwoBodyCoastSchema,

    async execute(_toolCallId, params, signal, _onUpdate, ctx) {
      const projectRoot = ctx.cwd;
      const bridgeScript = resolve(projectRoot, "scripts", "two_body_tool_bridge.py");
      if (!existsSync(bridgeScript)) {
        throw new Error(
          `propagate_two_body_coast's bridge script is missing: ${bridgeScript}. Expected ` +
            "scripts/two_body_tool_bridge.py to exist alongside src/twobody.py.",
        );
      }
      const pythonExecutable = resolvePythonExecutable(projectRoot);

      // pi.exec() has no stdin option (it runs without a shell, argv only),
      // so the structured case is passed as a single --case-json argument
      // instead of over stdin; scripts/two_body_tool_bridge.py accepts
      // either, mirroring scripts/gmat_tool_bridge.py.
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
          `propagate_two_body_coast's bridge script did not return valid JSON (exit ${result.code}): ` +
            `${error instanceof Error ? error.message : String(error)}\nstdout: ${stdout}\nstderr: ${stderr}`,
        );
      }

      if (parsed !== null && typeof parsed === "object" && "error" in (parsed as Record<string, unknown>)) {
        // A structured rejection from the bridge script -- a non-finite
        // input, non-positive mu/steps, or the zero-radius singularity
        // (AC2), relayed as an explicit tool error rather than an
        // improvised propagation result.
        return {
          content: [{ type: "text" as const, text: `propagate_two_body_coast rejected the input: ${(parsed as any).error}` }],
          details: parsed,
          isError: true,
        };
      }

      const resultRecord = parsed as Record<string, unknown>;

      return {
        content: [
          {
            type: "text" as const,
            text:
              `Two-body coast propagation complete.\n` +
              `final_state_m_mps=${JSON.stringify(resultRecord.final_state_m_mps)}\n` +
              `frame=${resultRecord.frame} central_body=${resultRecord.central_body} ` +
              `dynamics=${resultRecord.dynamics} integrator=${resultRecord.integrator}\n\n` +
              JSON.stringify(parsed, null, 2),
          },
        ],
        details: parsed,
        structuredContent: parsed,
        isError: false,
      };
    },
  });
}
