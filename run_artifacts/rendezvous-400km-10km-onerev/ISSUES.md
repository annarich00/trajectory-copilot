# Issues encountered running this rendezvous case

Case: `rendezvous-400km-10km-onerev` (Earth, 400 km circular chief, chaser at
`[0, 10000, 0]` m, one-orbital-period CW two-impulse rendezvous).

## Blocker: TJC-16.5 visualization stages (scene / trajectory / comparison plots)

`scripts/rendezvous_visualization_stage.py` (and `src/workflow.py`'s CW path,
which calls the same `src/workflow_visualization.py` stage functions) import
`src/visualization.py` (needs `plotly`) and
`src/visualization_trajectory.py` / `src/visualization_comparison.py` (need
`matplotlib`). Neither package is installed in this project's `.venv`:

```
ModuleNotFoundError: No module named 'plotly'
ModuleNotFoundError: No module named 'matplotlib'
```

`requirements-dev.txt` pins `plotly==7.1.0`, so installing it is the intended
fix, but installation is not possible from inside this sandbox:

1. `pip install` crashes before even trying to reach the network, because
   pip's vendored `distro` library opens `/etc/debian_version` and
   `/etc/os-release` to build its User-Agent string, and this sandbox user
   does not have read permission on those files (`PermissionError: [Errno 13]
   Permission denied: '/etc/debian_version'`), even though `ls -l` shows them
   as world-readable `644` files owned by `root`.
2. Working around that with `UNIXCONFDIR=<writable copy of /etc>` (a
   documented `pip`/`distro` environment override) gets past the
   `/etc` read, but then the actual package download fails: this sandbox's
   outbound HTTP(S) proxy returns `403 Forbidden: host pypi.org:443 is not
   in the allowlist` (same for `files.pythonhosted.org`). No PyPI mirror or
   local wheel cache for `plotly`/`matplotlib` exists anywhere on this
   machine (checked with `find / -iname "*.whl"` and `find / -iname
   "plotly*"`, excluding this project's own tree).

Net effect: this session cannot produce the (a) 3D relative-position scene,
(b) trajectory/burns plot, or (c) verification comparison plot artifacts
required by step 2/3 of the rendezvous pipeline for this case. These three
stages are reported to the operator as **blocked** (not `not_generated` in
the pipeline's own semantic sense -- that status means "this case's physics
genuinely has nothing to plot"; here the inputs exist but the plotting
libraries are missing and cannot be installed in this sandbox). No plot was
faked or substituted.

This does **not** block the rest of the pipeline: `src/gmat_verify.py`,
`scripts/run_cw_gmat_slice.py`, `scripts/gmat_tool_bridge.py`, and the
`run_gmat_verification` pi tool import neither `plotly` nor `matplotlib`, so
the actual CW solve + independent GMAT numerical verification (the
authoritative VERIFIED/FAIL result) still ran normally.

## Non-blocking environment quirks noticed along the way

- `/tmp` behaves inconsistently under this sandbox user: files written to
  `/tmp/*` sometimes immediately became unreadable/undirectory-listable
  (`Permission denied`) even though `ls -l /tmp` shows `drwxrwxrwt`. Switched
  to a project-local directory (`run_artifacts/`) for all generated files,
  which behaved normally.
- `git status` fails inside this session with `unable to access
  '/home/anna_ford/.gitconfig': Permission denied`, despite the file showing
  normal `644` permissions for this same user. Not investigated further
  (out of scope for this request; did not block any required pipeline step).

No further time was spent trying to restore network/package access once the
proxy's `403` and the `/etc` permission issue were both confirmed as hard
sandbox restrictions rather than something fixable by retrying.

## Blocker: `gmat-example-reviewer` subagent call (step 4, TJC-15)

Every `subagent({agent: "gmat-example-reviewer", ...})` call (tried 3 times)
failed immediately, before the subagent itself ran, with the same sandbox
`/tmp` permission error seen above:

```
Run fan-out budget manifest is unreadable at
'/tmp/pi-subagents-uid-1000/run-fanout-budgets/<uuid>-<uuid>/manifest.json':
EACCES: permission denied, open '.../manifest.json'
```

`ls -ld /tmp/pi-subagents-uid-1000` shows normal `drwxr-xr-x` permissions for
this same user, but `ls` on the directory itself and its `run-fanout-budgets`
subdirectory both fail with `Permission denied` -- the same `/tmp`
inconsistency noted below (files/dirs that `stat`/`ls -l` report as normally
readable but are not actually readable by this session). This is a sandbox
infrastructure issue with the `subagent` tool's own bookkeeping directory,
not a problem with the `gmat-example-reviewer` agent definition or its task.

Per the pipeline's own fallback rule (step 4: "do not block or retry
indefinitely"), this was not retried further after three identical failures.
The operator-facing report states "GMAT-example review skipped/unavailable"
with this one-line reason, and the numerical VERIFIED/FAIL result (already
obtained independently via the `run_gmat_verification` tool, which does not
go through this same subagent fan-out path) is unaffected.
