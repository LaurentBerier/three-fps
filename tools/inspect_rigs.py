import bpy, sys

def dump(path, importer):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    importer(path)
    print(f"\n=== {path} ===")
    arms = [o for o in bpy.data.objects if o.type == 'ARMATURE']
    for a in arms:
        bones = [b.name for b in a.data.bones]
        spine = [b for b in bones if any(k in b.lower() for k in ('spine','pelvis','hips','neck','head','thigh','shin','leg','foot','chest'))]
        print(f"  ARMATURE {a.name}: {len(bones)} bones")
        print(f"    full-body markers (spine/legs/head): {spine if spine else 'NONE -> arms only'}")
        # crude T-pose check: compare L vs R upper-arm head heights / x-spread
        print(f"    sample bones: {bones[:8]}")
    print("  actions:", [a.name for a in bpy.data.actions])

# arms metarig from the glb
dump(sys.argv[sys.argv.index('--')+1], lambda p: bpy.ops.import_scene.gltf(filepath=p))
# mutant full body
dump(sys.argv[sys.argv.index('--')+2], lambda p: bpy.ops.import_scene.fbx(filepath=p))
