import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_slice_generates_gmat_script_report_and_plot_without_false_verification(tmp_path):
    completed = subprocess.run(
        [sys.executable, 'scripts/run_cw_gmat_slice.py', '--output-dir', str(tmp_path), '--gmat', 'definitely-not-gmat'],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert completed.returncode == 1
    result = json.loads((tmp_path / 'verification_result.json').read_text())
    assert result['verified'] is False
    assert result['gmat']['attempted'] is False
    assert result['trajectory_artifact_nonempty'] is True
    assert (tmp_path / 'generated_cw_rendezvous.script').stat().st_size > 0
    assert result['cw']['targeting_status'] == 'unique'
    assert result['cw']['total_delta_v_mps'] > 0
    assert result['comparison']['tolerances']['position_m'] == 1.0


def test_slice_reports_infeasible_structured_targeting_without_gmat_or_artifact(tmp_path, monkeypatch):
    import scripts.run_cw_gmat_slice as slice_runner

    class InfeasibleTargeting:
        feasible = False
        status = 'singular-infeasible'
        reason = 'terminal position is unreachable'
        condition_number = float('inf')
        rank = 1
        reachability_residual_m = 2.0

    monkeypatch.setattr(slice_runner, 'two_burn_targeting', lambda *args, **kwargs: InfeasibleTargeting())
    monkeypatch.setattr(sys, 'argv', ['run_cw_gmat_slice.py', '--output-dir', str(tmp_path)])
    assert slice_runner.main() == 1
    result = json.loads((tmp_path / 'verification_result.json').read_text())
    assert result['verified'] is False
    assert result['cw']['targeting_status'] == 'singular-infeasible'
    assert 'targeting infeasible' in result['verification_status']
    assert result['gmat']['attempted'] is False
    assert result['trajectory_artifact'] is None
    assert result['trajectory_artifact_nonempty'] is False
    assert not (tmp_path / 'generated_cw_rendezvous.script').exists()
