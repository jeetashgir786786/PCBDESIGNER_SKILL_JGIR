"""drc.py turns KiCad DRC reports into the counts the router and verify gate act on."""
import drc
from conftest import FIXTURES


def test_clean_routed_report():
    s = drc.summary(FIXTURES / "drc_routed.rpt")
    assert s["unconnected"] == 0
    assert s["errors"] == 0
    assert s["warnings"] == 1
    assert ("silk_over_copper", "warning") in s["by"]


def test_placement_report_lists_unconnected_nets():
    s = drc.summary(FIXTURES / "drc_placement.rpt")
    assert s["unconnected"] == 22
    assert s["unconnected_nets"]["3V3"] == 8
    assert {"USB_DP", "USB_DN", "VBUS"} <= set(s["unconnected_nets"])


def test_open_net_is_reported_by_name():
    s = drc.summary(FIXTURES / "drc_open_net.rpt")
    assert s["unconnected"] == 1
    assert s["unconnected_nets"] == {"SPI_CS": 1}
    assert s["warnings"] == 2
    assert s["errors"] == 0


def test_items_carry_coordinates():
    v = drc.parse(FIXTURES / "drc_open_net.rpt")
    u = [x for x in v if x["type"] == "unconnected_items"][0]
    x, y, text = u["items"][0]
    assert isinstance(x, float) and isinstance(y, float)
    assert "SPI_CS" in text


def test_fmt_is_one_line():
    line = drc.fmt(drc.summary(FIXTURES / "drc_routed.rpt"))
    assert "unconnected=0" in line and "errors=0" in line and "\n" not in line
