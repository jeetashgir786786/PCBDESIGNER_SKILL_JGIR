"""Offscreen render of a GLB with pyrender (EGL/OSMesa). usage: render.py in.glb out.png az el [dist_factor] [w h]"""
import os, sys, math
os.environ.setdefault('PYOPENGL_PLATFORM', 'egl')
import numpy as np, trimesh, pyrender
from PIL import Image

def look_at(eye, target, up=(0, 0, 1)):
    f = np.array(target, float) - eye; f /= np.linalg.norm(f)
    u = np.array(up, float)
    s = np.cross(f, u)
    if np.linalg.norm(s) < 1e-6:
        s = np.cross(f, [0, 1, 0])
    s /= np.linalg.norm(s); u = np.cross(s, f)
    m = np.eye(4); m[:3, 0] = s; m[:3, 1] = u; m[:3, 2] = -f; m[:3, 3] = eye
    return m

def render(glb, out, az=-35, el=35, distf=1.6, w=1600, h=1200, bg=(245, 246, 248), target=None, fov=30, skip=(), alpha=None):
    tm = trimesh.load(glb, force='scene')
    sc = pyrender.Scene(bg_color=np.array(list(bg) + [255]) / 255.0, ambient_light=[0.35, 0.35, 0.38])
    for name, g in tm.geometry.items():
        try:
            node_tf = tm.graph[ [n for n in tm.graph.nodes_geometry if tm.graph[n][1] == name][0] ][0]
        except Exception:
            node_tf = np.eye(4)
        mat = None
        try:
            bc = tuple(int(v) for v in g.visual.material.baseColorFactor[:3])
            if any(sum(abs(a - b) for a, b in zip(bc, sk)) < 4 for sk in skip):
                continue
        except Exception:
            pass
        try:
            pm = g.visual.material
            mat = pyrender.MetallicRoughnessMaterial(baseColorFactor=np.array(pm.baseColorFactor) / 255.0,
                                                     metallicFactor=pm.metallicFactor or 0.1, roughnessFactor=pm.roughnessFactor or 0.6)
        except Exception:
            pass
        sc.add(pyrender.Mesh.from_trimesh(g, material=mat, smooth=False), pose=node_tf)
    b = tm.bounds
    c = (b[0] + b[1]) / 2 if target is None else np.array(target)
    r = np.linalg.norm(b[1] - b[0]) / 2
    d = r / math.tan(math.radians(fov / 2)) * distf / 1.6
    a, e = math.radians(az), math.radians(el)
    eye = c + d * np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
    cam = pyrender.PerspectiveCamera(yfov=math.radians(fov), aspectRatio=w / h, znear=d / 50, zfar=d * 10)
    pose = look_at(eye, c)
    sc.add(cam, pose=pose)
    for (laz, lel, inten) in [(az + 40, 60, 3.2), (az - 120, 30, 1.6), (az + 180, -20, 0.8)]:
        la, le = math.radians(laz), math.radians(lel)
        dl = pyrender.DirectionalLight(color=np.ones(3), intensity=inten)
        sc.add(dl, pose=look_at(c + np.array([math.cos(le) * math.cos(la), math.cos(le) * math.sin(la), math.sin(le)]) * d, c))
    rr = pyrender.OffscreenRenderer(w, h)
    col, _ = rr.render(sc, flags=pyrender.RenderFlags.SHADOWS_DIRECTIONAL)
    rr.delete()
    Image.fromarray(col).save(out)

if __name__ == '__main__':
    a = sys.argv
    skip = []
    if len(a) > 6 and a[6]:
        for t in a[6].split(';'):
            skip.append(tuple(int(v) for v in t.split(',')))
    render(a[1], a[2], float(a[3]) if len(a) > 3 else -35, float(a[4]) if len(a) > 4 else 35,
           float(a[5]) if len(a) > 5 else 1.6, skip=skip)
