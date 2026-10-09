import numpy as np
import pytest

from src.verify import (
    LVLHTransformationError,
    _absolute_to_rel_lvlh,
    _lvlh_basis,
    _rel_lvlh_to_absolute,
    compare_cw_two_body,
)


def test_model_validity_warning_triggers():
    cw_state = np.zeros(6)
    tb_state = np.array([100.0, 0.0, 0.0, 0.0, 0.2, 0.0])
    result = compare_cw_two_body(cw_state, tb_state, pos_tol_m=10.0, vel_tol_mps=0.05)
    assert "MODEL VALIDITY WARNING" in result.warnings


def _chief_state():
    return np.array([7_000_000.0, 1_000_000.0, -500_000.0]), np.array([-900.0, 7_300.0, 1_200.0])


def test_lvlh_basis_is_orthonormal_and_right_handed():
    chief_pos, chief_vel = _chief_state()
    rotation, _ = _lvlh_basis(chief_pos, chief_vel)
    np.testing.assert_allclose(rotation.T @ rotation, np.eye(3), rtol=0.0, atol=1e-15)
    np.testing.assert_allclose(np.cross(rotation[:, 0], rotation[:, 1]), rotation[:, 2], rtol=0.0, atol=1e-15)
    assert np.linalg.det(rotation) == pytest.approx(1.0, abs=1e-15)


def test_lvlh_inertial_round_trips_preserve_state_and_deputy_subtraction_direction():
    chief_pos, chief_vel = _chief_state()
    n = 0.00105
    relative = np.array([125.0, -240.0, 32.0, 0.08, -0.11, 0.03])
    deputy_pos, deputy_vel = _rel_lvlh_to_absolute(chief_pos, chief_vel, relative, n)
    recovered_relative = _absolute_to_rel_lvlh(chief_pos, chief_vel, deputy_pos, deputy_vel, n)
    np.testing.assert_allclose(recovered_relative, relative, rtol=0.0, atol=3e-11)
    recovered_deputy = _rel_lvlh_to_absolute(chief_pos, chief_vel, recovered_relative, n)
    np.testing.assert_allclose(recovered_deputy[0], deputy_pos, rtol=0.0, atol=2e-9)
    np.testing.assert_allclose(recovered_deputy[1], deputy_vel, rtol=0.0, atol=2e-12)


def test_nonzero_relative_velocity_includes_rotating_frame_transport_term():
    chief_pos = np.array([7_000_000.0, 0.0, 0.0])
    chief_vel = np.array([0.0, 7_546.0, 0.0])
    n = 0.001
    relative = np.array([100.0, 0.0, 0.0, 0.2, -0.1, 0.05])
    deputy_pos, deputy_vel = _rel_lvlh_to_absolute(chief_pos, chief_vel, relative, n)
    # omega × r = +0.1 m/s along inertial y: omitting it would give -0.1 m/s.
    np.testing.assert_allclose(deputy_vel - chief_vel, np.array([0.2, 0.0, 0.05]), rtol=0.0, atol=1e-15)
    np.testing.assert_allclose(_absolute_to_rel_lvlh(chief_pos, chief_vel, deputy_pos, deputy_vel, n), relative, rtol=0.0, atol=1e-14)


@pytest.mark.parametrize(
    ("chief_pos", "chief_vel", "message"),
    [
        (np.zeros(3), np.array([0.0, 1.0, 0.0]), "position must be nonzero"),
        (np.array([1.0, 0.0, 0.0]), np.zeros(3), "must not be collinear"),
        (np.array([1.0, 0.0, 0.0]), np.array([2.0, 0.0, 0.0]), "must not be collinear"),
    ],
)
def test_degenerate_chief_states_are_rejected_explicitly(chief_pos, chief_vel, message):
    with pytest.raises(LVLHTransformationError, match=message):
        _lvlh_basis(chief_pos, chief_vel)
