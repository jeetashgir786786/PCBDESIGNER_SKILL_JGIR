"""Locate KiCad install paths and set the 3D-model env vars. Works for KiCad 7/8/9 on Linux/macOS/Windows
(override with KICAD_SHARE=<dir containing symbols/ footprints/ 3dmodels/>)."""
import os, glob, subprocess

def share_dir():
    env = os.environ.get('KICAD_SHARE')
    if env and os.path.isdir(env):
        return env
    cands = ['/usr/share/kicad', '/usr/local/share/kicad',
             '/Applications/KiCad/KiCad.app/Contents/SharedSupport']
    cands += sorted(glob.glob(r'C:\Program Files\KiCad\*\share\kicad'), reverse=True)
    for c in cands:
        if os.path.isdir(os.path.join(c, 'footprints')):
            return c
    raise RuntimeError('KiCad library folder not found; set KICAD_SHARE')

SHARE = None
def setup():
    global SHARE
    SHARE = share_dir()
    m = os.path.join(SHARE, '3dmodels')
    for v in ('KICAD6_3DMODEL_DIR', 'KICAD7_3DMODEL_DIR', 'KICAD8_3DMODEL_DIR', 'KICAD9_3DMODEL_DIR'):
        os.environ.setdefault(v, m)
    return SHARE

def sym_dir(): return os.path.join(SHARE or setup(), 'symbols')
def fp_dir(): return os.path.join(SHARE or setup(), 'footprints')

def kicad_version():
    try:
        return subprocess.run(['kicad-cli', 'version'], capture_output=True, text=True).stdout.strip()
    except FileNotFoundError:
        return None

def major():
    v = kicad_version()
    return int(v.split('.')[0]) if v else None
