import numpy as np
import pytest

colorspacious = pytest.importorskip("colorspacious")

from plumaria import cvd

# Paleta de teste com uma máxima confusão vermelho/verde sob deuteranopia.
PALETTE = ["#D62728", "#2CA02C", "#1F77B4", "#FF7F0E"]


def test_simulate_cvd_shape_and_range():
    rgb = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    out = cvd.simulate_cvd(rgb, "deuteranomaly")
    assert out.shape == rgb.shape
    assert out.min() >= 0.0 and out.max() <= 1.0


def test_simulate_cvd_severity_zero_is_identity():
    rgb = np.array([0.2, 0.6, 0.9])
    out = cvd.simulate_cvd(rgb, "protanomaly", severity=0)
    assert np.allclose(out, rgb, atol=1e-6)


def test_simulate_cvd_invalid_type_raises():
    with pytest.raises(ValueError):
        cvd.simulate_cvd([1.0, 0.0, 0.0], "nao_existe")


def test_simulate_cvd_invalid_severity_raises():
    with pytest.raises(ValueError):
        cvd.simulate_cvd([1.0, 0.0, 0.0], "deuteranomaly", severity=200)


def test_delta_e_matrix_symmetric_zero_diagonal():
    m = cvd.delta_e_matrix(PALETTE)
    assert m.shape == (4, 4)
    assert np.allclose(m, m.T)
    assert np.allclose(np.diag(m), 0.0)
    assert (m[np.triu_indices(4, k=1)] > 0).all()


def test_min_pairwise_delta_e_positive():
    assert cvd.min_pairwise_delta_e(PALETTE) > 0


def test_cvd_reduces_separability():
    # Daltonismo nunca deve aumentar a menor separação de um par vermelho/verde.
    normal = cvd.min_pairwise_delta_e(PALETTE)
    deut = cvd.min_pairwise_delta_e(PALETTE, cvd_type="deuteranomaly")
    assert deut <= normal


def test_requires_at_least_two_colors():
    with pytest.raises(ValueError):
        cvd.min_pairwise_delta_e(["#123456"])


def test_separability_report_structure():
    report = cvd.separability_report(PALETTE)
    for key in ("normal", "protanomaly", "deuteranomaly", "tritanomaly"):
        assert isinstance(report[key], float)
    worst_cond, worst_de = report["worst"]
    assert worst_cond in ("normal",) + cvd.CVD_TYPES
    # O pior caso é, por definição, o menor ΔE entre todas as condições.
    assert worst_de == min(report[c] for c in ("normal",) + cvd.CVD_TYPES)
    assert isinstance(report["safe"], bool)
    assert report["safe"] == (worst_de >= cvd.JND_THRESHOLD)
