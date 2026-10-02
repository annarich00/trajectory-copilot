import numpy as np

from src.verify import compare_cw_two_body


def test_model_validity_warning_triggers():
    cw_state = np.zeros(6)
    tb_state = np.array([100.0, 0.0, 0.0, 0.0, 0.2, 0.0])
    result = compare_cw_two_body(cw_state, tb_state, pos_tol_m=10.0, vel_tol_mps=0.05)
    assert "MODEL VALIDITY WARNING" in result.warnings
