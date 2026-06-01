"""Consolidate the full-body mutant (Mixamo humanoid) into one FBX template:
the mutant mesh + 36-bone skeleton (T-pose bind) + all locomotion/combat
animations (idle/walk/run/attack/die) combined as separate takes.

Usage:
  blender --background --factory-startup --python mutant_fullbody.py -- <anim_dir> <out_dir>
"""
import bpy, sys, os

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
anim_dir, out_dir = argv[0], argv[1]
os.makedirs(out_dir, exist_ok=True)

# name -> source file. The base mesh+skeleton comes from mutant.fbx; the rest are
# the Mixamo animation clips on the same 'Mutant:' skeleton.
ANIMS = [
    ('idle',   'mutant breathing idle.fbx'),
    ('walk',   'mutant walking.fbx'),
    ('run',    'mutant run.fbx'),
    ('attack', 'mutant punch.fbx'),
    ('die',    'mutant dying.fbx'),
]

bpy.ops.wm.read_factory_settings(use_empty=True)

# --- Base mesh + skeleton (defines the T-pose bind) ---
bpy.ops.import_scene.fbx(filepath=os.path.join(anim_dir, 'mutant.fbx'))
base_objs = list(bpy.data.objects)
base_arm = next(o for o in base_objs if o.type == 'ARMATURE')
# Start from a clean action set (drop the clip bundled in mutant.fbx so the bind
# stays at the rest/T-pose and only our named takes are exported).
for a in list(bpy.data.actions):
    bpy.data.actions.remove(a)
if base_arm.animation_data:
    base_arm.animation_data.action = None

# --- Pull each clip's action onto the shared skeleton ---
kept = []
for name, fname in ANIMS:
    path = os.path.join(anim_dir, fname)
    before_objs = set(bpy.data.objects)
    before_acts = set(bpy.data.actions)
    bpy.ops.import_scene.fbx(filepath=path)
    new_objs = set(bpy.data.objects) - before_objs
    new_acts = [a for a in bpy.data.actions if a not in before_acts]
    # The body animation is the action with the most fcurves.
    act = max(new_acts, key=lambda a: len(a.fcurves), default=None)
    if act:
        act.name = name
        act.use_fake_user = True          # survive deletion of the imported rig
        kept.append(act)
        # drop any stray extra actions from this import
        for a in new_acts:
            if a is not act:
                bpy.data.actions.remove(a)
    # remove the imported (duplicate) armature + mesh; the action stays
    for o in new_objs:
        bpy.data.objects.remove(o, do_unlink=True)
    print(f"  {name}: {len(act.fcurves) if act else 0} fcurves")

print("ACTIONS:", [a.name for a in bpy.data.actions])

# --- Export base mesh + skeleton + all takes ---
bpy.ops.object.select_all(action='DESELECT')
for o in base_objs:
    if o.name in bpy.data.objects:
        o.select_set(True)
bpy.context.view_layer.objects.active = base_arm

bpy.ops.export_scene.fbx(
    filepath=os.path.join(out_dir, 'mutant_fullbody.fbx'),
    use_selection=True,
    add_leaf_bones=False,
    bake_anim=True,
    bake_anim_use_all_actions=True,
    bake_anim_use_nla_strips=False,
    path_mode='COPY',
    embed_textures=True,
)
print('WROTE mutant_fullbody.fbx')
print('DONE')
