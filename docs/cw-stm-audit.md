# CW state-transition-matrix audit (TJC-1.3)

## Scope and authoritative source

This is an independent, term-level audit of `src/cw.py::cw_stm`, performed for
TJC-1.3. The governing equations and convention are documented in the
controlled reference, `reference/SOURCE.md` §A–B: the right-handed LVLH/RIC
axes are x radial outward, y along-track/in-track in the chief direction of
motion, and z cross-track/orbit-normal. The state is

\[
X=[x,y,z,\dot x,\dot y,\dot z]^T.
\]

The equations audited are (Clohessy & Wiltshire, 1960, Eqs. 1–3):

\[
\ddot x-2n\dot y-3n^2x=0,\qquad
\ddot y+2n\dot x=0,\qquad
\ddot z+n^2z=0.
\]

The block solution below is from Schaub & Junkins, *Analytical Mechanics of
Space Systems*, 4th ed. (2018), Sec. 14.6, Eqs. 14.48–14.51, written in the
same radial/along-track/cross-track ordering. The original source is
W. H. Clohessy and R. S. Wiltshire, “Terminal Guidance System for Satellite
Rendezvous,” *Journal of the Aerospace Sciences* 27(9), 1960, pp. 653–658,
doi:10.2514/8.8704. These citations are external to the implementation;
`reference/SOURCE.md` records the repository's controlled convention.

Let \(\theta=nt\), \(s=\sin\theta\), and \(c=\cos\theta\). Then
\(X(t)=\Phi(t)X(0)\), with

\[
\Phi_{rr}=\begin{bmatrix}4-3c&0&0\\6(s-\theta)&1&0\\0&0&c\end{bmatrix},
\quad
\Phi_{rv}=\begin{bmatrix}s/n&2(1-c)/n&0\\2(c-1)/n&(4s-3\theta)/n&0\\0&0&s/n\end{bmatrix},
\]
\[
\Phi_{vr}=\begin{bmatrix}3ns&0&0\\6n(c-1)&0&0\\0&0&-ns\end{bmatrix},
\quad
\Phi_{vv}=\begin{bmatrix}c&2s&0\\-2s&4c-3&0\\0&0&c\end{bmatrix}.
\]

## Code and test mapping

| Cited block / terms | Implementation | Units | Direct regression evidence |
| --- | --- | --- | --- |
| \(\Phi_{rr}\): \(4-3c\), \(6(s-\theta)\), 1, \(c\) | `src/cw.py::cw_stm`, `phi_rr` | dimensionless | `tests/test_cw.py::test_cw_stm_blocks_match_cited_quarter_orbit_terms_and_units` |
| \(\Phi_{rv}\): \(s/n\), \(2(1-c)/n\), \(2(c-1)/n\), \((4s-3\theta)/n\) | `phi_rv` | seconds | same test; targeting benchmark exercises its use |
| \(\Phi_{vr}\): \(3ns\), \(6n(c-1)\), \(-ns\) | `phi_vr` | s⁻¹ | same test |
| \(\Phi_{vv}\): \(c\), \(2s\), \(-2s\), \(4c-3\) | `phi_vv` | dimensionless | same test |
| \(\Phi(0)=I_6\) | all blocks, `cw_stm` | n/a | `test_cw_stm_identity_at_zero_time`, absolute tolerance `1e-15` |

The STM uses four 3×3 arrays and `hstack`/`vstack`, so its output is 6×6 and
its row/column ordering is the documented state ordering. The zero-time test
uses an exact zero argument, where IEEE double-precision `sin(0)` and
`cos(0)` give the asserted identity; it is a regression tolerance rather than
a claim about arbitrary numerical cancellation.

## Audit conclusion

No STM sign, term, dimension, ordering, or `t=0` identity defect was found.
The implementation matches the cited circular-chief CW block solution. TJC-1.3
therefore makes no physics-code equation change; it adds explicit convention
and assumption documentation plus focused block and identity regressions.

## Assumptions and unsupported regimes

This is the linearized, unperturbed, circular-chief model. It is intended for
small relative separations/velocities in local LVLH/RIC geometry. It does not
validate eccentric chief motion, global phasing or large separations,
perturbations, thrust during coast, or accuracy after unqualified long
propagation. These limitations are also stated in `src/cw.py`,
`reference/SOURCE.md` §B, and the educational STM lesson. Singular
`\Phi_{rv}` targeting behavior is deliberately retained for TJC-1.4; this
audit does not alter two-burn targeting scope.
