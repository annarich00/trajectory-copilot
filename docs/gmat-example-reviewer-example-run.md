# GMAT-example reviewer subagent: definition and documented example run (TJC-14)

`.pi/agents/gmat-example-reviewer.md` is a project-local pi-subagents agent
(discoverable with `agentScope: "project"` or `"both"`). It reviews a
project-generated GMAT script's **formatting, structure and conventions**
against the open-source example corpus
`research/gmat_example_corpus/corpus.json` (TJC-11, schema 1.0.0). It is
**not** a numerical or screenshot verifier: `.pi/skills/gmat-rendezvous-verification/SKILL.md`
remains the sole source of PASS/FAIL numerical truth. It is read-only
(`tools: read, grep, find, ls`), must cite corpus entry ids, must answer
`NO CORPUS ENTRY` instead of fabricating a comparison, and returns a short
`SATISFACTORY | DIVERGENT | NO CORPUS ENTRY` verdict block. It is
wired into the rendezvous workflow by TJC-15 as an advisory, non-blocking step
(`.pi/prompts/rendezvous.md` step 4; worked example in
`docs/rendezvous-gmat-example-review-worked-example.md`).

Static guard: `tests/test_gmat_example_reviewer_agent.py` checks the agent file
(frontmatter, read-only tools, scope and non-verification statements, corpus
path, citation rule, no-entry rule, verdict format).

## How the example run below was produced (honest provenance)

* **Reviewed script.** `examples/cw_gmat_slice_example/generated_cw_rendezvous.script`
  was produced by a real run of `scripts/run_cw_gmat_slice.py` on
  `examples/cw_gmat_vertical_slice.yaml` (calls
  `src/gmat_verify.py::generate_gmat_script`; GMAT verified that case,
  position error 7.9e-3 m). It was written with `--output-dir /tmp/tjc14_run`,
  so its `ReportFile` paths point at that scratch directory; the file is
  otherwise byte-for-byte generator output. It is committed here because the
  directory previously contained only the result JSON and screenshot.
* **Reviewer runs.** These are **real model runs, but not through the
  `subagent` tool**. The headless `pi -p` session used here did not expose a
  `subagent` tool, so the agent's definition was exercised directly: the
  Markdown body of `gmat-example-reviewer.md` (frontmatter stripped) was passed
  as the system prompt, with the agent's own tool allowlist, using the
  session's default model (`MIT-parley` `openai/gpt-5.4-mini`):

  ```
  pi -p --no-session --no-context-files --no-skills --no-prompt-templates \
     --system-prompt "<agent file body after the closing --- of the frontmatter>" \
     --tools read,grep,find,ls "<task>"
  ```

  Frontmatter-driven behaviour (project-scope discovery, `systemPromptMode`,
  `inheritProjectContext: false`) was therefore not exercised, and the output
  is a single LLM sample (not deterministic). The text blocks below are the
  verbatim outputs (only pi's unrelated "No models match pattern" startup
  warnings were removed).

## Run A: the actual request type (CW rendezvous), no matching corpus mission type

Task given: "Review the generated GMAT script
examples/cw_gmat_slice_example/generated_cw_rendezvous.script. Mission type of
the original user request: two-spacecraft Clohessy-Wiltshire (CW) LVLH-relative
rendezvous between a chief and a deputy."

```
GMAT example review (format/structure/convention only; not numerical or screenshot verification)
Verdict: NO CORPUS ENTRY
Script reviewed: examples/cw_gmat_slice_example/generated_cw_rendezvous.script
Mission type: two-spacecraft Clohessy-Wiltshire (CW) LVLH-relative rendezvous between a chief and a deputy
Corpus entries cited: none
Divergences:
- not assessed
Advisory (not a mission-type comparison): corpus mission types present include orbit_transfer, lunar_transfer, lunar_impactor, lunar_swingby, finite_burn_propulsion, electric_propulsion, attitude_pointing, mars_orbit_constellation, station_keeping, leo_propagation, elliptical_orbit_propagation, sso_inclination_study, ground_station_contact, interplanetary_transfer, outer_planet_moon_exploration
Limits: Numerical correctness and trajectory screenshots are verified separately by the gmat-rendezvous-verification contract.
```

The corpus contains no rendezvous / relative-motion entry, so the agent
correctly refused to fabricate a comparison, which is the intended AC #3
behaviour. (A human note: its "Advisory" line only listed the corpus's
vocabulary, not entry-tied convention observations as the prompt allows.)

## Run B: nearest-neighbour comparison (caller supplies `orbit_transfer`)

Task given: same script, "Mission type of the original user request:
orbit_transfer."

```
GMAT example review (format/structure/convention only; not numerical or screenshot verification)
Verdict: DIVERGENT
Script reviewed: examples/cw_gmat_slice_example/generated_cw_rendezvous.script
Mission type: orbit_transfer
Corpus entries cited: nasa-ex_hohmanntransfer, nasa-tut_simpleorbittransfer
Divergences:
- Mission-shape mismatch: corpus orbit-transfer entries center on a transfer-targeting pattern with `Target`/`Vary`/`Achieve` around impulsive burns, while the generated script is a CW rendezvous/coast sequence with direct `Maneuver` and `Propagate` steps and no targeting block [nasa-ex_hohmanntransfer, nasa-tut_simpleorbittransfer]
- Output convention mismatch: cited orbit-transfer entries include mission-oriented visualization/output subscribers (`OpenFramesInterface`, `GroundTrackPlot`) and/or solver reporting, whereas the generated script uses only `ReportFile` records and no plot/view subscriber objects [nasa-ex_hohmanntransfer, nasa-tut_simpleorbittransfer]
Limits: Numerical correctness and trajectory screenshots are verified separately by the gmat-rendezvous-verification contract.
```

Human annotation (not agent output): the cited ids `nasa-ex_hohmanntransfer`
and `nasa-tut_simpleorbittransfer` are real corpus entries with
`mission_type: orbit_transfer` and `redistributable: true`, and the tag-level
claims match their `convention_tags` (both have
`target_vary_achieve_differential_corrector`; only the tutorial has
`groundtrackplot_output`). The "no targeting block" divergence is expected for
this project: the CW solver supplies the burns directly, so it is a
genuine structural difference rather than a defect. The reviewer is shown to
give a sourced, short, structured DIVERGENT verdict, and its `Limits:` line
keeps numerical/screenshot verification with the GMAT verification skill. The
exact wording of the divergences can vary between samples.
