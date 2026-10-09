# Trajectory CoPilot Controlled Reference

## Status, authority, and semester boundary

This is the controlled physics reference for the scoped semester rendezvous
workflow. It is authoritative for the conventions and contracts stated here;
`src/` is authoritative for deterministic behavior and `tests/` are the
executable evidence. The active workflow is limited to:

1. problem formulation;
2. fixed-duration CW rendezvous;
3. bounded inertial two-body coast fallback;
4. assumption-based model selection; and
5. GMAT numerical-plus-screenshot verification.

It does **not** support generalized trajectory optimization, transfer-time or
delta-v trade studies, Pareto fronts, continuous thrust, perturbation models,
CR3BP/cislunar/n-body dynamics, broad mission planning, or universal/learned
CW-validity thresholds. Those are future-work or excluded topics, not claims
made by this repository.

## A. Frames, state ordering, and units

### A.1 LVLH/RIC convention used by the CW code

The recovered CW implementation uses the right-handed LVLH/RIC convention:

- `x`: radial outward from the central body through the chief/reference;
- `y`: along-track (in-track), in the chief's direction of motion; and
- `z`: cross-track/orbit-normal, completing the right-handed triad.

The relative state is ordered exactly as

\[
\mathbf{x}=[x,y,z,\dot{x},\dot{y},\dot{z}]^T.
\]

`src/cw.py::cw_stm`, `propagate_relative_state`, and
`two_burn_targeting` use that ordering. `src/verify.py` uses the same axis
meaning when it converts a circular chief/deputy case between LVLH and inertial
Cartesian coordinates. LVLH, RTN, and RIC names vary across sources; a caller
must state this convention rather than infer a different one.

### A.2 Inertial Cartesian convention used by the two-body fallback

The bounded fallback accepts and returns the state

\[
[x,y,z,v_x,v_y,v_z]^T
\]

in a declared inertial Cartesian frame. It does not accept LVLH-relative input
without an explicitly implemented transformation. Its stable metadata is
`frame="inertial-cartesian"`, `central_body="Earth"`,
`dynamics="point-mass-two-body"`, and `integrator="fixed-step-rk4"`.

### A.3 Units

All deterministic inputs and outputs use SI units:

- position and distance: m;
- velocity: m/s;
- time/duration: s;
- gravitational parameter \(\mu\): m³/s²; and
- mean motion \(n\): rad/s.

## B. Clohessy-Wiltshire local rendezvous

### B.1 Physical assumptions

CW (Hill) dynamics are a linearized relative-motion model about a circular or
near-circular chief/reference orbit. The intended regime requires documented
support for all of the following:

- circularity (or explicitly justified near-circular approximation);
- local separation relative to reference-orbit radius, not global phasing;
- small relative velocity and a transfer duration/regime for which
  linearization remains acceptable;
- the LVLH/RIC frame and state ordering in §A.1;
- central-body gravity dominance with perturbations neglected; and
- impulsive-burn suitability for the fixed-duration two-impulse targeting
  path.

These are an assumption-based selection checklist, not a universal learned
threshold. `src/cw.py::validate_cw_use` emits only limited deterministic
warnings (currently a separation ratio heuristic and an approximately
two-orbit duration heuristic); it neither establishes the full physical case
nor replaces this assessment.

### B.2 Mean motion and equations of motion

For circular reference radius \(r_0\),

\[
n=\sqrt{\mu/r_0^3}.
\]

With the §A.1 LVLH axes, the implemented equations are

\[
\ddot{x}-2n\dot{y}-3n^2x=0,
\]
\[
\ddot{y}+2n\dot{x}=0,
\]
\[
\ddot{z}+n^2z=0.
\]

`src/cw.py::cw_stm` implements the circular-chief closed-form STM for
\(\mathbf{x}(t)=\Phi(t)\mathbf{x}(0)\). The block units are
\(\Phi_{rr}\) and \(\Phi_{vv}\) dimensionless, \(\Phi_{rv}\) seconds,
and \(\Phi_{vr}\) s⁻¹. `docs/cw-stm-audit.md` maps the implemented terms to
its cited CW sources; `tests/test_cw.py` exercises zero-time identity and
quarter-orbit signs/units.

### B.3 Fixed-duration two-impulse targeting and singularities

`src/cw.py::two_burn_targeting` is a deterministic fixed-duration,
two-impulse CW calculation, not transfer-time optimization. With the STM
position partition, it solves

\[
\Phi_{rv}v_0^+=b,\qquad b=r_f-\Phi_{rr}r_0.
\]

A well-conditioned full-rank \(\Phi_{rv}\) has a unique direct solution.
At singular or near-singular transfer times, singularity alone does **not**
make rendezvous impossible: the boundary is feasible exactly when \(b\) lies
in the column space of \(\Phi_{rv}\). The implementation uses an SVD
relative rank threshold of \(10^{-12}\) times the largest singular value and
accepts reachability only when the projection residual is at most
\(10^{-9}\max(1,\|b\|)\) m. A reachable rank-deficient system returns the
SVD-pseudoinverse minimum-norm \(v_0^+\), marked `singular-reachable` and
non-unique; an unreachable boundary returns `singular-infeasible` metadata,
a human-readable reason, and no fabricated burns. The requested transfer time
is never changed. These algebraic outcomes do not make long-duration,
multi-revolution, or nonlocal CW geometry physically valid.

### B.4 Applicability and rejection guidance

CW should be rejected or held for more information when circularity, locality,
duration/regime, frame definition, or the other §B.1 assumptions are unknown
or unsupported. Large separations relative to orbital radius, global or
GEO-scale phasing, non-circular chiefs, long/multi-revolution regimes, and
required perturbation modeling are documented reasons not to claim a local CW
result. They do not imply that this repository provides a general replacement
solver.

## C. Bounded two-body coast fallback

### C.1 Assumptions and contract

`src/twobody.py` implements deterministic point-mass two-body **coast
propagation**, not generalized rendezvous targeting. It requires an initial
six-element inertial Cartesian SI state, positive \(\mu\), finite duration,
and a positive fixed RK4 step count. It returns the final state in the same
frame and units.

The model assumes central point-mass gravity, no thrust during the coast arc,
and no perturbations. Its state derivative is

\[
\dot{\mathbf r}=\mathbf v,\qquad
\dot{\mathbf v}=-\mu\frac{\mathbf r}{\|\mathbf r\|^3}.
\]

The zero-radius singularity, non-finite inputs, non-positive \(\mu\), and
non-positive step count are explicitly rejected. `kepler_propagate_state`
uses fixed-step classical RK4; `propagate_cartesian_state` is its six-element
wrapper.

### C.2 What the fallback does not claim

The fallback has no burn execution, rendezvous targeting, optimization,
LVLH-relative input, J2, drag, third bodies, solar radiation pressure, or
thrust. `unsupported_request()` returns `UNSUPPORTED` for targeting,
maneuver, optimization, thrust, and perturbation requests rather than
improvising a result. A propagated coast state is not evidence that a
rendezvous has been solved.

`tests/test_twobody.py` checks a circular LEO one-period return, energy and
angular-momentum behavior, invalid input rejection, and deterministic behavior
for a deliberately CW-invalid geometry. Those tests evidence the bounded
contract only, not omitted physics.

## D. Assumption-based model selection

The active selector must choose only one of these outcomes:

- **CW rendezvous:** only after §B.1 assumptions and targeting conditioning
  are documented for a fixed-duration local case;
- **bounded two-body fallback:** only for the §C.1 inertial Cartesian
  point-mass coast contract; or
- **needs more information / unsupported:** for ambiguous frames, missing
  essential inputs, perturbed or thrust cases, optimization, variable-duration
  trade studies, or any case outside both contracts.

The selector must report circularity, locality/separation relative to radius,
duration/regime, frame/state definition, other physical assumptions, and
unknown or violated assumptions. It must not infer a universal learned
threshold from `validate_cw_use()` or from an isolated example.

## E. Required GMAT verification evidence

The scoped end-to-end verification requirement is both:

1. GMAT numerical output for the same declared case, compared against the
   candidate in matched frame, epoch, state order, units, dynamics, and
   documented position/velocity tolerances; and
2. a non-empty accessible GMAT orbit/trajectory screenshot with a stable path
   or link.

A tolerance exceedance, unavailable/failed GMAT execution, mismatched
comparison data, or missing/inaccessible screenshot is not `PASS`; it must
remain distinguishable as `FAIL`, `UNAVAILABLE`, or `INCOMPLETE`. The
recovered repository does not yet integrate GMAT. Internal two-body comparison
and the isolated pinned Poliastro adapter are bounded code-level checks and do
not replace the required GMAT numerical-plus-screenshot evidence.

## F. Future-work and unsupported capability boundary

Potential higher-fidelity propagation, optimization, Pareto analysis,
perturbation modeling, CR3BP/cislunar work, broad benchmarks, and generalized
mission design are intentionally outside this controlled reference's supported
semester workflow. They may be discussed as future work only when explicitly
labeled unsupported and must not be selected, promised, or reported as an
implemented capability.
