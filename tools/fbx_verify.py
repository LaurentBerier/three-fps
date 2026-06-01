import bpy, sys
for path in sys.argv[sys.argv.index("--") + 1:]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=path)
    print(f"\n=== {path} ===")
    for o in bpy.data.objects:
        extra = ""
        if o.type == 'ARMATURE':
            extra = f" bones={len(o.data.bones)}"
        if o.type == 'MESH':
            extra = f" verts={len(o.data.vertices)} mats={[m.name for m in o.data.materials]} mods={[m.type for m in o.modifiers]}"
        print(f"  {o.type:9} {o.name}{extra}")
    print("  actions:", [a.name for a in bpy.data.actions])
    imgs = [(i.name, 'packed' if i.packed_file else 'external') for i in bpy.data.images if i.name != 'Render Result']
    print("  images:", imgs)
