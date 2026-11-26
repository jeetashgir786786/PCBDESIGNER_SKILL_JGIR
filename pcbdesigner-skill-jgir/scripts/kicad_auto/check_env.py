#!/usr/bin/env python3
"""Check everything the kicad_auto toolkit needs and say how to install what is missing.
usage: python3 check_env.py"""
import shutil, subprocess, importlib, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def ok(b): return 'OK ' if b else 'MISSING'
rows = []
def chk(name, good, need, fix):
    rows.append((name, good, need, fix))

v = None
try:
    v = subprocess.run(['kicad-cli', 'version'], capture_output=True, text=True).stdout.strip()
except FileNotFoundError:
    pass
chk('kicad-cli', bool(v), 'all steps', 'install KiCad 7+ (Ubuntu: sudo apt install kicad)')
try:
    import pcbnew  # noqa
    pc = True
except Exception:
    pc = False
chk('pcbnew python module', pc, 'build/route/verify/fab',
    'use the Python that ships with KiCad (Windows: KiCad command prompt; macOS: KiCad.app python; Linux: system python3)')
try:
    import kenv; kenv.setup(); lib = True
except Exception:
    lib = False
chk('KiCad libraries', lib, 'build', 'set KICAD_SHARE=<dir with symbols/ footprints/ 3dmodels/>')
java = shutil.which('java')
chk('java (17+)', bool(java), 'route', 'sudo apt install openjdk-17-jre  (or any Java 17+)')
jar = next((p for p in [os.environ.get('FREEROUTING_JAR'), '/opt/fr/freerouting.jar',
                        os.path.expanduser('~/.local/share/freerouting/freerouting.jar')] if p and os.path.exists(p)), None)
chk('freerouting.jar', bool(jar), 'route', 'bash get_freerouting.sh')
chk('xvfb-run', bool(shutil.which('xvfb-run')) or os.name == 'nt' or sys.platform == 'darwin', 'route/images3d on headless Linux',
    'sudo apt install xvfb')
for m, need in (('numpy', 'route (A* finisher)'), ('PIL', 'route (A* finisher)'), ('cadquery', 'placeholder 3D models'),
                ('trimesh', 'GLB export'), ('OCP', 'GLB export')):
    try:
        importlib.import_module(m); g = True
    except Exception:
        g = False
    chk(m, g, need, f'pip install {"pillow" if m == "PIL" else ("cadquery" if m == "OCP" else m)}')
for t, need, fix in (('rsvg-convert', 'images2d', 'sudo apt install librsvg2-bin'), ('convert', 'images2d', 'sudo apt install imagemagick'),
                     ('xdotool', 'images3d on KiCad 7/8', 'sudo apt install xdotool'), ('import', 'images3d on KiCad 7/8', 'imagemagick')):
    chk(t, bool(shutil.which(t)), need, fix)
print('KiCad version:', v or 'not found')
for n, g, need, fix in rows:
    print(f'{ok(g)}  {n:22s} needed for: {need:34s}{"" if g else "-> " + fix}')
core = all(g for n, g, *_ in rows[:3])
print('\ncore (build/verify/fab):', 'READY' if core else 'NOT READY')
print('routing:', 'READY' if core and java and jar else 'NOT READY')
