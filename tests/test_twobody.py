import numpy as np

from src.twobody import orbital_period, propagate_cartesian_state


def test_orbital_period_positive():
    mu = 3.986004418e14
    a = 6778e3
    assert orbital_period(mu, a) > 0


def test_cartesian_propagation_runs():
    mu = 3.986004418e14
    state0 = np.array([6778e3, 0.0, 0.0, 0.0, 7670.0, 0.0])
    state1 = propagate_cartesian_state(state0, mu, 60.0, steps=200)
    assert state1.shape == (6,)
    assert np.isfinite(state1).all()
