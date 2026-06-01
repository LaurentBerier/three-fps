"""Export a RIGGED AK47 weapon template: the AK mesh + only its gun-part bones
(gun/slider/trigger/magazine/magazine_button) + the fire/idle/reload animations,
so the magazine, slider and trigger still animate during the reload. Unlike
weapon_ak47.fbx (rigid, skinning stripped), this keeps the separate animated magazine.

Usage:
  blender --background --factory-startup --python glb_weapon_rigged.py -- <glb> <out_dir>
"""
import bpy, sys, os

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
glb_path, out_dir = argv[0], argv[1]
os.makedirs(out_dir, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb_path)

armature = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
weapon = bpy.data.objects['SMDImport']

# Drop the arms mesh and the stray helper.
for junk in ['SkeletalMeshComponent0', 'Icosphere']:
    if junk in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[junk], do_unlink=True)

# Prune the armature down to just the gun-part bones (they are all root-level, so
# this leaves a clean standalone weapon skeleton). Their fire/idle/reload keyframes
# are untouched, so the magazine still drops and the slider still racks.
keep = {
    'gun', 'gun_end', 'slider', 'slider_end', 'trigger', 'trigger_end',
    'magazine', 'magazine_end', 'magazine_button', 'magazine_button_end',
}
bpy.ops.object.select_all(action='DESELECT')
armature.select_set(True)
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='EDIT')
for b in list(armature.data.edit_bones):
    if b.name not in keep:
        armature.data.edit_bones.remove(b)
bpy.ops.object.mode_set(mode='OBJECT')
print("REMAINING BONES:", [b.name for b in armature.data.bones])

# Strip keyframes that target the deleted arm bones. The FBX exporter discards any
# action containing an fcurve that no longer resolves, so without this only the
# active action (fire) would survive — idle/reload would be silently dropped.
import re
bone_of = re.compile(r'pose\.bones\["([^"]+)"\]')
for act in bpy.data.actions:
    for fc in list(act.fcurves):
        m = bone_of.match(fc.data_path)
        if m and m.group(1) not in keep:
            act.fcurves.remove(fc)
    print(f"ACTION {act.name}: {len(act.fcurves)} fcurves kept")

bpy.ops.object.select_all(action='DESELECT')
armature.select_set(True)
weapon.select_set(True)
bpy.context.view_layer.objects.active = armature

bpy.ops.export_scene.fbx(
    filepath=os.path.join(out_dir, 'weapon_ak47_rigged.fbx'),
    use_selection=True,
    add_leaf_bones=False,
    bake_anim=True,
    bake_anim_use_all_actions=True,
    bake_anim_use_nla_strips=False,
    path_mode='COPY',
    embed_textures=True,
)
print('WROTE weapon_ak47_rigged.fbx')
print('DONE')
