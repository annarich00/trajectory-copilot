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

### Known singularities
The CW targeting problem can become singular or ill-conditioned when the velocity-to-position mapping loses rank for particular transfer times, especially at times near integer multiples of the orbital period where certain in-plane terms vanish or nearly vanish.

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

### State propagation concepts
Two-body propagation in Cartesian coordinates is performed by numerically integrating:
\[
\ddot{\mathbf{r}} = -\mu \mathbf{r}/\|\mathbf{r}\|^3
\]
or by using Keplerian element propagation for Keplerian arcs.

This model is nonlinear but much more general than CW.

### Assumptions and limitations
Two-body propagation is appropriate when central gravity dominates and perturbations are small enough to ignore over the arc. It does not capture drag, J2, third-body effects, solar radiation pressure, or thrust unless added.

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
