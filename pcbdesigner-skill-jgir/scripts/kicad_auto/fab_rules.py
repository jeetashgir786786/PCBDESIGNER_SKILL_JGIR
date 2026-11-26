"""Design-rule presets for common fabs. Values are a planning snapshot (checked Nov 2026 against the
fab's published capability pages) - confirm on the live capability page before release.
Units: mm. Returned dict goes straight into the .kicad_pro 'rules' block."""

PRESETS = {
    # JLCPCB standard (non-advanced) process
    ('jlcpcb', 2): dict(min_clearance=0.127, min_track_width=0.127, min_via_diameter=0.5, min_via_annular_width=0.1,
                        min_through_hole_diameter=0.3, min_hole_clearance=0.25, min_hole_to_hole=0.25,
                        min_copper_edge_clearance=0.3),
    ('jlcpcb', 4): dict(min_clearance=0.1, min_track_width=0.1, min_via_diameter=0.4, min_via_annular_width=0.1,
                        min_through_hole_diameter=0.2, min_hole_clearance=0.25, min_hole_to_hole=0.25,
                        min_copper_edge_clearance=0.3),
    ('jlcpcb', 6): dict(min_clearance=0.09, min_track_width=0.09, min_via_diameter=0.4, min_via_annular_width=0.1,
                        min_through_hole_diameter=0.2, min_hole_clearance=0.25, min_hole_to_hole=0.25,
                        min_copper_edge_clearance=0.3),
    # PCBWay standard
    ('pcbway', 2): dict(min_clearance=0.127, min_track_width=0.127, min_via_diameter=0.45, min_via_annular_width=0.15,
                        min_through_hole_diameter=0.3, min_hole_clearance=0.25, min_hole_to_hole=0.3,
                        min_copper_edge_clearance=0.3),
    ('pcbway', 4): dict(min_clearance=0.1, min_track_width=0.1, min_via_diameter=0.45, min_via_annular_width=0.15,
                        min_through_hole_diameter=0.25, min_hole_clearance=0.25, min_hole_to_hole=0.3,
                        min_copper_edge_clearance=0.3),
}

COMMON = dict(min_silk_clearance=0.0, solder_mask_clearance=0.0, solder_mask_min_width=0.0, min_microvia_diameter=0.2,
              min_microvia_drill=0.1, use_height_for_length_calcs=True, allow_blind_buried_vias=False,
              allow_microvias=False)

# recommended routing via (diameter, drill) that keeps a margin over the minimums
DEFAULT_VIA = {2: (0.6, 0.3), 4: (0.45, 0.2), 6: (0.45, 0.2)}


def rules(fab='jlcpcb', layers=2, **override):
    key = (fab.lower(), min(layers, 6) if layers >= 4 else 2)
    if key not in PRESETS:
        raise KeyError(f'no preset for {key}; known: {sorted(PRESETS)}')
    r = dict(PRESETS[key]); r.update(COMMON); r.update(override)
    return r
