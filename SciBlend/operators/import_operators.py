import bpy
import bmesh
import os
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty
from bpy.types import Operator
import logging
import vtk
import numpy as np

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ImportStaticX3DOperator(bpy.types.Operator, ImportHelper):
    bl_idname = "import_x3d.static"
    bl_label = "Import Static"
    filename_ext = ""

    def execute(self, context):
        settings = context.scene.x3d_import_settings
        directory = self.filepath
        file_path = os.path.join(directory, "tmpfile.x3d")
        scale_factor = settings.scale_factor

        if os.path.exists(file_path):
            bpy.ops.import_scene.x3d(filepath=file_path,
                                     axis_forward=settings.axis_forward,
                                     axis_up=settings.axis_up)
            for obj in bpy.context.selected_objects:
                obj.scale = (scale_factor, scale_factor, scale_factor)

            self.report({'INFO'}, f"File {file_path} successfully imported into Blender.")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, f"File {file_path} not found.")
            return {'CANCELLED'}

class ImportX3DAnimationOperator(bpy.types.Operator, ImportHelper):
    bl_idname = "import_x3d.animation"
    bl_label = "Import Animation"
    filename_ext = ""

    def execute(self, context):
        settings = context.scene.x3d_import_settings
        scale_factor = settings.scale_factor
        start_frame = settings.start_frame_number
        end_frame = settings.end_frame_number
        num_frames = end_frame - start_frame + 1
        directory = os.path.dirname(self.filepath)

        x3d_files = [os.path.join(directory, f"tempfile{i}.x3d") for i in range(
            start_frame, end_frame + 1)]

        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        material = settings.shared_material

        if material is None:
            material = bpy.data.materials.new(name="SharedMaterial")
            material.use_nodes = True
            nodes = material.node_tree.nodes
            links = material.node_tree.links

            for node in nodes:
                nodes.remove(node)

            attribute_node = nodes.new(type='ShaderNodeAttribute')
            attribute_node.attribute_name = 'Col'

            bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')

            material_output = nodes.new(type='ShaderNodeOutputMaterial')

            links.new(
                attribute_node.outputs['Color'], bsdf.inputs['Base Color'])
            links.new(bsdf.outputs['BSDF'], material_output.inputs['Surface'])

        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = num_frames

        for frame, x3d_file in enumerate(x3d_files, start=1):
            if os.path.exists(x3d_file):
                bpy.ops.import_scene.x3d(filepath=x3d_file,
                                         axis_forward=settings.axis_forward,
                                         axis_up=settings.axis_up)

                imported_objects = bpy.context.selected_objects

                for obj in imported_objects:
                    if obj.type == 'MESH':
                        obj.scale = (scale_factor, scale_factor, scale_factor)
                        obj.data.materials.clear()
                        obj.data.materials.append(material)

                    obj.hide_render = False
                    obj.hide_viewport = False
                    obj.keyframe_insert(data_path="hide_render", frame=frame)
                    obj.keyframe_insert(data_path="hide_viewport", frame=frame)

                    obj.hide_render = True
                    obj.hide_viewport = True
                    if frame > 1:
                        obj.keyframe_insert(
                            data_path="hide_render", frame=frame-1)
                        obj.keyframe_insert(
                            data_path="hide_viewport", frame=frame-1)
                    if frame < num_frames:
                        obj.keyframe_insert(
                            data_path="hide_render", frame=frame+1)
                        obj.keyframe_insert(
                            data_path="hide_viewport", frame=frame+1)
            else:
                self.report({'WARNING'}, f"File {x3d_file} not found.")

        # Configurar la interpolación de los keyframes a constante
        for obj in bpy.data.objects:
            if obj.animation_data and obj.animation_data.action:
                for fcurve in obj.animation_data.action.fcurves:
                    for kf in fcurve.keyframe_points:
                        kf.interpolation = 'CONSTANT'

        self.report({'INFO'}, "Import and configuration completed.")
        return {'FINISHED'}

class ImportVTKAnimationOperator(Operator, ImportHelper):
    bl_idname = "import_vtk.animation"
    bl_label = "Import VTK Animation"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".vtk"
    filter_glob: StringProperty(default="*.vtk", options={'HIDDEN'})

    files: CollectionProperty(
        name="File Path",
        type=bpy.types.OperatorFileListElement,
    )

    directory: StringProperty(subtype='DIR_PATH')

    create_smooth_groups: BoolProperty(
        name="Create Smooth Groups",
        description="Create smooth groups based on surface normals",
        default=True,
    )

    def execute(self, context):
        try:
            # Eliminar todos los objetos existentes
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete()

            num_frames = len(self.files)
            context.scene.frame_start = 1
            context.scene.frame_end = num_frames

            for i, file_elem in enumerate(self.files):
                filepath = os.path.join(self.directory, file_elem.name)
                frame = i + 1

                vertices, faces, point_data = self.read_vtk(filepath)
                if not vertices or not faces:
                    self.report({'ERROR'}, f"Failed to read VTK file {file_elem.name}: No vertices or faces found.")
                    continue

                obj = self.create_mesh(context, vertices, faces, point_data, f"Frame_{frame}")
                
                # Configurar visibilidad
                obj.hide_viewport = False
                obj.hide_render = False
                obj.keyframe_insert(data_path="hide_viewport", frame=frame)
                obj.keyframe_insert(data_path="hide_render", frame=frame)

                obj.hide_viewport = True
                obj.hide_render = True
                if frame > 1:
                    obj.keyframe_insert(data_path="hide_viewport", frame=frame-1)
                    obj.keyframe_insert(data_path="hide_render", frame=frame-1)
                if frame < num_frames:
                    obj.keyframe_insert(data_path="hide_viewport", frame=frame+1)
                    obj.keyframe_insert(data_path="hide_render", frame=frame+1)

                # Crear material para cada atributo
                for attr_name, attr_values in point_data.items():
                    if len(attr_values) == len(vertices):
                        if not isinstance(attr_values[0], (tuple, list)):
                            min_value = min(attr_values)
                            max_value = max(attr_values)
                            self.create_material(obj, attr_name, min_value, max_value)

            # Configurar la interpolación de los keyframes a constante
            for obj in bpy.data.objects:
                if obj.animation_data and obj.animation_data.action:
                    for fcurve in obj.animation_data.action.fcurves:
                        for kf in fcurve.keyframe_points:
                            kf.interpolation = 'CONSTANT'

            self.report({'INFO'}, f"Imported {num_frames} VTK files as an animation.")
            return {'FINISHED'}
        except Exception as e:
            logger.error(f"Error importing VTK file: {e}")
            self.report({'ERROR'}, f"Error importing VTK file: {str(e)}")
            return {'CANCELLED'}

    def read_vtk(self, filepath):
        reader = vtk.vtkUnstructuredGridReader()
        reader.SetFileName(filepath)
        reader.Update()

        data = reader.GetOutput()
        
        points = data.GetPoints()
        vertices = [points.GetPoint(i) for i in range(points.GetNumberOfPoints())]
        
        faces = []
        for i in range(data.GetNumberOfCells()):
            cell = data.GetCell(i)
            cell_type = cell.GetCellType()
            if cell_type in [vtk.VTK_TRIANGLE, vtk.VTK_QUAD]:
                face = [cell.GetPointId(j) for j in range(cell.GetNumberOfPoints())]
                faces.append(face)
            elif cell_type == vtk.VTK_TETRA:
                for j in range(4):
                    face = [cell.GetPointId(k) for k in range(4) if k != j]
                    faces.append(face)
        
        point_data = {}
        pd = data.GetPointData()
        for i in range(pd.GetNumberOfArrays()):
            array = pd.GetArray(i)
            name = array.GetName()
            num_components = array.GetNumberOfComponents()
            num_tuples = array.GetNumberOfTuples()
            if num_components == 1:
                point_data[name] = [array.GetValue(j) for j in range(num_tuples)]
            else:
                point_data[name] = [array.GetTuple(j) for j in range(num_tuples)]

        return vertices, faces, point_data

    def create_mesh(self, context, vertices, faces, point_data, name):
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)
        context.collection.objects.link(obj)

        mesh.from_pydata(vertices, [], faces)
        mesh.update()

        for attr_name, attr_values in point_data.items():
            if len(attr_values) == len(vertices):
                if not isinstance(attr_values[0], (tuple, list)):
                    float_attribute = mesh.attributes.new(name=attr_name, type='FLOAT', domain='POINT')
                    for i, value in enumerate(attr_values):
                        float_attribute.data[i].value = value
                    min_value = min(attr_values)
                    max_value = max(attr_values)
                    self.create_material(obj, attr_name, min_value, max_value)

        if self.create_smooth_groups and hasattr(mesh, 'use_auto_smooth'):
            mesh.use_auto_smooth = True
            mesh.auto_smooth_angle = 3.14159

        return obj

    def create_material(self, obj, attribute_name, min_value, max_value):
        mat = bpy.data.materials.new(name=f"{obj.name}_{attribute_name}_Material")
        mat.use_nodes = True
        obj.data.materials.append(mat)

        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        nodes.clear()

        node_attr = nodes.new(type='ShaderNodeAttribute')
        node_attr.attribute_name = attribute_name

        node_map_range = nodes.new(type='ShaderNodeMapRange')
        node_map_range.inputs['From Min'].default_value = min_value
        node_map_range.inputs['From Max'].default_value = max_value
        node_map_range.inputs['To Min'].default_value = 0.0
        node_map_range.inputs['To Max'].default_value = 1.0

        node_color_ramp = nodes.new(type='ShaderNodeValToRGB')
        
        node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        node_output = nodes.new(type='ShaderNodeOutputMaterial')

        links.new(node_attr.outputs['Fac'], node_map_range.inputs['Value'])
        links.new(node_map_range.outputs['Result'], node_color_ramp.inputs['Fac'])
        links.new(node_color_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])
        links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])

        node_attr.location = (-600, 0)
        node_map_range.location = (-400, 0)
        node_color_ramp.location = (-200, 0)
        node_bsdf.location = (200, 0)
        node_output.location = (400, 0)

        return mat