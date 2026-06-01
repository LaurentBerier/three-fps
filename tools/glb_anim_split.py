"""Export the player's weapon-handling animations as SEPARATE FBX files, one clip
per file, on the full first-person rig (arms + AK + skeleton):
  player_fire.fbx     -> shooting only
  player_reload.fbx   -> reloading only (with the animated magazine)

Note: these clips live on the arms+gun metarig (there is no full-body shoot/reload
in this project), so the bind here is the FP arms pose, not a T-pose.

Usage:
  blender --background --factory-startup --python glb_anim_split.py -- <glb> <out_dir>
"""
import bpy, sys, os

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
glb_path, out_dir = argv[0], argv[1]
os.makedirs(out_dir, exist_ok=True)

# output name -> action to keep
CLIPS = [
    ('player_fire',   'fire_metarig'),
    ('player_reload', 'reload_empty_metarig'),
]

for out_name, action_name in CLIPS:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=glb_path)

    if 'Icosphere' in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects['Icosphere'], do_unlink=True)

    armature = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    arms = bpy.data.objects['SkeletalMeshComponent0']
    weapon = bpy.data.objects['SMDImport']

    # Keep only the target clip so just that one animation is exported.
    for a in list(bpy.data.actions):
        if a.name != action_name:
            bpy.data.actions.remove(a)
    if armature.animation_data is None:
        armature.animation_data_create()
    armature.animation_data.action = bpy.data.actions.get(action_name)

    bpy.ops.object.select_all(action='DESELECT')
    for o in (armature, arms, weapon):
        o.select_set(True)
    bpy.context.view_layer.objects.active = armature

    bpy.ops.export_scene.fbx(
        filepath=os.path.join(out_dir, out_name + '.fbx'),
        use_selection=True,
        add_leaf_bones=False,
        bake_anim=True,
        bake_anim_use_all_actions=True,
        bake_anim_use_nla_strips=False,
        path_mode='COPY',
        embed_textures=True,
    )
    print(f'WROTE {out_name}.fbx  (clip: {action_name})')

print('DONE')
