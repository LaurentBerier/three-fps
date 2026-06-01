"""Split ak47.glb into two FBX templates:
  - player_arms.fbx : SkeletalMeshComponent0 (military arms) + full metarig + animations
  - weapon_ak47.fbx : SMDImport (AK47) detached to a standalone rigid mesh
Also writes gun_socket.json with the rest transform of the 'gun' bone so the
runtime can derive the weapon attach offset exactly.

Usage:
  blender --background --factory-startup --python glb_to_fbx.py -- <glb> <out_dir>
"""
import bpy, sys, os, json

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
glb_path, out_dir = argv[0], argv[1]
os.makedirs(out_dir, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb_path)

scene_objs = list(bpy.data.objects)
armature = next(o for o in scene_objs if o.type == 'ARMATURE')
arms = bpy.data.objects['SkeletalMeshComponent0']
weapon = bpy.data.objects['SMDImport']

# Drop the stray helper mesh if present (not weighted to anything)
for junk in ['Icosphere']:
    if junk in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[junk], do_unlink=True)


def select_only(objs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]


# --- Capture the 'gun' socket bone rest transform (armature space) ---
gun = armature.data.bones.get('gun')
socket = {}
if gun:
    m = armature.matrix_world @ gun.matrix_local  # bone head/orientation in world (rest)
    socket = {
        'bone': 'gun',
        'matrix_world_rowmajor': [list(row) for row in m],
        'head_world': list((armature.matrix_world @ gun.head_local)),
    }
with open(os.path.join(out_dir, 'gun_socket.json'), 'w') as f:
    json.dump(socket, f, indent=2)

# ---------------- Export 1: player arms + skeleton + animations ----------------
select_only([armature, arms])
bpy.ops.export_scene.fbx(
    filepath=os.path.join(out_dir, 'player_arms.fbx'),
    use_selection=True,
    add_leaf_bones=False,
    bake_anim=True,
    bake_anim_use_all_actions=True,
    bake_anim_use_nla_strips=False,
    path_mode='COPY',
    embed_textures=True,
)
print('WROTE player_arms.fbx')

# ---------------- Export 2: weapon as a standalone rigid mesh ----------------
# Strip the armature dependency so the AK is a clean static mesh at its rest pose.
for mod in list(weapon.modifiers):
    weapon.modifiers.remove(mod)
weapon.vertex_groups.clear()
weapon.parent = None

select_only([weapon])
bpy.ops.export_scene.fbx(
    filepath=os.path.join(out_dir, 'weapon_ak47.fbx'),
    use_selection=True,
    add_leaf_bones=False,
    bake_anim=False,
    path_mode='COPY',
    embed_textures=True,
)
print('WROTE weapon_ak47.fbx')
print('DONE')
