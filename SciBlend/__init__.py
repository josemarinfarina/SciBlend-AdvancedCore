import bpy
import os

try:
    import bpy.utils.previews
except ImportError:
    print("Warning: bpy.utils.previews not available")
    
from .operators.x3d.operators import ImportX3DOperator

try:
    from .operators.vtk.operators import ImportVTKAnimationOperator
except ImportError as e:
    import sys
    print(f"Error importing VTK operator: {e}", file=sys.stderr)
    class ImportVTKAnimationOperator(bpy.types.Operator):
        bl_idname = "import_vtk.animation"
        bl_label = "Import VTK/VTU/PVTU Animation (VTK not available)"
        def execute(self, context):
            self.report({'ERROR'}, "VTK is not available. Please install VTK package.")
            return {'CANCELLED'}

try:
    from .operators.netcdf.operators import ImportNetCDFOperator
except ImportError as e:
    import sys
    print(f"Error importing NetCDF operator: {e}", file=sys.stderr)
    class ImportNetCDFOperator(bpy.types.Operator):
        bl_idname = "import_netcdf.animation"
        bl_label = "Import NetCDF Animation (netCDF4 not available)"
        def execute(self, context):
            self.report({'ERROR'}, "netCDF4 is not available. Please install required package.")
            return {'CANCELLED'}

try:
    from .operators.shp.operators import ImportShapefileOperator
except ImportError as e:
    import sys
    print(f"Error importing Shapefile operator: {e}", file=sys.stderr)
    class ImportShapefileOperator(bpy.types.Operator):
        bl_idname = "import_shapefile.static"
        bl_label = "Import Shapefile (dependencies not available)"
        def execute(self, context):
            self.report({'ERROR'}, "Shapefile dependencies not available. Please install required packages.")
            return {'CANCELLED'}

from .operators.material_operators import CreateSharedMaterialOperator, ApplySharedMaterialOperator, RemoveAllShadersOperator
from .operators.object_operators import (
    CreateNullOperator, ParentNullToGeoOperator, NullToOriginOperator, CreateSceneOperator,
    BooleanCutterOperator, BooleanCutterHideOperator,
    AddMeshCutterOperator, GroupObjectsOperator, DeleteHierarchyOperator
)
from .operators.shp.delaunay import ShapefileDelaunayOperator
from .operators.gob_operators import (
    GOB_OT_connect_to_paraview, 
    GOB_OT_disconnect_from_paraview, 
    GOB_OT_refresh_from_paraview,
    GOBSettings
)

preview_collection = None

class X3DImportSettings(bpy.types.PropertyGroup):
    scale_factor: bpy.props.FloatProperty(
        name="Scale",
        description="Scale factor for imported objects",
        default=1.0,
        min=0.0001,
        max=100.0
    )
    axis_forward: bpy.props.EnumProperty(
        name="Forward",
        items=[
            ('X', "X", ""),
            ('Y', "Y", ""),
            ('Z', "Z", ""),
            ('-X', "-X", ""),
            ('-Y', "-Y", ""),
            ('-Z', "-Z", ""),
        ],
        default='Y',
    )
    axis_up: bpy.props.EnumProperty(
        name="Up",
        items=[
            ('X', "X", ""),
            ('Y', "Y", ""),
            ('Z', "Z", ""),
            ('-X', "-X", ""),
            ('-Y', "-Y", ""),
            ('-Z', "-Z", ""),
        ],
        default='Z',
    )
    overwrite_scene: bpy.props.BoolProperty(
        name="Overwrite Scene",
        description="Delete all objects in the scene before importing new meshes",
        default=True
    )
    shared_material: bpy.props.PointerProperty(
        type=bpy.types.Material,
        name="Shared Material"
    )

class SciBlendPanel(bpy.types.Panel):
    bl_label = "SciBlend Advanced Core"
    bl_idname = "OBJECT_PT_sciblend"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SciBlend Advanced Core'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.x3d_import_settings

        box = layout.box()
        box.label(text="Import", icon='IMPORT')
        row = box.row(align=True)
        row.operator("import_x3d.animation", text="X3D", icon='SEQUENCE')
        row.operator("import_vtk.animation", text="VTK/VTU/PVTU", icon='SEQUENCE')
        row.operator("import_netcdf.animation", text="NetCDF", icon='SEQUENCE')
        row.operator("import_shapefile.static", text="Shapefile", icon='MESH_DATA')
        row = box.row(align=True)
        row.prop(settings, "overwrite_scene")

        box = layout.box()
        box.label(text="Settings", icon='SETTINGS')
        row = box.row(align=True)
        row.prop(settings, "scale_factor")
        row.prop(settings, "axis_forward")
        row.prop(settings, "axis_up")

        box = layout.box()
        box.label(text="Material", icon='MATERIAL')
        row = box.row(align=True)
        row.prop(settings, "shared_material", text="")
        row.operator("import_x3d.create_shared_material", text="New", icon='ADD')
        row.operator("import_x3d.apply_shared_material", text="Apply", icon='CHECKMARK')
        row.operator("import_x3d.remove_all_shaders", text="Clear", icon='X')

        box = layout.box()
        box.label(text="Objects", icon='OBJECT_DATAMODE')
        row = box.row(align=True)
        row.operator("import_x3d.create_null", text="Create Null", icon='EMPTY_AXIS')
        row.operator("import_x3d.parent_null_to_geo", text="Parent to Geo", icon='OBJECT_DATAMODE')
        row.operator("import_x3d.null_to_origin", text="Center Null", icon='EMPTY_AXIS')
        row.operator("object.group_objects", text="Group", icon='GROUP')

        row = box.row(align=True)
        row.operator("object.create_scene", text="Scene Preset", icon='SCENE_DATA')

        box = layout.box()
        box.label(text="Boolean", icon='MOD_BOOLEAN')
        row = box.row(align=True)
        row.prop(context.scene, "new_cutter_mesh", text="")
        row.operator("object.add_mesh_cutter_operator", text="Add Cutter", icon='ADD')
        row = box.row(align=True)
        row.operator("object.boolean_cutter_operator", text="Apply", icon='MOD_BOOLEAN')
        row.operator("object.boolean_cutter_hide_operator", text="Hide", icon='HIDE_ON')

        box = layout.box()
        box.label(text="Organize", icon='OUTLINER')
        row = box.row(align=True)
        row.prop(context.scene, "group_type", text="")
        row.operator("object.group_objects", text="Group", icon='GROUP')
        row.operator("object.delete_hierarchy", text="Delete Hierarchy", icon='X')

        box = layout.box()
        box.label(text="GoB - Paraview Bridge", icon='LINKED')
        row = box.row(align=True)
        gob = context.scene.gob_settings
        row.prop(gob, "host", text="Host")
        row.prop(gob, "port", text="Port")
        row = box.row(align=True)
        if not gob.is_connected:
            row.operator("gob.connect_to_paraview", text="Connect", icon='LINKED')
        else:
            row.operator("gob.refresh_from_paraview", text="Refresh", icon='FILE_REFRESH')
            row.operator("gob.disconnect_from_paraview", text="Disconnect", icon='UNLINKED')

classes = (
    ImportX3DOperator,
    ImportVTKAnimationOperator,
    ImportNetCDFOperator,
    ImportShapefileOperator,
    CreateSharedMaterialOperator,
    ApplySharedMaterialOperator,
    RemoveAllShadersOperator,
    CreateNullOperator,
    ParentNullToGeoOperator,
    NullToOriginOperator,
    CreateSceneOperator,
    BooleanCutterOperator,
    BooleanCutterHideOperator,
    AddMeshCutterOperator,
    GroupObjectsOperator,
    DeleteHierarchyOperator,
    ShapefileDelaunayOperator,
    GOBSettings,
    GOB_OT_connect_to_paraview,
    GOB_OT_disconnect_from_paraview,
    GOB_OT_refresh_from_paraview,
    X3DImportSettings,
    SciBlendPanel,
)

def register():
    global preview_collection
    preview_collection = bpy.utils.previews.new()

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.x3d_import_settings = bpy.props.PointerProperty(type=X3DImportSettings)
    bpy.types.Scene.boolean_cutter_object = bpy.props.PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.new_cutter_mesh = bpy.props.PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.group_type = bpy.props.EnumProperty(
        name="Group Type",
        items=[
            ("EMPTY", "Empty", "Group under an Empty"),
            ("COLLECTION", "Collection", "Group in a Collection")
        ],
        default="EMPTY"
    )
    bpy.types.Scene.gob_settings = bpy.props.PointerProperty(type=GOBSettings)

def unregister():
    global preview_collection
    if preview_collection:
        bpy.utils.previews.remove(preview_collection)

    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.x3d_import_settings
    del bpy.types.Scene.boolean_cutter_object
    del bpy.types.Scene.new_cutter_mesh
    del bpy.types.Scene.group_type
    del bpy.types.Scene.gob_settings

if __name__ == "__main__":
    register()

bl_info = {
    "name": "SciBlend",
    "author": "José Marín",
    "version": (1, 0),
    "blender": (4, 5, 1),
    "location": "View3D > Sidebar > SciBlend Advanced Core",
    "description": "Scientific visualization tools for Blender",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}
