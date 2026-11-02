# GMAT Open-Source Mission Script Examples — Research Log (TJC-10)

Research-only index of open-source GMAT (General Mission Analysis Tool) `.script` mission
examples collected from the public internet, for use as a reference corpus by a later task
(TJC-11). This log and the files under `research/gmat_examples_raw/` are purely additive;
no file under `src/`, `scripts/`, `tests/`, or `examples/` was modified to produce them.

All fetches below were performed live against GitHub (`github.com`, `api.github.com`,
`raw.githubusercontent.com`) from this sandbox on 2026-11-02. Internet access worked for
these GitHub hosts. One additional source (GMAT's Atlassian wiki, `gmat.atlassian.net`)
returned HTTP 200 but is a JavaScript single-page app that does not expose page content to
a plain `curl` fetch, so no script text was collected from it (see "Sources investigated
but not used" below).

## Source repositories used

| # | Repository | License found | Notes |
|---|---|---|---|
| A | [`nasa/GMAT`](https://github.com/nasa/GMAT) — official GMAT repository | **Apache License 2.0** (`License.txt` in repo root; confirmed via `GET /repos/nasa/GMAT/license` → `"license": {"key": "apache-2.0", ...}`) | Official sample-mission scripts live under `application/samples/`. Compatible, permissive license; redistribution with attribution is allowed under Apache-2.0 terms. |
| B | [`TridibeshChattoraj/GMAT_Mission_Portfolio`](https://github.com/TridibeshChattoraj/GMAT_Mission_Portfolio) | **No license file found; GitHub reports `license: null`.** Flagged as **license unknown/unclear**. | Personal astrodynamics-learning repo; scripts cover LEO propagation, elliptical/SSO orbits, inclination studies, ground-station contact. |
| C | [`hannxmarie/impulsive_manoeuvres_interplanetary`](https://github.com/hannxmarie/impulsive_manoeuvres_interplanetary) | **No license file found; GitHub reports `license: null`.** Flagged as **license unknown/unclear**. | Single Earth→Mars interplanetary transfer script using B-plane targeting. |
| D | [`iamxanadu/GMAT-SaturnIcyMoonExplorer`](https://github.com/iamxanadu/GMAT-SaturnIcyMoonExplorer) | **No license file found; GitHub reports `license: null`.** Flagged as **license unknown/unclear**. | Saturn-system (Enceladus/Titan) exploration mission scripts with user-defined celestial bodies and SPICE kernels. |

**License flag summary (per acceptance criterion #4):** Sources B, C, and D have **no
discoverable license** in their repositories (no `LICENSE`/`LICENSE.md`/`License.txt`
file, and the GitHub API's `license` field is `null` for all three). They are flagged here
explicitly rather than silently included. Only source A (`nasa/GMAT`, Apache-2.0) has a
clearly compatible, confirmed open-source license. The next task (building a
subagent-readable corpus) should decide whether/how material from B, C, D may be reused,
given the lack of a confirmed license.

## Sources investigated but not used

- `gmat.atlassian.net/wiki/spaces/GW/` (GMAT wiki/tutorial space) — `curl` returned
  HTTP 200, but the response body is a JavaScript-rendered single-page app shell with no
  static script/tutorial text in the HTML; no content could be extracted without a
  JS-executing browser, which is unavailable in this sandbox. No files were collected
  from this source. Not fabricated — simply not retrievable here.
- GitHub code search (`api.github.com/search/code`) requires authentication in this
  sandbox (`401 Requires authentication`), so repository code search was done via
  `api.github.com/search/repositories` instead (repository-level search, unauthenticated,
  worked fine).
- `VeluRagavendraS/Two-Spacecraft-Formation-Flying-and-Impulsive-Burn-Analysis-Using-GMAT`
  — repository exists and describes a two-spacecraft formation-flying + impulsive-burn
  GMAT mission, but its contents are only a `README.md` and screenshot images; it contains
  **no `.script` file**, so nothing was collected from it.

## Collected examples

Raw files are saved under `research/gmat_examples_raw/<source>/`. Each entry below gives
the exact URL fetched, the license status, and what the script demonstrates (read from the
script's own header comments and `Create`/command statements).

### Source A: `nasa/GMAT` official sample missions (Apache-2.0)

Fetched from `raw.githubusercontent.com/nasa/GMAT/main/application/samples/<file>`
(directory listing obtained via `api.github.com/repos/nasa/GMAT/contents/application/samples`).
`main` branch HEAD at fetch time: commit `c9b78bd1c8499845cb78fde315e1f761b6b06f1c`.

1. **Ex_HohmannTransfer.script**
   - URL: https://raw.githubusercontent.com/nasa/GMAT/main/application/samples/Ex_HohmannTransfer.script
   - License: Apache-2.0 (nasa/GMAT repo license)
   - Demonstrates: A classic two-burn Hohmann transfer mission, targeting the two
     impulsive burns to move between circular orbits. Mission type: **orbit transfer**.

2. **Ex_LunarTransfer.script**
   - URL: https://raw.githubusercontent.com/nasa/GMAT/main/application/samples/Ex_LunarTransfer.script
   - License: Apache-2.0
   - Demonstrates: Setting up and targeting a trans-lunar injection/transfer mission.
     Mission type: **lunar transfer**.

3. **Ex_GivenEpochGoToTheMoon.script**
   - URL: https://raw.githubusercontent.com/nasa/GMAT/main/application/samples/Ex_GivenEpochGoToTheMoon.script
   - License: Apache-2.0
   - Demonstrates: Starting from a fixed/given separation epoch, finding a trajectory
     that captures into lunar orbit. Mission type: **lunar transfer / targeting**.

4. **Ex_LCROSSTrajectory.script**
   - URL: https://raw.githubusercontent.com/nasa/GMAT/main/application/samples/Ex_LCROSSTrajectory.script
   - License: Apache-2.0
   - Demonstrates: Reproduction of the real LCROSS mission trajectory to lunar impact.
     Mission type: **lunar impactor / historical mission reproduction**.

5. **Ex_FiniteBurn.script**
   - URL: https://raw.githubusercontent.com/nasa/GMAT/main/application/samples/Ex_FiniteBurn.script
   - License: Apache-2.0
   - Demonstrates: Setting up fuel tanks and thrusters and using them in a finite
     (non-impulsive) maneuver sequence. Mission type: **propulsion / finite burn**.

6. **Ex_ElectricPropulsion.script**
   - URL: https://raw.githubusercontent.com/nasa/GMAT/main/application/samples/Ex_ElectricPropulsion.script
   - License: Apache-2.0
   - Demonstrates: A long-duration, low-thrust burn using an electric thruster. Mission
     type: **electric/low-thrust propulsion**.

7. **Ex_Attitude_NadirPointing.script**
   - URL: https://raw.githubusercontent.com/nasa/GMAT/main/application/samples/Ex_Attitude_NadirPointing.script
   - License: Apache-2.0
   - Demonstrates: Use of an attitude coordinate system defining a nadir-pointing
     attitude model. Mission type: **attitude/pointing**.

8. **Ex_Attitude_Spinner.script**
   - URL: https://raw.githubusercontent.com/nasa/GMAT/main/application/samples/Ex_Attitude_Spinner.script
   - License: Apache-2.0
   - Demonstrates: Use of a spinning (spinner) attitude model. Mission type:
     **attitude/pointing**.

9. **Ex_MarsOrbit.script**
   - URL: https://raw.githubusercontent.com/nasa/GMAT/main/application/samples/Ex_MarsOrbit.script
   - License: Apache-2.0
   - Demonstrates: Propagating a constellation of satellites in orbit around Mars.
     Mission type: **interplanetary / Mars orbit / constellation**.

10. **Ex_MMSSingleLunarSwingby.script**
    - URL: https://raw.githubusercontent.com/nasa/GMAT/main/application/samples/Ex_MMSSingleLunarSwingby.script
    - License: Apache-2.0
    - Demonstrates: Setting up a single lunar swingby with multiple targeting sequences,
      modeled on the MMS (Magnetospheric Multiscale) mission family. Mission type:
      **lunar swingby / gravity assist**.

11. **Ex_LEOStationKeeping.script**
    - URL: https://raw.githubusercontent.com/nasa/GMAT/main/application/samples/Ex_LEOStationKeeping.script
    - License: Apache-2.0
    - Demonstrates: Altitude-box stationkeeping maneuver sequence for a LEO spacecraft.
      Mission type: **station-keeping**.

12. **Tut_SimpleOrbitTransfer.script**
    - URL: https://raw.githubusercontent.com/nasa/GMAT/main/application/samples/Tut_SimpleOrbitTransfer.script
    - License: Apache-2.0
    - Demonstrates: The official GMAT Users Guide "Simple Orbit Transfer" tutorial
      script — introductory orbit-raising maneuver targeting. Mission type: **orbit
      transfer (tutorial)**.

### Source B: `TridibeshChattoraj/GMAT_Mission_Portfolio` — **license unknown/unclear**

`main` branch HEAD at fetch time: commit `29dbf52751115abe7dd03b90dbf275af75f13fc9`.
**No LICENSE file in this repo; GitHub API reports `license: null`. Flagged as
license unknown/unclear — do not assume redistribution rights.**

13. **Leo_V1_orbit_Visualisation_ISS.script**
    - URL: https://raw.githubusercontent.com/TridibeshChattoraj/GMAT_Mission_Portfolio/main/Leo_V1_orbit_Visualisation_ISS.script
    - License: unknown/unclear (no license file; `license: null`)
    - Demonstrates: LEO orbit propagation and visualization using ISS-like orbital
      parameters. Mission type: **LEO propagation / visualization**.

14. **ESOC_ground_Contact_one_satellite.script**
    - URL: https://raw.githubusercontent.com/TridibeshChattoraj/GMAT_Mission_Portfolio/main/ESOC%20Ground%20Station%20Coverage/ESOC%20ground%20Contact%20one%20satellite.script
    - License: unknown/unclear (no license file; `license: null`)
    - Demonstrates: Ground-station contact/coverage analysis for a single satellite
      against an ESOC (Darmstadt) ground station. Mission type: **ground-station
      contact/coverage analysis**.

15. **Elliptical_Orbit.script**
    - URL: https://raw.githubusercontent.com/TridibeshChattoraj/GMAT_Mission_Portfolio/main/Elliptical%20Orbit%20%2B%20SSO%20Analysis/Elliptical%20Orbit.script
    - License: unknown/unclear (no license file; `license: null`)
    - Demonstrates: Keplerian-dynamics propagation of an elliptical orbit. Mission
      type: **elliptical orbit propagation**.

16. **Inclination_098_SSO.script**
    - URL: https://raw.githubusercontent.com/TridibeshChattoraj/GMAT_Mission_Portfolio/main/Inclination%20Study/Inclination_098_SSO.script
    - License: unknown/unclear (no license file; `license: null`)
    - Demonstrates: Propagation of a Sun-synchronous orbit (SSO, ~98° inclination) as
      part of a comparative inclination study. Mission type: **SSO / inclination
      study**.

### Source C: `hannxmarie/impulsive_manoeuvres_interplanetary` — **license unknown/unclear**

`main` branch HEAD at fetch time: commit `b5e530c1c5873771e169a7e549adf55286c3dd7b`.
**No LICENSE file in this repo; GitHub API reports `license: null`. Flagged as
license unknown/unclear.**

17. **impulsive_trajectory_w001.script**
    - URL: https://raw.githubusercontent.com/hannxmarie/impulsive_manoeuvres_interplanetary/main/impulsive_trajectory_w001.script
    - License: unknown/unclear (no license file; `license: null`)
    - Demonstrates: An Earth-to-Mars interplanetary transfer for a "Human Mars Lander"
      spacecraft using impulsive maneuvers and B-plane targeting (VNB-frame burns
      targeting BdotT/BdotR), per the repo's README. Mission type: **interplanetary
      transfer / B-plane targeting**.

### Source D: `iamxanadu/GMAT-SaturnIcyMoonExplorer` — **license unknown/unclear**

`master` branch HEAD at fetch time: commit `c47aacb968a4b92aa1833338999c15c94c33d92b`.
**No LICENSE file in this repo; GitHub API reports `license: null`. Flagged as
license unknown/unclear.**

18. **ToEnceledus.script**
    - URL: https://raw.githubusercontent.com/iamxanadu/GMAT-SaturnIcyMoonExplorer/master/ToEnceledus.script
    - License: unknown/unclear (no license file; `license: null`)
    - Demonstrates: A mission to Saturn's icy moon Enceladus, defining user-defined
      celestial bodies (e.g. Titan) with SPICE kernels and NAIF IDs for high-fidelity
      outer-planet-system navigation. Mission type: **interplanetary / outer-planet
      moon exploration**.

## Summary

- **18 distinct examples collected** (exceeds the required minimum of 10), spanning
  mission types: orbit transfer (Hohmann, simple transfer), lunar transfer/swingby/impact,
  finite and electric propulsion, attitude/pointing (nadir, spinner), Mars orbit
  constellation, LEO station-keeping, LEO/elliptical/SSO propagation, ground-station
  contact analysis, Earth-Mars interplanetary B-plane targeting, and outer-planet
  (Saturn/Enceladus) moon exploration.
- **4 distinct source repositories**: the official `nasa/GMAT` repository plus three
  independent GitHub repositories authored by different individuals.
- **License status**: only source A (`nasa/GMAT`, Apache-2.0) has a confirmed,
  compatible open-source license. Sources B, C, and D are explicitly flagged as
  **license unknown/unclear** — no LICENSE file was found in any of them, and this must
  be resolved (e.g. by excluding them, or by contacting the authors) before any
  redistribution decision is made in a follow-up task.
