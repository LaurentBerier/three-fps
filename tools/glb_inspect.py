import bpy, sys
from mathutils import Vector

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
glb_path = argv[0]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb_path)

objs = list(bpy.data.objects)
print("=== OBJECTS ===")
for o in objs:
    print(f"  {o.type:9} {o.name}  parent={o.parent.name if o.parent else None} parent_type={o.parent_type} parent_bone='{o.parent_bone}'")

armatures = [o for o in objs if o.type == 'ARMATURE']
meshes = [o for o in objs if o.type == 'MESH']

for arm in armatures:
    print(f"=== ARMATURE {arm.name}: {len(arm.data.bones)} bones ===")
    print("  bone names:", [b.name for b in arm.data.bones])

for m in meshes:
    vg = [g.name for g in m.vertex_groups]
    print(f"=== MESH {m.name} ===")
    print(f"  parent={m.parent.name if m.parent else None} parent_bone='{m.parent_bone}'")
    print(f"  vertex_groups({len(vg)}):", vg)
    mods = [(mod.name, mod.type, getattr(mod, 'object', None).name if getattr(mod, 'object', None) else None) for mod in m.modifiers]
    print(f"  modifiers:", mods)
    print(f"  world_origin:", tuple(round(c, 4) for c in m.matrix_world.translation))

# Hand bone world transforms (to derive weapon attach offset)
for arm in armatures:
    for bname in ['hand.R', 'hand.L']:
        b = arm.data.bones.get(bname)
        if b:
            head_world = arm.matrix_world @ b.head_local
            print(f"  BONE {bname} head_world:", tuple(round(c, 4) for c in head_world))

print("=== ANIMATIONS ===")
for a in bpy.data.actions:
    print(f"  action {a.name} frames {a.frame_range[0]:.0f}-{a.frame_range[1]:.0f}")
