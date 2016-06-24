bl_info = {
    "name": "glTF format",
    "author": "Daniel Stokes",
    "version": (0, 1, 0),
    "blender": (2, 76, 0),
    "location": "File > Import-Export",
    "description": "Export glTF",
    "warning": "",
    "wiki_url": ""
                "",
    "support": 'TESTING',
    "category": "Import-Export"}


# Treat as module
if '.' in __name__:
    if 'loaded' in locals():
        import imp
        imp.reload(blendergltf)
        from .blendergltf import *
    else:
        loaded = True
        from .blendergltf import *

# Treat as addon
else:
    if "bpy" in locals():
        import importlib
        importlib.reload(blendergltf)


    import json

    import bpy
    from bpy.props import (
            StringProperty,
            BoolProperty
            )
    from bpy_extras.io_utils import (
            ExportHelper,
            )

    from . import blendergltf


    class ExportGLTF(bpy.types.Operator, ExportHelper):
        """Save a Khronos glTF File"""

        bl_idname = "export_scene.gltf"
        bl_label = 'Export glTF'

        filename_ext = ".gltf"
        filter_glob = StringProperty(
                default="*.gltf",
                options={'HIDDEN'},
                )

        apply_modifiers = BoolProperty(
            name="Apply modifiers",
            description="Apply modifiers",
            default=True,
            )

        use_redcrane_extensions = BoolProperty(
            name="Use Redcrane extensions / techniques",
            description="Use redcrane techniques",
            default=False,
            )

        check_extension = True

        def execute(self, context):

            keywords = self.as_keywords(ignore=("filter_glob",))

            scene = {
                'actions': bpy.data.actions,
                'camera': bpy.data.cameras,
                'lamps': bpy.data.lamps,
                'images': bpy.data.images,
                'materials': bpy.data.materials,
                'scenes': bpy.data.scenes,
                'textures': bpy.data.textures,
            }

            scene['objects'] = []
            scene['meshes'] = []

            # Mapping from object to mesh
            scene['obj_meshes'] = {}

            for obj in bpy.data.objects:
                if obj.type != 'MESH': continue

                new_mesh = obj.to_mesh(
                    context.scene, keywords['apply_modifiers'], 'PREVIEW'
                )
                scene['meshes'].append(new_mesh)

                # Right now this will do, but this script requires some major
                # restructuring because we want to be able to reference a mesh
                # independently from its containing object. The objects should
                # only define the node hierarchy. We can fix this by adding
                # another layer of indirection that maps objects to their usable
                # meshes.
                scene['obj_meshes'][obj] = new_mesh
                scene['objects'].append(obj)

            gltf = blendergltf.export_gltf(scene, **keywords)

            with open(self.filepath, 'w') as fout:
                json.dump(gltf, fout, indent=4, sort_keys=True, check_circular=False)

            # Clean up meshes
            for mesh in scene['meshes']:
                bpy.data.meshes.remove(mesh)

            return {'FINISHED'}


    def menu_func_export(self, context):
        self.layout.operator(ExportGLTF.bl_idname, text="glTF (.gltf)")


    def register():
        bpy.utils.register_module(__name__)

        bpy.types.INFO_MT_file_export.append(menu_func_export)


    def unregister():
        bpy.utils.unregister_module(__name__)

        bpy.types.INFO_MT_file_export.remove(menu_func_export)
