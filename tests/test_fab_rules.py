"""Fab presets must encode the manufacturer limits the router relies on."""
import pytest

import fab_rules


def test_jlcpcb_two_layer_via_minimums():
    r = fab_rules.rules("jlcpcb", 2)
    assert r["min_through_hole_diameter"] >= 0.3
    assert r["min_via_diameter"] >= 0.5


def test_default_two_layer_via_respects_preset():
    d, h = fab_rules.DEFAULT_VIA[2]
    r = fab_rules.rules("jlcpcb", 2)
    assert h >= r["min_through_hole_diameter"] and d >= r["min_via_diameter"]
    assert (d - h) / 2 >= r["min_via_annular_width"]


@pytest.mark.parametrize("layers", [4, 6, 8, 12])
def test_multilayer_presets(layers):
    r = fab_rules.rules("jlcpcb", layers)
    d, h = fab_rules.DEFAULT_VIA[min(layers, 6)]
    assert h >= r["min_through_hole_diameter"]


def test_override_and_unknown_fab():
    assert fab_rules.rules("jlcpcb", 2, min_copper_edge_clearance=0.5)["min_copper_edge_clearance"] == 0.5
    with pytest.raises(KeyError):
        fab_rules.rules("nofab", 2)
