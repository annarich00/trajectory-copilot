# Trajectory CoPilot Orbital Mechanics Reference

This document is the physics reference for rendezvous and proximity-operations problems. The intent is that the agent consults this source instead of relying on pretrained memory.

## A. Coordinate Frames

### LVLH
Local Vertical Local Horizontal. A rotating frame centered on the reference spacecraft.

A common convention is:
- \(\hat{x}\): radial direction, outward from the central body through the reference spacecraft
- \(\hat{y}\): along-track direction, in the direction of motion
- \(\hat{z}\): cross-track direction, completing a right-handed triad

### RTN
Radial-Transverse-Normal.
- Radial points from the central body to the spacecraft.
- Transverse lies in the orbital plane, approximately along velocity for near-circular orbits.
- Normal is parallel to orbital angular momentum.

### RIC
Radial-Intrack-Crosstrack.
- Radial is outward from the primary.
- Intrack is along velocity or along-track direction in the orbital plane.
- Crosstrack is orbit normal.

### ECI
Earth-Centered Inertial.
A non-rotating inertial frame used for Cartesian propagation under two-body dynamics.

## Conventions

- Coordinate definitions must be stated explicitly because LVLH/RTN/RIC naming varies across sources.
- CW equations assume a reference orbit with radius \(r_0\) and mean motion \(n\).
- For this repository, the default relative-motion convention is LVLH/RIC with:
  - \(x\) radial,
  - \(y\) along-track/intrack,
  - \(z\) cross-track.

## B. Clohessy-Wiltshire Dynamics

### Assumptions
CW, also called Hill’s equations, is a linearized relative-motion model about a circular reference orbit.

The standard assumptions are:
- chief/reference orbit is circular or nearly circular,
- relative separation is small compared with orbital radius,
- relative velocities are small,
- central-body gravity dominates,
- linearization about the reference orbit is acceptable over the transfer time,
- perturbations are neglected.

### Mean motion definition
For a circular orbit,
\[
 n = \sqrt{\mu / r_0^3}
\]
where:
- \(n\) is mean motion [rad/s],
- \(\mu\) is the gravitational parameter [m^3/s^2],
- \(r_0\) is the reference orbit radius [m].

### Equations of motion
Using the LVLH convention \((x,y,z)\):
\[
\ddot{x} - 2n\dot{y} - 3n^2 x = 0
\]
\[
\ddot{y} + 2n\dot{x} = 0
\]
\[
\ddot{z} + n^2 z = 0
\]

These equations are linear time-invariant in the rotating frame.

### State-transition matrix formulation
The CW state vector is commonly written as
\[
\mathbf{x} = [x, y, z, \dot{x}, \dot{y}, \dot{z}]^T.
\]
The propagated state is
\[
\mathbf{x}(t) = \Phi(t)\,\mathbf{x}(0)
\]
with a 6x6 STM partitioned as:
\[
\Phi = \begin{bmatrix}
\Phi_{rr} & \Phi_{rv} \\
\Phi_{vr} & \Phi_{vv}
\end{bmatrix}
\]
where each block is 3x3.

The STM is used for targeting by solving the appropriate block equation for the initial or terminal impulsive velocity change.

### Implementation audit and convention
The repository implementation uses exactly the state ordering
\( [x,y,z,\dot{x},\dot{y},\dot{z}]^T \) and the x-radial-outward,
y-along-track, z-orbit-normal right-handed LVLH/RIC convention stated above.
`src/cw.py::cw_stm` implements the circular-chief block solution audited in
`docs/cw-stm-audit.md`; that note maps every term to Clohessy & Wiltshire
(1960) and Schaub & Junkins (2018). The block units are \(\Phi_{rr}\) and
\(\Phi_{vv}\) dimensionless, \(\Phi_{rv}\) in seconds, and \(\Phi_{vr}\) in
s⁻¹. The implementation and regression test require \(\Phi(0)=I_6\) within
an absolute tolerance of \(10^{-15}\) for exact floating-point zero time.

### Fixed-duration two-burn targeting and singularities
For a specified duration, let the initial targeting burn change the initial
relative velocity from \(v_0\) to \(v_0^+=v_0+\Delta v_0\). Partitioning the
STM position equation gives
\[
r_f=\Phi_{rr}r_0+\Phi_{rv}v_0^+.
\]
Thus the terminal-position boundary condition is
\[
\Phi_{rv}v_0^+=b,\qquad b=r_f-\Phi_{rr}r_0.
\]
For a well-conditioned full-rank \(\Phi_{rv}\), `src/cw.py::two_burn_targeting`
uses the unique inverse solve and then computes the terminal burn
\(\Delta v_1=v_f-v_f^-\). At integer orbital periods, \(\Phi_{rv}\) is
singular; singularity alone does **not** mean rendezvous is impossible. The
boundary is feasible precisely when \(b\) lies in the column space of
\(\Phi_{rv}\). A feasible rank-deficient system has infinitely many initial
velocity solutions, and the implementation returns the SVD-pseudoinverse
minimum-norm \(v_0^+\), explicitly marked `singular-reachable` and
non-unique.

The implementation uses an SVD relative rank threshold of \(10^{-12}\) times
the largest singular value. It projects \(b\) onto the retained left-singular
vectors and accepts it as reachable only when the projection residual is at
most \(10^{-9}\max(1,\|b\|)\) metres. A singular or ill-conditioned case with
a larger residual returns machine-readable `singular-infeasible` metadata,
a human-readable reason, and no fabricated burns. It does not change the
requested transfer time. These rules apply only to fixed-duration linear CW
targeting; they do not make long-duration, multi-revolution, or nonlocal CW
geometry physically valid, nor do they perform general trajectory
optimization.

### Validity limits
CW is best for local proximity operations, short-to-moderate transfer times, and small relative separations. It degrades when:
- separation is large compared with the orbit radius,
- the transfer is long enough for linearization error to accumulate,
- the reference orbit is not circular,
- the geometry is global-scale rather than local-relative.

### Failure cases
Common CW failure cases include:
- GEO-scale phasing between spacecraft separated by large true-anomaly arcs,
- large along-track separations that are a significant fraction of the orbit,
- noncircular reference orbits,
- long multi-revolution transfers where linear error compounds,
- missions requiring perturbation modeling.

## C. Two-Body Orbital Dynamics

### Assumptions
- central point-mass gravity,
- no thrust during coast arcs,
- no perturbations unless explicitly added.

### Mean motion
For a Keplerian orbit with semi-major axis \(a\):
\[
 n = \sqrt{\mu / a^3}
\]
For a circular orbit, \(a = r_0\).

### Orbital period
\[
 T = 2\pi \sqrt{a^3/\mu}
\]

### Vis-viva equation
\[
 v^2 = \mu\left(\frac{2}{r} - \frac{1}{a}\right)
\]
where \(r\) is the instantaneous radius.

### Bounded deterministic fallback contract
The implemented fallback is a **coast propagator**, not a generalized rendezvous solver. It accepts an initial inertial Cartesian state
\[
\mathbf{x}_0=[x,y,z,v_x,v_y,v_z]^T
\]
in SI units: position in metres, velocity in metres per second, positive \(\mu\) in m³/s², a finite duration in seconds, and a positive fixed RK4 step count. Its output is the final state in the same SI inertial Cartesian frame. The stable like-for-like metadata is `frame="inertial-cartesian"`, `central_body="Earth"`, `dynamics="point-mass-two-body"`, and `integrator="fixed-step-rk4"`; an optional epoch may accompany a case for an external verifier.

`src/twobody.py::TwoBodyCase` carries those inputs and metadata for the later pinned Poliastro adapter. The core propagator imports neither Poliastro nor Astropy.

### Point-mass equation and state derivative
For \(\mathbf{x}=[\mathbf{r},\mathbf{v}]^T\), the point-mass coast dynamics are:
\[
\dot{\mathbf{r}}=\mathbf{v},\qquad
\dot{\mathbf{v}}=-\mu\frac{\mathbf{r}}{\|\mathbf{r}\|^3}.
\]
The central-body singularity \(\|\mathbf{r}\|=0\), non-finite values, non-positive \(\mu\), and a non-positive step count are rejected explicitly.

### Fixed-step classical RK4 stages
For derivative \(f(\mathbf{x})\) and step \(h=\Delta t/N\), the implementation evaluates:
\[
k_1=f(\mathbf{x}_i),\quad k_2=f(\mathbf{x}_i+h k_1/2),\quad
k_3=f(\mathbf{x}_i+h k_2/2),\quad k_4=f(\mathbf{x}_i+h k_3),
\]
then advances
\[
\mathbf{x}_{i+1}=\mathbf{x}_i+\frac{h}{6}(k_1+2k_2+2k_3+k_4).
\]
In code this is split into position and velocity stages in `src/twobody.py::kepler_propagate_state`; `propagate_cartesian_state` is the six-element wrapper.

### Invariants and verification evidence
For an unperturbed coast arc, the specific energy
\[
\epsilon=\frac{1}{2}\|\mathbf{v}\|^2-\frac{\mu}{\|\mathbf{r}\|}
\]
and specific angular momentum
\[
\mathbf{h}=\mathbf{r}\times\mathbf{v}
\]
should remain constant to numerical integration error. `tests/test_twobody.py` checks a circular LEO state against its analytical one-period return (2 cm position and 2e-5 m/s velocity tolerances) and checks these invariants over three periods. It also shows that a deliberately CW-invalid, 1,000 km radial-separation absolute state propagates deterministically under the same bounded coast contract.

### Unsupported requests and limitations
`unsupported_request()` returns `UNSUPPORTED` for targeting, maneuver design, trajectory optimization, thrust, and perturbation requests rather than improvising a result. The fallback supports no LVLH-relative input or unspecified frame, no burn execution, and no J2, drag, third bodies, solar radiation pressure, or thrust. It is suitable as a deterministic point-mass propagation result for later GMAT comparison, not a claim that a rendezvous has been solved. GMAT remains the required end-to-end numerical and visual verifier; the pinned Poliastro adapter is intentionally deferred to TJC-1.7.

## D. Model Selection Guidance

### When CW is valid
CW is appropriate when:
- the reference orbit is circular or close to circular,
- the relative distance is small compared with orbital radius,
- the mission is a local rendezvous or proximity-operations problem,
- the time horizon is short enough that linearization remains accurate,
- the problem is expressed in a clear LVLH/RTN/RIC frame.

### When CW is invalid
Reject CW when:
- the target/chaser separation is large,
- the scenario is really a phasing problem around the full orbit,
- the orbit is GEO-scale with large angular separation,
- the transfer spans multiple revolutions with meaningful nonlinear drift,
- the chief orbit is not near circular,
- the frame convention is ambiguous.

### GEO separation examples
If one spacecraft is roughly one-third of the GEO belt away from another, the geometry is not local proximity motion. CW should be rejected because the relative separation is too large and the nonlinear orbital geometry dominates the motion.

### Large-phasing examples
Large phasing arcs are better treated with two-body or higher-fidelity propagation. If the objective is to move along the orbit by a large fraction of the orbital circumference, the problem is not a small relative-motion problem.

### Multi-revolution limitations
CW can be used for some multi-revolution rendezvous problems, but the error grows with duration and the transfer can become ill-conditioned near singular times. For long or multi-rev problems, verify with two-body propagation at minimum and use higher-fidelity methods if accuracy matters.
