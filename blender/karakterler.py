"""Cebir Kaçışı karakterleri - Blender (bpy) ile prosedürel modelleme ve iskelet (rig).
Çalıştırma:  blender -b -P blender/karakterler.py -- web/karakterler.glb   (veya bpy modülüyle python)
Çıktı: iki kök düğüm (hero, cat). Kollar ve bacaklar tek parça, kemiklerle (skinning) bükülür.
Kemik adları: pelvis, head, shoulder_L/R, elbow_L/R, hip_L/R, knee_L/R, braid_L/R, braid2_L/R, eye_L/R
Kedi kemikleri aynı adlarla 'cat_' önekiyle başlar.
"""
import bpy, bmesh, math, os, sys, random
from mathutils import Vector, Matrix

OUT = sys.argv[-1] if sys.argv[-1].endswith('.glb') else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'web', 'karakterler.glb')
random.seed(7)
bpy.ops.wm.read_factory_settings(use_empty=True)
COL = bpy.context.scene.collection

# ---------------------------------------------------------------- yardımcılar
def lin(h):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c) + (1,)
MATS = {}
def mat(name, color, rough=0.6, metal=0.0):
    if name in MATS: return MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = lin(color); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    MATS[name] = m; return m

def ss(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a))); return t * t * (3 - 2 * t)
def gauss(d, s): return math.exp(-(d / s) ** 2)

PARTS = []          # (nesne, ağırlık fonksiyonu) — mevcut karakter
def reg(o, wf):
    PARTS.append((o, wf)); return o

def obj_from_bm(name, bm, m, loc=(0, 0, 0), smooth=True):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); COL.objects.link(o); o.location = loc
    me.materials.append(m)
    if smooth:
        for p in me.polygons: p.use_smooth = True
    return o
def subsurf(o, lv=2):
    s = o.modifiers.new('sub', 'SUBSURF'); s.levels = lv; s.render_levels = lv; return o

def skin(name, verts, edges, radii, m, wf, lv=2):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, edges, []); me.update()
    o = bpy.data.objects.new(name, me); COL.objects.link(o); me.materials.append(m)
    sk = o.modifiers.new('skin', 'SKIN'); sk.use_smooth_shade = True
    sv = me.skin_vertices[0].data
    for i, r in enumerate(radii): sv[i].radius = r if isinstance(r, (tuple, list)) else (r, r)
    sv[0].use_root = True
    subsurf(o, lv); return reg(o, wf)
def chain(name, pts, radii, m, wf, lv=2):
    return skin(name, pts, [(i, i + 1) for i in range(len(pts) - 1)], radii, m, wf, lv)

def sphere(name, r, m, wf, loc, scale=(1, 1, 1), seg=(24, 12), shape=None, lv=1, uv=False):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg[0], v_segments=seg[1], radius=r, calc_uvs=uv)
    for v in bm.verts:
        v.co = Vector((v.co.x * scale[0], v.co.y * scale[1], v.co.z * scale[2]))
        if shape: v.co = shape(v.co)
    o = obj_from_bm(name, bm, m, loc)
    if lv: subsurf(o, lv)
    return reg(o, wf)

def torus(name, R, r, m, wf, loc, rot=(0, 0, 0), scale=(1, 1, 1), seg=(32, 10)):
    bm = bmesh.new(); rings = []
    for i in range(seg[0]):
        a = 2 * math.pi * i / seg[0]; ring = []
        for j in range(seg[1]):
            b = 2 * math.pi * j / seg[1]
            ring.append(bm.verts.new(((R + r * math.cos(b)) * math.cos(a) * scale[0], (R + r * math.cos(b)) * math.sin(a) * scale[1], r * math.sin(b) * scale[2])))
        rings.append(ring)
    for i in range(seg[0]):
        for j in range(seg[1]):
            bm.faces.new((rings[i][j], rings[(i + 1) % seg[0]][j], rings[(i + 1) % seg[0]][(j + 1) % seg[1]], rings[i][(j + 1) % seg[1]]))
    o = obj_from_bm(name, bm, m, loc); o.rotation_euler = rot
    return reg(o, wf)

def tube(name, pts, radius, m, wf, taper=None, res=6, flat=1.0, bev=2):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = radius; cu.bevel_resolution = bev; cu.use_fill_caps = False
    sp = cu.splines.new('NURBS'); sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p[0], p[1], p[2], 1); sp.points[i].radius = taper[i] if taper else 1.0
    sp.use_endpoint_u = True; sp.order_u = min(4, len(pts)); sp.resolution_u = res
    tmp = bpy.data.objects.new(name + '_c', cu); COL.objects.link(tmp)
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(tmp); bpy.data.curves.remove(cu)
    if flat != 1.0:
        c = sum((v.co for v in me.vertices), Vector()) / max(1, len(me.vertices))
        for v in me.vertices: v.co.y = c.y + (v.co.y - c.y) * flat
    o = bpy.data.objects.new(name, me); COL.objects.link(o); me.materials.append(m)
    for p in me.polygons: p.use_smooth = True
    return reg(o, wf)

def sneaker(name, L, Wd, sole_h, cx, cy, z0, m_sole, m_upper, m_toe, m_heel, m_collar, wf, toe_white=True):
    """Organik spor ayakkabı: ayak izi biçimli yuvarlatılmış taban + şekillendirilmiş üst."""
    bm = bmesh.new(); outline = []
    N = 40
    for i in range(N):
        a = 2 * math.pi * i / N
        yy = -math.cos(a) * L / 2                 # -y = burun
        f = (yy + L / 2) / L                      # 0 burun .. 1 topuk
        w = Wd / 2 * (0.86 + 0.18 * math.sin(math.pi * min(1, f * 1.4)) - 0.12 * f)
        outline.append(bm.verts.new((cx + math.sin(a) * w, cy + yy, z0)))
    face = bm.faces.new(outline)
    ext = bmesh.ops.extrude_face_region(bm, geom=[face])
    for v in ext['geom']:
        if isinstance(v, bmesh.types.BMVert): v.co.z += sole_h
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = obj_from_bm(name + '_sole', bm, m_sole)
    b = o.modifiers.new('bev', 'BEVEL'); b.width = sole_h * 0.35; b.segments = 2
    subsurf(o, 1); reg(o, wf)
    # üst kısım: burun alçak, topuk yüksek, bilek ağzı açık
    def up_shape(c):
        x, y, z = c.x, c.y, c.z
        f = (y / (L * 0.5) + 1) / 2              # 0 burun .. 1 topuk
        z = max(z, -0.002)
        z *= 0.55 + 0.75 * f
        x *= 1 - 0.1 * (1 - f)
        return Vector((x, y, z))
    sphere(name + '_upper', 1, m_upper, wf, (cx, cy + 0.004, z0 + sole_h * 0.9), scale=(Wd * 0.47, L * 0.47, Wd * 0.62), seg=(24, 12), shape=up_shape, lv=1)
    if toe_white:
        sphere(name + '_toe', 1, m_toe, wf, (cx, cy - L * 0.3, z0 + sole_h * 0.95), scale=(Wd * 0.44, L * 0.2, Wd * 0.3), seg=(16, 8), lv=1,
               shape=lambda c: Vector((c.x, c.y, max(c.z, 0) * 1.0)))
    sphere(name + '_heel', 1, m_heel, wf, (cx, cy + L * 0.4, z0 + sole_h + Wd * 0.3), scale=(Wd * 0.36, L * 0.09, Wd * 0.34), seg=(16, 8), lv=1)
    torus(name + '_collar', Wd * 0.3, Wd * 0.06, m_collar, wf, (cx, cy + L * 0.17, z0 + sole_h + Wd * 0.62), rot=(-0.25, 0, 0), scale=(1, 1.35, 1), seg=(24, 8))
    for k in range(4):   # bağcıklar
        yk = cy - L * 0.02 + k * L * 0.07 - L * 0.08
        tube(f'{name}_lace{k}', [(cx - Wd * 0.22, yk, z0 + sole_h + Wd * (0.48 + k * 0.035)), (cx, yk - 0.004, z0 + sole_h + Wd * (0.52 + k * 0.035)), (cx + Wd * 0.22, yk, z0 + sole_h + Wd * (0.48 + k * 0.035))],
             Wd * 0.025, m_toe if toe_white else m_collar, wf, res=4)

def planar_uv(o, cx, cz, w, h, back_uv=(0.04, 0.04), back_scale=0.06):
    """Önden düzlemsel UV; arka yarım küre dokunun düz (yüzsüz) köşesine eşlenir."""
    me = o.data; uv = me.uv_layers.new(name='UVMap') if not me.uv_layers else me.uv_layers[0]
    for loop in me.loops:
        co = me.vertices[loop.vertex_index].co
        if co.y > 0.0:
            uv.data[loop.index].uv = (back_uv[0] + back_scale * (0.5 + co.x / w), back_uv[1] + back_scale * (0.5 + co.z / h))
        else:
            uv.data[loop.index].uv = (0.5 + (co.x - cx) / w, 0.5 + (co.z - cz) / h)

def bake(o):
    me = bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    o.modifiers.clear(); old = o.data; o.data = me
    if old.users == 0: bpy.data.meshes.remove(old)

def build_rig(rig_name, root, bones):
    """bones: [(ad, baş, kuyruk, ebeveyn, bağlı)]"""
    ad = bpy.data.armatures.new(rig_name); arm = bpy.data.objects.new(rig_name, ad); COL.objects.link(arm); arm.parent = root
    bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode='EDIT')
    for name, h, t, par, con in bones:
        eb = ad.edit_bones.new(name); eb.head = h; eb.tail = t; eb.roll = 0
        if par: eb.parent = ad.edit_bones[par]; eb.use_connect = con
    bpy.ops.object.mode_set(mode='OBJECT')
    return arm

def finish(arm, bone_names):
    """Parçaları pişir, ağırlıkla, malzemeye göre birleştir, iskelete bağla."""
    bpy.context.view_layer.update()
    for o, wf in PARTS:
        bake(o)
        mw = o.matrix_world
        groups = {b: o.vertex_groups.new(name=b) for b in bone_names}
        for v in o.data.vertices:
            w = wf(mw @ v.co); tot = sum(w.values()) or 1
            for b, val in w.items():
                if val > 1e-4: groups[b].add([v.index], val / tot, 'REPLACE')
    by_mat = {}
    for o, _ in PARTS: by_mat.setdefault(o.data.materials[0].name, []).append(o)
    for mname, objs in by_mat.items():
        bpy.ops.object.select_all(action='DESELECT')
        for o in objs: o.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        if len(objs) > 1: bpy.ops.object.join()
        j = bpy.context.view_layer.objects.active; j.name = arm.name.replace('_rig', '') + '_' + mname
        j.parent = arm; md = j.modifiers.new('arm', 'ARMATURE'); md.object = arm
    PARTS.clear()

# ================================================================ KAHRAMAN (öğrenci)
SKIN = mat('hero_skin', '#f3cdb6', 0.55); FACE = mat('hero_face', '#f3cdb6', 0.55)
HOOD = mat('hero_hoodie', '#ece4d3', 0.92); HOODR = mat('hero_hoodie_rib', '#ddd3be', 0.95)
NAVY = mat('hero_collar', '#1e2a4f', 0.8); PANTS = mat('hero_pants', '#18181f', 0.85)
STRIPE = mat('hero_stripe', '#f4f4f4', 0.6); CORD = mat('hero_cord', '#121214', 0.7); METAL = mat('hero_metal', '#c9ced6', 0.25, 1.0)
SOLE = mat('hero_sole', '#f1ede3', 0.7); SUEDE = mat('hero_suede', '#c9b7a2', 0.95); SHOEW = mat('hero_shoe_white', '#f7f6f2', 0.5); SHOEB = mat('hero_shoe_black', '#1d1d22', 0.6)
HAIR = mat('hero_hair', '#6a452d', 0.5); HAIRD = mat('hero_hair_dark', '#4e301e', 0.55); HAIRC = mat('hero_hair_cap', '#5e3d27', 0.55)
TIE = mat('hero_hairtie', '#2a2a2e', 0.6); CHERRY = mat('hero_clip_red', '#d61f35', 0.22); LEAF = mat('hero_clip_green', '#3c9a46', 0.3)

hero = bpy.data.objects.new('hero', None); COL.objects.link(hero)
PZ = 0.86; SHZ = 1.28; ELZ = 1.01; HIPZ = 0.83; KNZ = 0.43; HEADZ = 1.435; HC = Vector((0, 0, 1.545)); HR = 0.125
BR = {s: (Vector((0.085 * s, 0.1, 1.485)), Vector((0.097 * s, 0.12, 1.205)), Vector((0.11 * s, 0.14, 0.925))) for s in (1, -1)}
rig = build_rig('hero_rig', hero, [
    ('pelvis', (0, 0, PZ), (0, 0, 1.1), None, False),
    ('head', (0, 0, HEADZ), (0, 0, 1.68), 'pelvis', False),
    ('eye_L', (0.046, -0.093, HC.z + 0.007), (0.046, -0.14, HC.z + 0.007), 'head', False),
    ('eye_R', (-0.046, -0.093, HC.z + 0.007), (-0.046, -0.14, HC.z + 0.007), 'head', False),
    ('shoulder_L', (0.19, 0, SHZ), (0.19, 0, ELZ), 'pelvis', False), ('elbow_L', (0.19, 0, ELZ), (0.19, 0, 0.765), 'shoulder_L', True),
    ('shoulder_R', (-0.19, 0, SHZ), (-0.19, 0, ELZ), 'pelvis', False), ('elbow_R', (-0.19, 0, ELZ), (-0.19, 0, 0.765), 'shoulder_R', True),
    ('hip_L', (0.088, 0, HIPZ), (0.088, 0, KNZ), 'pelvis', False), ('knee_L', (0.088, 0, KNZ), (0.088, 0, 0.03), 'hip_L', True),
    ('hip_R', (-0.088, 0, HIPZ), (-0.088, 0, KNZ), 'pelvis', False), ('knee_R', (-0.088, 0, KNZ), (-0.088, 0, 0.03), 'hip_R', True),
    ('braid_L', tuple(BR[1][0]), tuple(BR[1][1]), 'head', False), ('braid2_L', tuple(BR[1][1]), tuple(BR[1][2]), 'braid_L', True),
    ('braid_R', tuple(BR[-1][0]), tuple(BR[-1][1]), 'head', False), ('braid2_R', tuple(BR[-1][1]), tuple(BR[-1][2]), 'braid_R', True),
])
HB = ['pelvis', 'head', 'eye_L', 'eye_R', 'shoulder_L', 'elbow_L', 'shoulder_R', 'elbow_R', 'hip_L', 'knee_L', 'hip_R', 'knee_R', 'braid_L', 'braid2_L', 'braid_R', 'braid2_R']
W_PEL = lambda p: {'pelvis': 1}
W_HEAD = lambda p: {'head': 1}
def W_NECK(p): h = ss(HEADZ - 0.03, HEADZ + 0.04, p.z); return {'head': h, 'pelvis': 1 - h}
def W_ARM(side):
    def f(p):
        e = ss(ELZ + 0.045, ELZ - 0.045, p.z); t = ss(SHZ - 0.03, SHZ + 0.05, p.z)
        return {'elbow_' + side: e, 'shoulder_' + side: (1 - e) * (1 - t), 'pelvis': (1 - e) * t}
    return f
def W_LEG(side):
    def f(p):
        k = ss(KNZ + 0.045, KNZ - 0.045, p.z); t = ss(HIPZ - 0.04, HIPZ + 0.06, p.z)
        return {'knee_' + side: k, 'hip_' + side: (1 - k) * (1 - t), 'pelvis': (1 - k) * t}
    return f
def W_BRAID(side, s):
    a, m_, b = BR[s]
    def f(p):
        k = ss(m_.z + 0.06, m_.z - 0.06, p.z); h = ss(a.z - 0.02, a.z + 0.05, p.z)
        return {'braid2_' + side: k, 'braid_' + side: (1 - k) * (1 - h), 'head': (1 - k) * h}
    return f

# gövde
cv = [(0, 0, -0.07), (0, 0, 0.10), (0, 0, 0.28), (0, 0, 0.42), (0, 0, 0.52), (0.17, 0.0, 0.43), (-0.17, 0.0, 0.43)]
skin('hero_torso', [(x, y, z + PZ) for x, y, z in cv], [(0, 1), (1, 2), (2, 3), (3, 4), (3, 5), (3, 6)],
     [(0.185, 0.13), (0.172, 0.12), (0.19, 0.13), (0.175, 0.115), (0.07, 0.065), (0.075, 0.075), (0.075, 0.075)], HOOD, W_PEL)
torus('hero_hem', 0.178, 0.026, HOODR, W_PEL, (0, 0, PZ - 0.05), scale=(1, 0.72, 1))
torus('hero_neckband', 0.074, 0.018, HOODR, W_PEL, (0, 0.005, PZ + 0.505), rot=(0.12, 0, 0), scale=(1.1, 1, 1))
for s in (-1, 1): sphere(f'hero_hood_side_{s}', 0.06, HOOD, W_PEL, (0.075 * s, 0.06, PZ + 0.52), scale=(0.75, 1.0, 1.0))
sphere('hero_hood_back', 0.085, HOOD, W_PEL, (0, 0.115, PZ + 0.46), scale=(1.35, 0.45, 0.85))
torus('hero_collar', 0.056, 0.011, NAVY, W_PEL, (0, -0.008, PZ + 0.525), rot=(0.25, 0, 0))
for s in (-1, 1):
    tube(f'hero_cord_{s}', [(0.045 * s, -0.112, PZ + 0.475), (0.05 * s, -0.128, PZ + 0.40), (0.048 * s, -0.135, PZ + 0.32), (0.052 * s, -0.135, PZ + 0.255)], 0.0045, CORD, W_PEL)
    sphere(f'hero_tip_{s}', 0.0065, METAL, W_PEL, (0.052 * s, -0.135, PZ + 0.245), scale=(1, 1, 2.6), seg=(10, 6), lv=0)
chain('hero_neck', [(0, 0, PZ + 0.49), (0, 0, PZ + 0.60)], [0.045, 0.043], SKIN, W_NECK)

# kollar: omuzdan bileğe kesintisiz kol (dirsekte bükülür)
for s, side in ((1, 'L'), (-1, 'R')):
    x = 0.19 * s
    chain(f'hero_arm_{side}', [(0.165 * s, 0, SHZ + 0.035), (x, 0, SHZ - 0.01), (x, 0, SHZ - 0.14), (x, 0.004, ELZ), (x, 0, ELZ - 0.12), (x, 0, ELZ - 0.235)],
          [0.072, 0.068, 0.063, 0.058, 0.056, 0.059], HOOD, W_ARM(side))
    torus(f'hero_cuff_{side}', 0.048, 0.017, HOODR, W_ARM(side), (x, 0, ELZ - 0.237))
    skin(f'hero_hand_{side}', [(x, 0, ELZ - 0.235), (x, 0, ELZ - 0.29), (x, 0, ELZ - 0.345), (x, -0.032, ELZ - 0.29)], [(0, 1), (1, 2), (1, 3)],
         [0.028, (0.036, 0.017), (0.026, 0.013), 0.012], SKIN, W_ARM(side))

# bacaklar: kesintisiz pantolon (dizde bükülür) + organik ayakkabı
for s, side in ((1, 'L'), (-1, 'R')):
    x = 0.088 * s
    chain(f'hero_leg_{side}', [(x, 0, HIPZ + 0.07), (x, 0, HIPZ - 0.2), (x, 0, KNZ), (x, 0, KNZ - 0.2), (x, 0, 0.06)], [0.094, 0.086, 0.077, 0.079, 0.083], PANTS, W_LEG(side))
    tube(f'hero_stripe_{side}', [(x + 0.091 * s, 0, HIPZ + 0.03), (x + 0.085 * s, 0, HIPZ - 0.2), (x + 0.078 * s, 0, KNZ), (x + 0.08 * s, 0, KNZ - 0.2), (x + 0.084 * s, 0, 0.065)], 0.0035, STRIPE, W_LEG(side), res=8)
    sphere(f'hero_toggle_{side}', 0.011, SHOEB, W_LEG(side), (x + 0.06 * s, -0.045, 0.065), scale=(1, 1, 1.5), seg=(10, 6), lv=0)
    sneaker(f'hero_shoe_{side}', 0.27, 0.112, 0.042, x, -0.035, 0.0, SOLE, SUEDE, SHOEW, SHOEB, SHOEB, W_LEG(side))

# baş
def head_shape(c):
    x, y, z = c.x, c.y, c.z
    if z < 0:
        t = (-z / HR); x *= 1 - 0.30 * t ** 1.6
        if y < 0: y *= 1 - 0.10 * t
        z *= 1.08
    else: z *= 1.06
    if y > 0: y *= 1.06
    d = math.hypot(x, z + 0.02); y -= 0.011 * gauss(d, 0.016) * (1 if y < 0 else 0)
    for sx in (-0.046, 0.046):
        d = math.hypot(x - sx, z - 0.006); y += 0.005 * gauss(d, 0.024) * (1 if y < 0 else 0)
    for sx in (-0.06, 0.06):
        d = math.hypot(x - sx, z + 0.035); y -= 0.004 * gauss(d, 0.03) * (1 if y < 0 else 0)
    return Vector((x, y, z))
hd = sphere('hero_head', HR, FACE, W_HEAD, HC, seg=(56, 32), shape=head_shape, lv=1)
planar_uv(hd, 0, 0, 0.30, 0.32)
for s in (-1, 1): sphere(f'hero_ear_{s}', 0.024, SKIN, W_HEAD, (0.118 * s, 0.01, HC.z - 0.01), scale=(0.5, 0.9, 1.3), seg=(12, 8))

# saç kabuğu (tel yönünde UV'li)
bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=28, radius=HR, calc_uvs=True)
for v in bm.verts: v.co = head_shape(v.co) * 1.075 + Vector((0, 0.008, 0.012))
kill = [v for v in bm.verts if (v.co.y < 0.0 and v.co.z < 0.03 + 1.6 * v.co.x ** 2 and abs(v.co.x) < 0.125) or (v.co.z < -0.075 and v.co.y < 0.035)]
bmesh.ops.delete(bm, geom=kill, context='VERTS')
cap = obj_from_bm('hero_hair_cap', bm, HAIRC, HC)
so = cap.modifiers.new('sol', 'SOLIDIFY'); so.thickness = 0.008; so.offset = -1; subsurf(cap, 1); reg(cap, W_HEAD)

def P(x, y, z): return (x, y, z + HC.z)
for k in range(10):   # alın perçemi
    side = -1 if k < 5 else 1; i = k % 5
    x1 = side * (0.02 + i * 0.022); x2 = side * (0.035 + i * 0.024); z2 = 0.045 - i * 0.012
    tube(f'hero_fringe_{k}', [P(0.008 * side, -0.035, 0.15), P(x1 * 0.8, -0.115, 0.115), P(x2, -0.132 + i * 0.006, z2 + 0.02), P(x2 + side * 0.012, -0.124 + i * 0.008, z2 - 0.012)],
         0.017, HAIR if i % 2 else HAIRD, W_HEAD, taper=[0.9, 1.0, 0.7, 0.12], flat=0.55)
    for j in range(2):   # perçem içinde ince teller
        o = (j - 0.5) * 0.008
        tube(f'hero_fringe_s{k}_{j}', [P(0.008 * side + o, -0.04, 0.152), P(x1 * 0.8 + o, -0.121, 0.116), P(x2 + o, -0.138 + i * 0.006, z2 + 0.018), P(x2 + side * 0.014 + o, -0.128 + i * 0.008, z2 - 0.02)],
             0.004, HAIRD, W_HEAD, taper=[0.6, 1, 0.8, 0.1], bev=1)
for s in (-1, 1):
    for j in range(3):
        o = j * 0.008
        tube(f'hero_strand_{s}_{j}', [P((0.112 + o) * s, -0.06 + o, 0.06), P((0.13 + o) * s, -0.075 + o, -0.02), P((0.125 + o) * s, -0.07 + o, -0.1), P((0.112 + o) * s, -0.06 + o, -0.16 - j * 0.015)],
             0.007 - j * 0.0015, HAIR if j else HAIRD, W_HEAD, taper=[1, 0.9, 0.7, 0.15])
for k in range(40):   # arkaya taranmış ince tutamlar
    a = -1.3 + k * (2.6 / 39) + random.uniform(-0.03, 0.03)
    sx, cy = math.sin(a), math.cos(a); side = 1 if sx >= 0 else -1
    w = random.uniform(-0.006, 0.006)
    pts = [P(0.0 + w, -0.02, 0.149), P(0.072 * sx, 0.072 * cy, 0.132), P(0.128 * sx + w, 0.112 * cy + 0.02, 0.045), P(0.085 * side + w, 0.115 + w, -0.04)]
    tube(f'hero_lock_{k}', pts, random.uniform(0.008, 0.012), HAIRD if k % 3 == 0 else HAIR, W_HEAD, taper=[0.35, 1, 0.9, 0.45])

# örgüler: üç tutam, her tutam üç ince telden
for s, side in ((1, 'L'), (-1, 'R')):
    a, m_, b = BR[s]; N = 80
    def center(t):
        if t < 0.5: return a.lerp(m_, t * 2)
        return m_.lerp(b, (t - 0.5) * 2)
    for k in range(3):
        for j in range(3):
            pts, tap = [], []
            for i in range(N):
                t = i / (N - 1); c = center(t); rb = 0.021 * (1 - 0.35 * t)
                ph = t * 14 * math.pi + k * 2 * math.pi / 3
                off = (j - 1) * 0.0055
                pts.append((c.x + rb * math.cos(ph) + off * math.sin(ph), c.y + rb * math.sin(2 * ph) * 0.45 + off * 0.5, c.z + 0.004 * math.sin(ph) + off * 0.3))
                tap.append(1 - 0.4 * t)
            tube(f'hero_braid_{side}_{k}_{j}', pts, 0.0075, HAIRD if (k + j) % 3 == 0 else HAIR, W_BRAID(side, s), taper=tap, res=3, bev=1)
    end = b + Vector((0, 0, -0.005))
    torus(f'hero_tie_{side}', 0.013, 0.006, TIE, W_BRAID(side, s), tuple(end), seg=(16, 6))
    for k in range(7):
        ang = k * 2 * math.pi / 7
        tube(f'hero_tuft_{side}_{k}', [tuple(end + Vector((0, 0, -0.005))), tuple(end + Vector((0.012 * math.cos(ang), 0.012 * math.sin(ang), -0.045))),
                                        tuple(end + Vector((0.017 * math.cos(ang), 0.017 * math.sin(ang), -0.085 - 0.01 * (k % 2))))], 0.006, HAIR, W_BRAID(side, s), taper=[1, 0.8, 0.1])

# kiraz tokası
clip_c = Vector((-0.075, -0.088, 0.21 - 0.11)) + HC
R = Matrix.Rotation(math.radians(20), 3, 'Z') @ Matrix.Rotation(math.radians(-25), 3, 'Y') @ Matrix.Rotation(math.radians(-35), 3, 'X')
def CL(x, y, z): return tuple(clip_c + R @ Vector((x, y, z)))
for hx in (-0.03, 0.03):
    for dx in (-0.0085, 0.0085): sphere(f'hero_heart_{hx}_{dx}', 0.0105, CHERRY, W_HEAD, CL(hx + dx, 0, 0.004), scale=(1, 0.55, 1), seg=(12, 8), lv=0)
    sphere(f'hero_heart_tip_{hx}', 0.012, CHERRY, W_HEAD, CL(hx, 0, -0.008), scale=(0.9, 0.5, 1.2), seg=(10, 6), lv=0)
for dx in (-0.008, 0.008): sphere(f'hero_cherry_{dx}', 0.0095, CHERRY, W_HEAD, CL(dx, -0.003, -0.002), seg=(12, 8), lv=0)
sphere('hero_leaf', 0.009, LEAF, W_HEAD, CL(0.0, -0.002, 0.014), scale=(1.5, 0.5, 0.7), seg=(10, 6), lv=0)
finish(rig, HB)

# ================================================================ GRİ BIYIK (kedi)
FUR = mat('cat_fur', '#9fa0a8', 0.9); CFACE = mat('cat_face', '#9fa0a8', 0.9); TUFT = mat('cat_fur_tuft', '#a9aab2', 0.9); TUFTD = mat('cat_fur_tuft_dark', '#86878f', 0.9)
PINK = mat('cat_pink', '#e48aae', 0.6); LIME = mat('cat_hoodie', '#9bd92a', 0.9); LIMER = mat('cat_hoodie_rib', '#86c21f', 0.95)
ZIG = mat('cat_zigzag', '#2e7a2a', 0.8); CBLK = mat('cat_pants', '#16161b', 0.85); CSHOE = mat('cat_shoe', '#111114', 0.45)
CSOLE = mat('cat_sole', '#2a2a30', 0.8); CCORD = mat('cat_cord', '#2f2f35', 0.7); WHISK = mat('cat_whisker', '#25252a', 0.4)

cat = bpy.data.objects.new('cat', None); COL.objects.link(cat)
CPZ = 1.06; CSHZ = 1.62; CELZ = 1.21; CHIPZ = 1.02; CKNZ = 0.53; CHEADZ = 1.77; CC = Vector((0, 0, 1.95)); CR = 0.2
crig = build_rig('cat_rig', cat, [
    ('cat_pelvis', (0, 0, CPZ), (0, 0, 1.35), None, False),
    ('cat_head', (0, 0, CHEADZ), (0, 0, 2.15), 'cat_pelvis', False),
    ('cat_eye_L', (0.075, -0.162, CC.z + 0.015), (0.075, -0.22, CC.z + 0.015), 'cat_head', False),
    ('cat_eye_R', (-0.075, -0.162, CC.z + 0.015), (-0.075, -0.22, CC.z + 0.015), 'cat_head', False),
    ('cat_shoulder_L', (0.265, 0, CSHZ), (0.265, 0, CELZ), 'cat_pelvis', False), ('cat_elbow_L', (0.265, 0, CELZ), (0.265, 0, 0.85), 'cat_shoulder_L', True),
    ('cat_shoulder_R', (-0.265, 0, CSHZ), (-0.265, 0, CELZ), 'cat_pelvis', False), ('cat_elbow_R', (-0.265, 0, CELZ), (-0.265, 0, 0.85), 'cat_shoulder_R', True),
    ('cat_hip_L', (0.12, 0, CHIPZ), (0.12, 0, CKNZ), 'cat_pelvis', False), ('cat_knee_L', (0.12, 0, CKNZ), (0.12, 0, 0.03), 'cat_hip_L', True),
    ('cat_hip_R', (-0.12, 0, CHIPZ), (-0.12, 0, CKNZ), 'cat_pelvis', False), ('cat_knee_R', (-0.12, 0, CKNZ), (-0.12, 0, 0.03), 'cat_hip_R', True),
])
CB = ['cat_pelvis', 'cat_head', 'cat_eye_L', 'cat_eye_R', 'cat_shoulder_L', 'cat_elbow_L', 'cat_shoulder_R', 'cat_elbow_R', 'cat_hip_L', 'cat_knee_L', 'cat_hip_R', 'cat_knee_R']
C_PEL = lambda p: {'cat_pelvis': 1}
C_HEAD = lambda p: {'cat_head': 1}
def C_NECK(p): h = ss(CHEADZ - 0.03, CHEADZ + 0.05, p.z); return {'cat_head': h, 'cat_pelvis': 1 - h}
def C_ARM(side):
    def f(p):
        e = ss(CELZ + 0.06, CELZ - 0.06, p.z); t = ss(CSHZ - 0.03, CSHZ + 0.06, p.z)
        return {'cat_elbow_' + side: e, 'cat_shoulder_' + side: (1 - e) * (1 - t), 'cat_pelvis': (1 - e) * t}
    return f
def C_LEG(side):
    def f(p):
        k = ss(CKNZ + 0.06, CKNZ - 0.06, p.z); t = ss(CHIPZ - 0.05, CHIPZ + 0.07, p.z)
        return {'cat_knee_' + side: k, 'cat_hip_' + side: (1 - k) * (1 - t), 'cat_pelvis': (1 - k) * t}
    return f

cv = [(0, 0, -0.06), (0, 0, 0.12), (0, 0, 0.36), (0, 0, 0.56), (0, 0, 0.66), (0.23, 0, 0.58), (-0.23, 0, 0.58)]
skin('cat_torso', [(x, y, z + CPZ) for x, y, z in cv], [(0, 1), (1, 2), (2, 3), (3, 4), (3, 5), (3, 6)],
     [(0.235, 0.165), (0.22, 0.152), (0.25, 0.165), (0.235, 0.15), (0.1, 0.09), (0.095, 0.095), (0.095, 0.095)], LIME, C_PEL)
torus('cat_hem', 0.235, 0.03, LIMER, C_PEL, (0, 0, CPZ - 0.06), scale=(1, 0.72, 1))
torus('cat_neckband', 0.11, 0.026, LIMER, C_PEL, (0, 0.005, CPZ + 0.655), rot=(0.12, 0, 0), scale=(1.1, 1, 1))
for s in (-1, 1): sphere(f'cat_hood_side_{s}', 0.08, LIME, C_PEL, (0.1 * s, 0.075, CPZ + 0.67), scale=(0.75, 1.0, 1.0))
sphere('cat_hood_back', 0.12, LIME, C_PEL, (0, 0.14, CPZ + 0.6), scale=(1.3, 0.38, 0.85))
zz = [(-0.085, 0.47), (0.075, 0.33), (-0.055, 0.24), (0.085, 0.08)]
def front_y(z): return -(0.152 + 0.014 * math.sin(max(0, min(1, (z + 0.06) / 0.62)) * math.pi)) - 0.004
for i in range(3):
    (x1, z1), (x2, z2) = zz[i], zz[i + 1]
    tube(f'cat_zig_{i}', [(x1, front_y(z1), z1 + CPZ), ((x1 + x2) / 2, front_y((z1 + z2) / 2) - 0.004, (z1 + z2) / 2 + CPZ), (x2, front_y(z2), z2 + CPZ)], 0.016, ZIG, C_PEL, flat=0.35)
for s in (-1, 1):
    tube(f'cat_cord_{s}', [(0.06 * s, -0.14, CPZ + 0.63), (0.065 * s, -0.162, CPZ + 0.5), (0.062 * s, -0.17, CPZ + 0.38)], 0.006, CCORD, C_PEL)
    sphere(f'cat_cordend_{s}', 0.012, CCORD, C_PEL, (0.062 * s, -0.17, CPZ + 0.37), seg=(10, 6), lv=0)
chain('cat_neck', [(0, 0, CPZ + 0.62), (0, 0, CPZ + 0.74)], [0.075, 0.07], FUR, C_NECK)

# kollar: omuz kası, hafif kıvrımlı kol, kıvrık bilek, gerçek pati
for s, side in ((1, 'L'), (-1, 'R')):
    x = 0.265 * s
    chain(f'cat_arm_{side}', [(0.225 * s, 0, CSHZ + 0.05), (x, 0, CSHZ - 0.01), (x + 0.004 * s, 0, CSHZ - 0.2), (x, 0.008, CELZ), (x, 0, CELZ - 0.18), (x, 0, CELZ - 0.345)],
          [0.1, 0.094, 0.082, 0.074, 0.072, 0.079], LIME, C_ARM(side))
    for k in range(2):   # dirsek kırışıkları
        torus(f'cat_wrinkle_{side}_{k}', 0.071, 0.008, LIME, C_ARM(side), (x, 0.004, CELZ + 0.03 - k * 0.05), rot=(0.1 * (k - 0.5), 0.15 * s, 0), seg=(24, 6))
    torus(f'cat_cuff_{side}', 0.067, 0.021, LIMER, C_ARM(side), (x, 0, CELZ - 0.355))
    pz = CELZ - 0.445
    sphere(f'cat_paw_{side}', 0.074, FUR, C_ARM(side), (x, -0.005, pz), scale=(0.95, 1.1, 1.0), seg=(20, 12))
    for k in range(4):
        sphere(f'cat_finger_{side}_{k}', 0.024, FUR, C_ARM(side), (x + (k - 1.5) * 0.031 * s, -0.062, pz - 0.035 + abs(k - 1.5) * 0.006), scale=(1, 1.15, 1), seg=(12, 8))
    sphere(f'cat_thumb_{side}', 0.024, FUR, C_ARM(side), (x - 0.062 * s, -0.035, pz + 0.01), scale=(1, 1.3, 1), seg=(12, 8))

for s, side in ((1, 'L'), (-1, 'R')):
    x = 0.12 * s
    chain(f'cat_leg_{side}', [(x, 0, CHIPZ + 0.09), (x, 0, CHIPZ - 0.22), (x, 0, CKNZ), (x, 0, CKNZ - 0.25), (x, 0, 0.07)], [0.13, 0.118, 0.11, 0.135, 0.17], CBLK, C_LEG(side))
    sneaker(f'cat_shoe_{side}', 0.37, 0.17, 0.055, x, -0.06, 0.0, CSOLE, CSHOE, CSHOE, CSOLE, CSOLE, C_LEG(side), toe_white=False)

def cat_shape(c):
    x, y, z = c.x, c.y, c.z
    if z < 0.02: x *= 1.12
    if z > 0: z *= 0.9
    if y < 0:
        d = math.hypot(x, z + 0.06); y -= 0.03 * gauss(d, 0.06)
        for sx in (-0.075, 0.075):
            d = math.hypot(x - sx, z - 0.015); y += 0.01 * gauss(d, 0.035)
        d = abs(z - 0.055); y += 0.006 * gauss(d, 0.02) * gauss(x, 0.09)
    return Vector((x, y, z))
chd = sphere('cat_head_mesh', CR, CFACE, C_HEAD, CC, seg=(56, 32), shape=cat_shape, lv=1)
planar_uv(chd, 0, 0, 0.5, 0.42)
# başın arkası ve tepesi: hafif gri tüy tutamları (yüz sadece önde)
# başın arkası ve tepesi: tel dokulu açık gri tüy katmanı (yüz yalnızca önde)
TUFTC = mat('cat_fur_cap', '#acadb5', 0.9)
bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=56, v_segments=32, radius=CR, calc_uvs=True)
for v in bm.verts:
    n = v.co.normalized(); v.co = cat_shape(v.co) * (1.035 + 0.008 * math.sin(n.x * 40) * math.sin(n.z * 37))
kill = [v for v in bm.verts if (v.co.normalized().y < 0.0 and v.co.normalized().z < 0.9) or v.co.normalized().z < -0.62]
bmesh.ops.delete(bm, geom=kill, context='VERTS')
fc = obj_from_bm('cat_fur_cap', bm, TUFTC, CC); subsurf(fc, 1); reg(fc, C_HEAD)
for s, side in ((1, 'L'), (-1, 'R')):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.08, radius2=0.004, depth=0.2)
    for v in bm.verts: v.co.y *= 0.5
    e = obj_from_bm(f'cat_ear_{side}', bm, FUR, (0.12 * s, 0.0, CHEADZ + 0.33)); e.rotation_euler = (0, math.radians(-22 * s), 0); subsurf(e, 1); reg(e, C_HEAD)
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.05, radius2=0.002, depth=0.15)
    for v in bm.verts: v.co.y *= 0.3
    e2 = obj_from_bm(f'cat_earin_{side}', bm, PINK, (0.117 * s, -0.026, CHEADZ + 0.322)); e2.rotation_euler = (0, math.radians(-22 * s), 0); subsurf(e2, 1); reg(e2, C_HEAD)
    for k in range(3):
        y0 = 0.135 - k * 0.02
        tube(f'cat_whisk_{side}_{k}', [(0.07 * s, -0.19, y0 + CHEADZ), (0.2 * s, -0.17, y0 + 0.01 - k * 0.012 + CHEADZ), (0.33 * s, -0.12, y0 - 0.02 - k * 0.03 + CHEADZ)], 0.0028, WHISK, C_HEAD, taper=[1, 0.8, 0.2])
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=3, radius1=0.026, radius2=0.004, depth=0.02)
n = obj_from_bm('cat_nose', bm, PINK, (0, -0.212, CHEADZ + 0.138)); n.rotation_euler = (math.radians(90), 0, math.radians(180)); n.scale = (1.2, 0.8, 1); subsurf(n, 1); reg(n, C_HEAD)
finish(crig, CB)

# ---------------------------------------------------------------- dışa aktar
bpy.ops.object.select_all(action='SELECT')
os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_apply=False, use_selection=True, export_yup=True,
                          export_materials='EXPORT', export_cameras=False, export_lights=False, export_skins=True, export_animations=False)
print('YAZILDI', OUT)
