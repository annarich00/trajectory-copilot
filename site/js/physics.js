/**
 * physics.js — a PEDAGOGICAL / VISUALIZATION MIRROR of the deterministic
 * physics source in this repository. It exists ONLY so that sliders, live
 * tables, and step-by-step walkthroughs in the browser can show numbers
 * without a server-side Python process.
 *
 * ============================ IMPORTANT ============================
 * This file is NOT an independent implementation, NOT a verification
 * authority, and NOT a second source of truth. It is a hand-ported copy of
 * specific functions in src/cw.py, src/twobody.py, and src/verify.py, kept
 * only for interactive display purposes.
 *
 *   - The AUTHORITATIVE physics implementation is the Python code in
 *     src/cw.py, src/twobody.py, src/verify.py, src/optimization.py.
 *   - The AUTHORITATIVE test results are produced by running pytest against
 *     tests/ in this repository (see the Test Explorer page for the exact
 *     command). Nothing in this browser page runs pytest or Python.
 *   - Every number this file produces is labeled in the UI as a
 *     "pedagogical browser mirror" result, naming the exact Python function
 *     it is hand-ported from. It should never be described as "confirming",
 *     "verifying", or "proving" the Python result — only as illustrating the
 *     same equations interactively.
 *   - If src/*.py changes, this file can silently drift out of sync, because
 *     there is no shared code path between them. Treat any disagreement
 *     between this file and the Python as a bug in this file, never as
 *     evidence against the Python.
 * =====================================================================
 *
 * Nothing here calls out to a network or external API. All computation is
 * local, deterministic, numerical linear algebra implemented from scratch
 * (3x3 / 6-vector operations only, matching what the CW/two-body code needs).
 */

/* ---------------------------------------------------------------------
 * Small linear-algebra helpers (no library — mirrors numpy usage inline)
 * ------------------------------------------------------------------- */

function vSub(a, b) { return a.map((x, i) => x - b[i]); }
function vAdd(a, b) { return a.map((x, i) => x + b[i]); }
function vScale(a, s) { return a.map((x) => x * s); }
function vDot(a, b) { return a.reduce((s, x, i) => s + x * b[i], 0); }
function vNorm(a) { return Math.sqrt(vDot(a, a)); }
function vCross(a, b) {
  return [
    a[1] * b[2] - a[2] * b[1],
    a[2] * b[0] - a[0] * b[2],
    a[0] * b[1] - a[1] * b[0],
  ];
}
function mat3VecMul(M, v) {
  return [0, 1, 2].map((i) => M[i][0] * v[0] + M[i][1] * v[1] + M[i][2] * v[2]);
}
function mat3TVecMul(M, v) {
  // M^T @ v
  return [0, 1, 2].map((j) => M[0][j] * v[0] + M[1][j] * v[1] + M[2][j] * v[2]);
}
function det3(m) {
  return (
    m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) -
    m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) +
    m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
  );
}
function solve3(M, b) {
  // Cramer's rule — fine for a 3x3 targeting solve; mirrors np.linalg.solve
  // for the purpose of this demo (the Python uses LU via LAPACK).
  const D = det3(M);
  const cols = [0, 1, 2].map((col) => {
    const Mi = M.map((row) => row.slice());
    for (let r = 0; r < 3; r++) Mi[r][col] = b[r];
    return det3(Mi);
  });
  return cols.map((c) => c / D);
}
// crude condition number estimate (ratio of largest/smallest singular value
// of a 3x3 via power iteration on M^T M) — used ONLY for the illustrative
// "singularity" demo, not a substitute for np.linalg.cond.
function approxCond3(M) {
  // M^T M
  const Mt = [[M[0][0], M[1][0], M[2][0]], [M[0][1], M[1][1], M[2][1]], [M[0][2], M[1][2], M[2][2]]];
  function matMul(A, B) {
    const out = [[0,0,0],[0,0,0],[0,0,0]];
    for (let i=0;i<3;i++) for (let j=0;j<3;j++) for (let k=0;k<3;k++) out[i][j]+=A[i][k]*B[k][j];
    return out;
  }
  const G = matMul(Mt, M);
  function powerIter(A, iters=100) {
    let v = [1,1,1];
    let lambda = 0;
    for (let i=0;i<iters;i++) {
      const w = mat3VecMul(A, v);
      const n = vNorm(w);
      if (n === 0) return 0;
      v = w.map(x=>x/n);
      lambda = n;
    }
    return lambda;
  }
  const lambdaMax = powerIter(G);
  // smallest eigenvalue via inverse power iteration is expensive to hand-roll
  // robustly; instead use det and trace-based estimate acceptable for a demo.
  const d = det3(M);
  if (d === 0 || !isFinite(d)) return Infinity;
  // sigma_min^2 * sigma_max^2 * sigma_mid^2 = det(G); approximate sigma_min
  // using det(M) and the two already-known large directions is nontrivial in
  // closed form for 3x3, so for the demo we fall back to norm(M)*norm(inv(M)).
  const Minv = invert3(M);
  const normM = Math.sqrt(M.flat().reduce((s,x)=>s+x*x,0));
  const normMinv = Math.sqrt(Minv.flat().reduce((s,x)=>s+x*x,0));
  return normM * normMinv;
}
function invert3(M) {
  const d = det3(M);
  const adj = [
    [
      (M[1][1]*M[2][2]-M[1][2]*M[2][1]),
      -(M[0][1]*M[2][2]-M[0][2]*M[2][1]),
      (M[0][1]*M[1][2]-M[0][2]*M[1][1]),
    ],
    [
      -(M[1][0]*M[2][2]-M[1][2]*M[2][0]),
      (M[0][0]*M[2][2]-M[0][2]*M[2][0]),
      -(M[0][0]*M[1][2]-M[0][2]*M[1][0]),
    ],
    [
      (M[1][0]*M[2][1]-M[1][1]*M[2][0]),
      -(M[0][0]*M[2][1]-M[0][1]*M[2][0]),
      (M[0][0]*M[1][1]-M[0][1]*M[1][0]),
    ],
  ];
  // adj above is cofactor matrix (not yet transposed); build inverse = adjT/det
  const cof = adj;
  const inv = [[0,0,0],[0,0,0],[0,0,0]];
  for (let i=0;i<3;i++) for (let j=0;j<3;j++) inv[i][j] = cof[j][i]/d;
  return inv;
}

/* ---------------------------------------------------------------------
 * Mirrors of src/cw.py
 * ------------------------------------------------------------------- */

// Mirrors: src/cw.py :: mean_motion(mu, reference_radius_m)
function meanMotion(mu, r0) {
  return Math.sqrt(mu / (r0 * r0 * r0));
}

// Mirrors: src/cw.py :: cw_stm(n, t)
// Returns { phi_rr, phi_rv, phi_vr, phi_vv } each a 3x3 array-of-arrays,
// exactly matching the block structure built in cw_stm().
function cwStm(n, t) {
  const nt = n * t;
  const s = Math.sin(nt);
  const c = Math.cos(nt);

  const phi_rr = [
    [4 - 3 * c, 0.0, 0.0],
    [6 * (s - nt), 1.0, 0.0],
    [0.0, 0.0, c],
  ];
  const phi_rv = [
    [s / n, (2 * (1 - c)) / n, 0.0],
    [(2 * (c - 1)) / n, (4 * s - 3 * nt) / n, 0.0],
    [0.0, 0.0, s / n],
  ];
  const phi_vr = [
    [3 * n * s, 0.0, 0.0],
    [6 * n * (c - 1), 0.0, 0.0],
    [0.0, 0.0, -n * s],
  ];
  const phi_vv = [
    [c, 2 * s, 0.0],
    [-2 * s, 4 * c - 3, 0.0],
    [0.0, 0.0, c],
  ];
  return { phi_rr, phi_rv, phi_vr, phi_vv, nt, s, c };
}

// Mirrors: src/cw.py :: propagate_relative_state(state0, n, t)
function propagateRelativeState(state0, n, t) {
  const r0 = state0.slice(0, 3);
  const v0 = state0.slice(3, 6);
  const { phi_rr, phi_rv, phi_vr, phi_vv } = cwStm(n, t);
  const r = vAdd(mat3VecMul(phi_rr, r0), mat3VecMul(phi_rv, v0));
  const v = vAdd(mat3VecMul(phi_vr, r0), mat3VecMul(phi_vv, v0));
  return r.concat(v);
}

// Mirrors: src/cw.py :: validate_cw_use(reference_radius_m, relative_position_m, transfer_time_s, n)
function validateCwUse(r0, relPos, transferTime, n) {
  const warnings = [];
  const rel = vNorm(relPos);
  if (r0 <= 0) warnings.push('Reference orbit radius must be positive.');
  if (rel / r0 > 0.01) warnings.push('Relative separation is large compared with orbit radius.');
  if (transferTime <= 0) warnings.push('Transfer time must be positive.');
  if (n != null && transferTime > (2 * Math.PI / n) * 2) {
    warnings.push('Transfer spans more than about two orbital periods.');
  }
  return { valid: warnings.length === 0, warnings };
}

// CW_CONDITION_NUMBER_LIMIT mirrors src/cw.py module constant.
const CW_CONDITION_NUMBER_LIMIT = 1.0e6;

// Mirrors: src/cw.py :: check_phi_rv_conditioning(phi_rv, condition_limit)
// Raises (throws) CWSingularTransferError-equivalent under the same
// conditions as the Python: non-finite entries, exact singularity (det=0),
// or condition number above the limit.
class CWSingularTransferError extends Error {}

function checkPhiRvConditioning(phi_rv, conditionLimit = CW_CONDITION_NUMBER_LIMIT) {
  const flat = phi_rv.flat();
  if (flat.some((x) => !isFinite(x))) {
    throw new CWSingularTransferError(
      'Phi_rv contains non-finite entries; CW targeting is undefined for this transfer time.'
    );
  }
  const d = det3(phi_rv);
  if (d === 0 || !isFinite(d)) {
    throw new CWSingularTransferError(
      'Phi_rv is exactly singular (det=0); two-impulse CW targeting has no unique solution at this transfer time.'
    );
  }
  const cond = approxCond3(phi_rv);
  if (!isFinite(cond) || cond > conditionLimit) {
    throw new CWSingularTransferError(
      `Phi_rv is ill-conditioned for CW targeting (cond≈${cond.toExponential(3)} > limit=${conditionLimit.toExponential(1)}).`
    );
  }
  return cond;
}

// Mirrors: src/cw.py :: two_burn_targeting(state0, n, t_final, target_final_state)
// Returns { dv0, dv1, finalState, phi, steps } where `steps` captures each
// intermediate quantity for the step-by-step teaching walkthrough.
function twoBurnTargeting(state0, n, tFinal, targetFinalState = null) {
  const r0 = state0.slice(0, 3);
  const v0 = state0.slice(3, 6);
  const target = targetFinalState || [0, 0, 0, 0, 0, 0];
  const rfDes = target.slice(0, 3);
  const vfDes = target.slice(3, 6);

  const phi = cwStm(n, tFinal);
  const { phi_rr, phi_rv, phi_vr, phi_vv } = phi;

  const phiRrR0 = mat3VecMul(phi_rr, r0);
  const phiRvV0 = mat3VecMul(phi_rv, v0);
  const rhs = vSub(vSub(rfDes, phiRrR0), phiRvV0);

  checkPhiRvConditioning(phi_rv); // throws CWSingularTransferError if ill-posed
  const dv0 = solve3(phi_rv, rhs);

  const v0Plus = vAdd(v0, dv0);
  const vfMinus = vAdd(mat3VecMul(phi_vr, r0), mat3VecMul(phi_vv, v0Plus));
  const dv1 = vSub(vfDes, vfMinus);
  const rf = vAdd(mat3VecMul(phi_rr, r0), mat3VecMul(phi_rv, v0Plus));
  const vf = vAdd(vfMinus, dv1);

  return {
    dv0, dv1,
    finalState: rf.concat(vf),
    phi,
    steps: { r0, v0, rfDes, vfDes, phiRrR0, phiRvV0, rhs, v0Plus, vfMinus, rf, vf },
  };
}

// Mirrors: src/cw.py :: solve_cw_rendezvous(mu, reference_radius_m, state0, t_final, target_final_state, trajectory_samples)
// Orchestrates meanMotion -> twoBurnTargeting -> propagateRelativeState into
// one complete CW rendezvous result, matching the structured fields the
// authoritative Python function returns (burns, total delta-v, trajectory,
// final state, time of flight, units/frame/assumptions, status).
const CW_RENDEZVOUS_FRAME_MIRROR = 'LVLH/RIC: x radial outward, y along-track, z cross-track (reference/SOURCE.md Sec A.1)';
const CW_RENDEZVOUS_ASSUMPTIONS_MIRROR = [
  'circular, or explicitly justified near-circular, chief/reference orbit',
  'local relative separation, small relative to the reference-orbit radius, not global phasing',
  'small relative velocity and a fixed transfer duration/regime for which CW linearization remains acceptable',
  'right-handed LVLH/RIC frame and [x, y, z, x_dot, y_dot, z_dot] state ordering (reference/SOURCE.md Sec A.1)',
  'central-body gravity dominance with perturbations neglected',
  'impulsive, instantaneous two-burn maneuvers at the start and end of the fixed transfer',
];

function solveCwRendezvous(mu, referenceRadiusM, state0, tFinal, targetFinalState = null, trajectorySamples = 50) {
  const n = meanMotion(mu, referenceRadiusM);
  let targeting;
  try {
    targeting = twoBurnTargeting(state0, n, tFinal, targetFinalState);
  } catch (e) {
    // In this browser mirror, a thrown CWSingularTransferError-equivalent
    // corresponds to the Python's "singular-infeasible" structured status,
    // since checkPhiRvConditioning/solve3 do not reproduce the SVD
    // reachability path implemented in src/cw.py::two_burn_targeting.
    return {
      status: 'singular-infeasible', feasible: false, meanMotionRadps: n, transferTimeS: tFinal,
      dv0: null, dv1: null, totalDeltaV: null, trajectoryTimesS: null, trajectoryStates: null,
      finalState: null, reason: e.message,
      frame: CW_RENDEZVOUS_FRAME_MIRROR, assumptions: CW_RENDEZVOUS_ASSUMPTIONS_MIRROR,
    };
  }
  const postBurn1State = state0.slice(0, 3).concat(vAdd(state0.slice(3, 6), targeting.dv0));
  const trajectoryTimesS = [];
  const trajectoryStates = [];
  for (let i = 0; i < trajectorySamples; i++) {
    const t = (tFinal * i) / (trajectorySamples - 1);
    trajectoryTimesS.push(t);
    trajectoryStates.push(propagateRelativeState(postBurn1State, n, t));
  }
  return {
    status: 'unique', feasible: true, meanMotionRadps: n, transferTimeS: tFinal,
    dv0: targeting.dv0, dv1: targeting.dv1,
    totalDeltaV: vNorm(targeting.dv0) + vNorm(targeting.dv1),
    trajectoryTimesS, trajectoryStates, finalState: targeting.finalState,
    reason: 'Phi_rv is well-conditioned; returned the unique inverse solution.',
    frame: CW_RENDEZVOUS_FRAME_MIRROR, assumptions: CW_RENDEZVOUS_ASSUMPTIONS_MIRROR,
  };
}

/* ---------------------------------------------------------------------
 * Mirrors of src/twobody.py
 * ------------------------------------------------------------------- */

// Mirrors: src/twobody.py :: orbital_period(mu, semi_major_axis_m)
function orbitalPeriod(mu, a) {
  return 2.0 * Math.PI * Math.sqrt((a * a * a) / mu);
}

// Mirrors: src/twobody.py :: vis_viva_speed(mu, radius_m, semi_major_axis_m)
function visVivaSpeed(mu, r, a) {
  return Math.sqrt(mu * (2.0 / r - 1.0 / a));
}

// Mirrors: src/twobody.py :: kepler_propagate_state(r0, v0, mu, dt, steps)
// Classic RK4 integration of r'' = -mu r / |r|^3, identical structure to the
// Python implementation (same k1..k4 stages, same step count default).
function keplerPropagateState(r0, v0, mu, dt, steps = 2000) {
  let r = r0.slice();
  let v = v0.slice();
  const h = dt / steps;

  function accel(x) {
    const norm = vNorm(x);
    return vScale(x, -mu / (norm * norm * norm));
  }

  for (let i = 0; i < steps; i++) {
    const k1_r = v;
    const k1_v = accel(r);

    const k2_r = vAdd(v, vScale(k1_v, 0.5 * h));
    const k2_v = accel(vAdd(r, vScale(k1_r, 0.5 * h)));

    const k3_r = vAdd(v, vScale(k2_v, 0.5 * h));
    const k3_v = accel(vAdd(r, vScale(k2_r, 0.5 * h)));

    const k4_r = vAdd(v, vScale(k3_v, h));
    const k4_v = accel(vAdd(r, vScale(k3_r, h)));

    r = vAdd(r, vScale(vAdd(vAdd(k1_r, vScale(k2_r, 2)), vAdd(vScale(k3_r, 2), k4_r)), h / 6.0));
    v = vAdd(v, vScale(vAdd(vAdd(k1_v, vScale(k2_v, 2)), vAdd(vScale(k3_v, 2), k4_v)), h / 6.0));
  }
  return [r, v];
}

// Mirrors: src/twobody.py :: propagate_cartesian_state(state0, mu, dt, steps)
function propagateCartesianState(state0, mu, dt, steps = 2000) {
  const [r, v] = keplerPropagateState(state0.slice(0, 3), state0.slice(3, 6), mu, dt, steps);
  return r.concat(v);
}

// Mirrors: src/twobody.py :: specific_orbital_energy(state, mu)
function specificOrbitalEnergy(state, mu) {
  const r = state.slice(0, 3);
  const v = state.slice(3, 6);
  return 0.5 * vDot(v, v) - mu / vNorm(r);
}

// Mirrors: src/twobody.py :: specific_angular_momentum(state)
function specificAngularMomentum(state) {
  return vCross(state.slice(0, 3), state.slice(3, 6));
}

/* ---------------------------------------------------------------------
 * Mirrors of src/verify.py
 * ------------------------------------------------------------------- */

// Mirrors: src/verify.py :: compare_cw_two_body(cw_state, two_body_state, pos_tol_m, vel_tol_mps)
function compareCwTwoBody(cwState, twoBodyState, posTolM = 50.0, velTolMps = 0.05) {
  const posErr = vNorm(vSub(cwState.slice(0, 3), twoBodyState.slice(0, 3)));
  const velErr = vNorm(vSub(cwState.slice(3, 6), twoBodyState.slice(3, 6)));
  const warnings = [];
  if (posErr > posTolM || velErr > velTolMps) warnings.push('MODEL VALIDITY WARNING');
  return { cwState, twoBodyState, posErrM: posErr, velErrMps: velErr, warnings };
}

// Mirrors: src/verify.py :: _chief_circular_state(n, mu)
function chiefCircularState(n, mu) {
  const r0 = Math.pow(mu / (n * n), 1.0 / 3.0);
  const v0 = n * r0;
  return [[r0, 0.0, 0.0], [0.0, v0, 0.0]];
}

// Mirrors: src/verify.py :: _lvlh_basis(chief_pos, chief_vel)
function lvlhBasis(chiefPos, chiefVel) {
  const rHat = vScale(chiefPos, 1 / vNorm(chiefPos));
  const h = vCross(chiefPos, chiefVel);
  const hHat = vScale(h, 1 / vNorm(h));
  const tHat = vCross(hHat, rHat);
  // columns = [rHat, tHat, hHat]
  const R = [
    [rHat[0], tHat[0], hHat[0]],
    [rHat[1], tHat[1], hHat[1]],
    [rHat[2], tHat[2], hHat[2]],
  ];
  return { R, hHat };
}

// Mirrors: src/verify.py :: _rel_lvlh_to_absolute(chief_pos, chief_vel, rel_state, n)
function relLvlhToAbsolute(chiefPos, chiefVel, relState, n) {
  const { R, hHat } = lvlhBasis(chiefPos, chiefVel);
  const rRelLvlh = relState.slice(0, 3);
  const vRelLvlh = relState.slice(3, 6);
  const rRelInertial = mat3VecMul(R, rRelLvlh);
  const omega = vScale(hHat, n);
  const deputyPos = vAdd(chiefPos, rRelInertial);
  const vRelInertial = vAdd(mat3VecMul(R, vRelLvlh), vCross(omega, rRelInertial));
  const deputyVel = vAdd(chiefVel, vRelInertial);
  return [deputyPos, deputyVel];
}

// Mirrors: src/verify.py :: _absolute_to_rel_lvlh(chief_pos, chief_vel, deputy_pos, deputy_vel, n)
function absoluteToRelLvlh(chiefPos, chiefVel, deputyPos, deputyVel, n) {
  const { R, hHat } = lvlhBasis(chiefPos, chiefVel);
  const rRelInertial = vSub(deputyPos, chiefPos);
  const vRelInertial = vSub(deputyVel, chiefVel);
  const omega = vScale(hHat, n);
  const rRelLvlh = mat3TVecMul(R, rRelInertial);
  const vRelLvlh = mat3TVecMul(R, vSub(vRelInertial, vCross(omega, rRelInertial)));
  return rRelLvlh.concat(vRelLvlh);
}

// Mirrors: src/verify.py :: validate_against_two_body(initial_state, n, dt, mu, pos_tol_m, vel_tol_mps)
function validateAgainstTwoBody(initialState, n, dt, mu, posTolM = 50.0, velTolMps = 0.05, steps = 2000) {
  const cwState = propagateRelativeState(initialState, n, dt);

  const [chiefPos0, chiefVel0] = chiefCircularState(n, mu);
  const [deputyPos0, deputyVel0] = relLvlhToAbsolute(chiefPos0, chiefVel0, initialState, n);

  const chiefStateF = propagateCartesianState(chiefPos0.concat(chiefVel0), mu, dt, steps);
  const deputyStateF = propagateCartesianState(deputyPos0.concat(deputyVel0), mu, dt, steps);

  const tbState = absoluteToRelLvlh(
    chiefStateF.slice(0, 3), chiefStateF.slice(3, 6),
    deputyStateF.slice(0, 3), deputyStateF.slice(3, 6),
    n
  );

  return {
    ...compareCwTwoBody(cwState, tbState, posTolM, velTolMps),
    chiefPos0, chiefVel0, deputyPos0, deputyVel0, chiefStateF, deputyStateF,
  };
}

/* ---------------------------------------------------------------------
 * Exports (plain global object — no bundler/module system in this repo)
 * ------------------------------------------------------------------- */

window.TCPhysics = {
  // vector/matrix helpers
  vSub, vAdd, vScale, vDot, vNorm, vCross, mat3VecMul, mat3TVecMul, det3, solve3, invert3, approxCond3,
  // cw.py mirror
  meanMotion, cwStm, propagateRelativeState, validateCwUse,
  CW_CONDITION_NUMBER_LIMIT, CWSingularTransferError, checkPhiRvConditioning, twoBurnTargeting, solveCwRendezvous,
  // twobody.py mirror
  orbitalPeriod, visVivaSpeed, keplerPropagateState, propagateCartesianState,
  specificOrbitalEnergy, specificAngularMomentum,
  // verify.py mirror
  compareCwTwoBody, chiefCircularState, lvlhBasis, relLvlhToAbsolute, absoluteToRelLvlh, validateAgainstTwoBody,
};
