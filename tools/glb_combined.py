"""Export the full first-person rig as one FBX: arms mesh + AK mesh + the complete
metarig + all animations (fire/idle/reload_empty). This is the combined viewmodel,
so the arms and the gun (incl. the animated magazine) play together.

Usage:
  blender --background --factory-startup --python glb_combined.py -- <glb> <out_dir>
"""
import bpy, sys, os

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
glb_path, out_dir = argv[0], argv[1]
os.makedirs(out_dir, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb_path)

armature = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
arms = bpy.data.objects['SkeletalMeshComponent0']
weapon = bpy.data.objects['SMDImport']

# Drop the stray helper mesh only; keep both arms and gun.
if 'Icosphere' in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects['Icosphere'], do_unlink=True)

bpy.ops.object.select_all(action='DESELECT')
for o in (armature, arms, weapon):
    o.select_set(True)
bpy.context.view_layer.objects.active = armature

bpy.ops.export_scene.fbx(
    filepath=os.path.join(out_dir, 'player_ak47_combined.fbx'),
    use_selection=True,
    add_leaf_bones=False,
    bake_anim=True,
    bake_anim_use_all_actions=True,
    bake_anim_use_nla_strips=False,
    path_mode='COPY',
    embed_textures=True,
)
print('WROTE player_ak47_combined.fbx')
print('DONE')
