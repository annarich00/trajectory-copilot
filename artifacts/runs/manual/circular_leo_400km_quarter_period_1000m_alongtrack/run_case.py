import sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.model_selector import ModelSelectionCase
from src.workflow import RendezvousCase, run_rendezvous_workflow
from src.cw import mean_motion

MU = 398600441800000.0          # m^3/s^2, specified (398600.4418 km^3/s^2)
R_EARTH = 6378137.0             # m, specified
ALT = 400000.0                  # m, specified
R_REF = R_EARTH + ALT           # m, derived = 6778137.0
TRANSFER_S = 1388.406068        # s, specified

n = mean_motion(MU, R_REF)

model_case = ModelSelectionCase(
    circularity="supported",
    frame="supported",
    other_physics="supported",
    maneuver_assumptions="supported",
    reference_radius_m=R_REF,
    relative_separation_m=1000.0,
    transfer_time_s=TRANSFER_S,
    mean_motion_rad_s=n,
)

case = RendezvousCase(
    case_id="circular_leo_400km_quarter_period_1000m_alongtrack",
    readiness="READY_TO_SOLVE",
    model_selection_case=model_case,
    mu_m3_s2=MU,
    reference_radius_m=R_REF,
    initial_relative_state=[0.0, 1000.0, 0.0, 0.0, 0.0, 0.0],
    final_relative_state=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    transfer_time_s=TRANSFER_S,
    pos_tol_m=1.0,
    vel_tol_mps=0.001,
    dv_tol_mps=0.001,
)

output_dir = Path(__file__).resolve().parent
result = run_rendezvous_workflow(
    case,
    output_dir=output_dir,
    gmat_executable="GmatConsole-R2026a",
)

data = result.to_dict()
(output_dir / "workflow_result.json").write_text(json.dumps(data, indent=2, default=str))

print("outcome:", result.outcome)
print("verified:", result.verified)
print("verification_status:", result.verification_status)
print("trust_statement:", result.trust_statement)
report = data["unified_verification_report"]
if report:
    comp = report["comparison"]
    solver = report["solver"]
    print("solver.status:", solver["status"])
print(json.dumps({k: data["artifacts"].get(k) for k in ("generated_script", "trajectory_screenshot", "screenshot_source", "gui_screenshot_attempt", "report_files")}, indent=2, default=str))
