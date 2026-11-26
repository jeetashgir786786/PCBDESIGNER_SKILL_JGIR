"""The bundled example spec must be internally consistent (runs without KiCad)."""
import importlib.util
import os

from conftest import SKILL


def load(layers):
    os.environ["LAYERS"] = str(layers)
    p = SKILL / "scripts" / "kicad_auto" / "examples" / "usb_uart_spec.py"
    spec = importlib.util.spec_from_file_location(f"usb_uart_{layers}", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_refs_unique_and_placed():
    m = load(2)
    parts = m.parts()
    refs = [p["ref"] for p in parts]
    assert len(refs) == len(set(refs))
    assert all("place" in p for p in parts if p.get("fp") and not p.get("virtual"))


def test_zone_nets_exist_on_pads():
    for layers in (2, 4):
        m = load(layers)
        pad_nets = {n for p in m.parts() for n in p["pins"].values()}
        for z in m.BOARD["zones"]:
            assert z["net"] in pad_nets
        assert len([z for z in m.BOARD["zones"] if z["layer"].startswith("In")]) == (2 if layers == 4 else 0)


def test_every_net_has_two_or_more_pins():
    m = load(2)
    count = {}
    for p in m.parts():
        for n in p["pins"].values():
            count[n] = count.get(n, 0) + 1
    singles = [n for n, c in count.items() if c < 2]
    assert not singles, f"single-pin nets: {singles}"
