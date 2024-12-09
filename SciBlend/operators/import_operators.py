import bpy
import bmesh
import os
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty, IntProperty, FloatProperty
from bpy.types import Operator
import logging
import vtk
import numpy as np
import mathutils
import math

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
    bl_label = "Import VTK/VTU/PVTU Animation"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ""
    filter_glob: StringProperty(default="*.vtk;*.vtu;*.pvtu", options={'HIDDEN'})

    files: CollectionProperty(
        name="File Path",
        type=bpy.types.OperatorFileListElement,
    )

    directory: StringProperty(subtype='DIR_PATH')

    # Estas propiedades servirán como fallback
    start_frame_number: IntProperty(
        name="Start Frame Number",
        description="Number of the first frame to import",
        default=1,
        min=1
    )
    
    end_frame_number: IntProperty(
        name="End Frame Number",
        description="Number of the last frame to import",
        default=10,
        min=1
    )
    
    axis_forward: EnumProperty(
        name="Forward Axis",
        description="Axis that faces forward",
        items=[
            ('X', "X", ""),
            ('Y', "Y", ""),
            ('Z', "Z", ""),
            ('-X', "-X", ""),
            ('-Y', "-Y", ""),
            ('-Z', "-Z", "")
        ],
        default='-Z'
    )
    
    axis_up: EnumProperty(
        name="Up Axis",
        description="Axis that faces up",
        items=[
            ('X', "X", ""),
            ('Y', "Y", ""),
            ('Z', "Z", ""),
            ('-X', "-X", ""),
            ('-Y', "-Y", ""),
            ('-Z', "-Z", "")
        ],
        default='Y'
    )
    
    scale_factor: FloatProperty(
        name="Scale Factor",
        description="Scale factor for imported objects",
        default=1.0,
        min=0.01,
        max=100.0
    )

    create_smooth_groups: BoolProperty(
        name="Create Smooth Groups",
        description="Create smooth groups based on surface normals",
        default=True,
    )

    height_scale: FloatProperty(
        name="Height Scale",
        description="Scale factor for height values in spherical projection",
        default=0.01,
        min=0.0001,
        max=1.0,
        soft_min=0.001,
        soft_max=0.1
    )

    def execute(self, context):
        try:
            # Obtener configuraciones de x3d_import_settings
            settings = context.scene.x3d_import_settings
            self.scale_factor = settings.scale_factor
            self.start_frame_number = settings.start_frame_number
            self.end_frame_number = settings.end_frame_number
            self.axis_forward = settings.axis_forward
            self.axis_up = settings.axis_up

            # Eliminar todos los objetos existentes
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete()

            # Usar solo los archivos dentro del rango especificado
            files_to_process = self.files[self.start_frame_number-1:self.end_frame_number]
            num_frames = len(files_to_process)

            context.scene.frame_start = self.start_frame_number
            context.scene.frame_end = self.start_frame_number + num_frames - 1

            # Crear material compartido
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

                links.new(attribute_node.outputs['Fac'], bsdf.inputs['Base Color'])
                links.new(bsdf.outputs['BSDF'], material_output.inputs['Surface'])

            for i, file_elem in enumerate(files_to_process):
                filepath = os.path.join(self.directory, file_elem.name)
                frame = self.start_frame_number + i

                vertices, faces, point_data = self.read_unstructured_grid(filepath)
                if not vertices:
                    self.report({'ERROR'}, f"Failed to read file {file_elem.name}: No vertices found.")
                    continue

                obj = self.create_mesh(context, vertices, faces, point_data, f"Frame_{frame}")
                
                # Crear matriz de transformación
                from bpy_extras.io_utils import axis_conversion
                rotation = axis_conversion(
                    from_forward='-Z',
                    from_up='Y',
                    to_forward=self.axis_forward,
                    to_up=self.axis_up
                ).to_4x4()

                # Crear matriz de escala
                scale = mathutils.Matrix.Scale(self.scale_factor, 4)
                
                # Aplicar transformaciones
                obj.matrix_world = rotation @ scale

                # Actualizar la vista
                bpy.context.view_layer.update()

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

            self.report({'INFO'}, f"Imported {num_frames} files as an animation.")
            return {'FINISHED'}
        except Exception as e:
            logger.error(f"Error importing file: {e}")
            self.report({'ERROR'}, f"Error importing file: {str(e)}")
            return {'CANCELLED'}

    def read_unstructured_grid(self, filepath):
        extension = os.path.splitext(filepath)[1].lower()
        
        if extension == '.vtk':
            reader = vtk.vtkUnstructuredGridReader()
            reader.SetFileName(filepath)
            reader.Update()
            data = reader.GetOutput()

            if data is None or data.GetNumberOfPoints() == 0:
                reader = vtk.vtkPolyDataReader()
                reader.SetFileName(filepath)
                reader.Update()
                data = reader.GetOutput()

        elif extension == '.vtu':
            reader = vtk.vtkXMLUnstructuredGridReader()
            reader.SetFileName(filepath)
            reader.Update()
            data = reader.GetOutput()
        elif extension == '.pvtu':
            reader = vtk.vtkXMLPUnstructuredGridReader()
            reader.SetFileName(filepath)
            reader.Update()
            data = reader.GetOutput()
        else:
            raise ValueError(f"Unsupported file extension: {extension}")

        converter = vtk.vtkCellDataToPointData()
        converter.SetInputData(data)
        converter.PassCellDataOn()
        converter.Update()
        
        converted_data = converter.GetOutput()
        
        points = converted_data.GetPoints()
        if points is None:
            return [], [], {}

        vertices = [points.GetPoint(i) for i in range(points.GetNumberOfPoints())]

        faces = []
        for i in range(converted_data.GetNumberOfCells()):
            cell = converted_data.GetCell(i)
            cell_type = cell.GetCellType()
            if cell_type in [vtk.VTK_TRIANGLE, vtk.VTK_QUAD]:
                face = [cell.GetPointId(j) for j in range(cell.GetNumberOfPoints())]
                faces.append(face)
            elif cell_type == vtk.VTK_TETRA:
                for j in range(4):
                    face = [cell.GetPointId(k) for k in range(4) if k != j]
                    faces.append(face)
            elif cell_type == vtk.VTK_HEXAHEDRON:
                indices = [cell.GetPointId(j) for j in range(cell.GetNumberOfPoints())]
                faces.append([indices[0], indices[1], indices[2], indices[3]])
                faces.append([indices[4], indices[5], indices[6], indices[7]])
                faces.append([indices[0], indices[1], indices[5], indices[4]])
                faces.append([indices[1], indices[2], indices[6], indices[5]])
                faces.append([indices[2], indices[3], indices[7], indices[6]])
                faces.append([indices[3], indices[0], indices[4], indices[7]])
            elif cell_type == vtk.VTK_WEDGE:
                indices = [cell.GetPointId(j) for j in range(6)]
                faces.append([indices[0], indices[1], indices[2]])
                faces.append([indices[3], indices[4], indices[5]])
                faces.append([indices[0], indices[1], indices[4], indices[3]])
                faces.append([indices[1], indices[2], indices[5], indices[4]])
                faces.append([indices[2], indices[0], indices[3], indices[5]])
            elif cell_type == vtk.VTK_PYRAMID:
                indices = [cell.GetPointId(j) for j in range(5)]
                faces.append([indices[0], indices[1], indices[2], indices[3]])
                faces.append([indices[0], indices[1], indices[4]])
                faces.append([indices[1], indices[2], indices[4]])
                faces.append([indices[2], indices[3], indices[4]])
                faces.append([indices[3], indices[0], indices[4]])
            elif cell_type == vtk.VTK_VOXEL:
                indices = [cell.GetPointId(j) for j in range(8)]
                faces.append([indices[0], indices[1], indices[3], indices[2]])  
                faces.append([indices[4], indices[5], indices[7], indices[6]])  
                faces.append([indices[0], indices[2], indices[6], indices[4]])  
                faces.append([indices[1], indices[3], indices[7], indices[5]])  
                faces.append([indices[0], indices[1], indices[5], indices[4]])  
                faces.append([indices[2], indices[3], indices[7], indices[6]]) 
            elif cell_type == vtk.VTK_HEXAGONAL_PRISM:
                indices = [cell.GetPointId(j) for j in range(12)]
                faces.append([indices[0], indices[1], indices[2], indices[3], indices[4], indices[5]])
                faces.append([indices[6], indices[7], indices[8], indices[9], indices[10], indices[11]])
                for i in range(6):
                    faces.append([indices[i], indices[(i+1)%6], indices[((i+1)%6)+6], indices[i+6]])
            elif cell_type == vtk.VTK_LINE:
                indices = [cell.GetPointId(0), cell.GetPointId(1)]
            elif cell_type == vtk.VTK_PENTAGONAL_PRISM:
                indices = [cell.GetPointId(j) for j in range(10)]
                faces.append([indices[0], indices[1], indices[2], indices[3], indices[4]])
                faces.append([indices[5], indices[6], indices[7], indices[8], indices[9]])
                for i in range(5):
                    faces.append([indices[i], indices[(i+1)%5], indices[((i+1)%5)+5], indices[i+5]])
            elif cell_type == vtk.VTK_PIXEL:
                indices = [cell.GetPointId(j) for j in range(4)]
                faces.append([indices[0], indices[1], indices[3], indices[2]])
            elif cell_type == vtk.VTK_POLYGON:
                num_points = cell.GetNumberOfPoints()
                indices = [cell.GetPointId(j) for j in range(num_points)]
                faces.append(indices)
            elif cell_type == vtk.VTK_POLYHEDRON:
                num_faces = cell.GetNumberOfFaces()
                for i in range(num_faces):
                    face = cell.GetFace(i)
                    face_indices = [face.GetPointId(j) for j in range(face.GetNumberOfPoints())]
                    faces.append(face_indices)
            elif cell_type == vtk.VTK_POLYLINE:
                num_points = cell.GetNumberOfPoints()
                indices = [cell.GetPointId(j) for j in range(num_points)]
            elif cell_type == vtk.VTK_POLY_VERTEX:
                pass
            elif cell_type == vtk.VTK_QUAD:
                indices = [cell.GetPointId(j) for j in range(4)]
                faces.append(indices)
            elif cell_type == vtk.VTK_TRIANGLE_STRIP:
                num_points = cell.GetNumberOfPoints()
                for i in range(num_points - 2):
                    if i % 2 == 0:
                        faces.append([cell.GetPointId(i), cell.GetPointId(i+1), cell.GetPointId(i+2)])
                    else:
                        faces.append([cell.GetPointId(i+1), cell.GetPointId(i), cell.GetPointId(i+2)])
            elif cell_type == vtk.VTK_VERTEX:
                pass

        point_data = {}
        pd = converted_data.GetPointData()
        for i in range(pd.GetNumberOfArrays()):
            array = pd.GetArray(i)
            base_name = array.GetName()
            num_components = array.GetNumberOfComponents()
            num_tuples = array.GetNumberOfTuples()
            
            if num_components > 1:
                if num_components == 3:
                    magnitudes = []
                    for j in range(num_tuples):
                        vector = array.GetTuple3(j)
                        magnitude = math.sqrt(sum(x*x for x in vector))
                        magnitudes.append(magnitude)
                    point_data[f"{base_name}_Magnitude"] = magnitudes
                    
                    for comp in range(num_components):
                        component_values = []
                        for j in range(num_tuples):
                            component_values.append(array.GetComponent(j, comp))
                        suffix = ['X', 'Y', 'Z'][comp]
                        point_data[f"{base_name}_{suffix}"] = component_values
                else:
                    point_data[base_name] = [array.GetTuple(j) for j in range(num_tuples)]
            else:
                point_data[base_name] = [array.GetValue(j) for j in range(num_tuples)]

        cd = converted_data.GetCellData()
        for i in range(cd.GetNumberOfArrays()):
            array = cd.GetArray(i)
            base_name = array.GetName()
            num_components = array.GetNumberOfComponents()
            num_tuples = array.GetNumberOfTuples()
            
            if num_components > 1:
                cell_values_components = []
                if num_components == 3:
                    magnitudes = []
                    for j in range(num_tuples):
                        vector = array.GetTuple3(j)
                        magnitude = math.sqrt(sum(x*x for x in vector))
                        magnitudes.append(magnitude)
                    cell_values_components.append(('Magnitude', magnitudes))
                
                for comp in range(num_components):
                    component_values = []
                    for j in range(num_tuples):
                        component_values.append(array.GetComponent(j, comp))
                    suffix = ['X', 'Y', 'Z'][comp] if comp < 3 else str(comp)
                    cell_values_components.append((suffix, component_values))
                
                for suffix, cell_values in cell_values_components:
                    vertex_values = []
                    for cell_idx, cell_value in enumerate(cell_values):
                        cell = converted_data.GetCell(cell_idx)
                        num_points = cell.GetNumberOfPoints()
                        vertex_values.extend([cell_value] * num_points)
                    point_data[f"Cell_{base_name}_{suffix}"] = vertex_values
            else:
                cell_values = [array.GetValue(j) for j in range(num_tuples)]
                vertex_values = []
                for cell_idx, cell_value in enumerate(cell_values):
                    cell = converted_data.GetCell(cell_idx)
                    num_points = cell.GetNumberOfPoints()
                    vertex_values.extend([cell_value] * num_points)
                point_data[f"Cell_{base_name}"] = vertex_values

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

class ImportNetCDFOperator(Operator, ImportHelper):
    bl_idname = "import_netcdf.animation"
    bl_label = "Import NetCDF Animation"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".nc"
    filter_glob: StringProperty(default="*.nc;*.nc4", options={'HIDDEN'})

    variable_name: StringProperty(
        name="Variable Name",
        description="Name of the variable to visualize",
        default=""
    )

    time_dimension: StringProperty(
        name="Time Dimension",
        description="Name of the time dimension",
        default="time"
    )

    scale_factor: FloatProperty(
        name="Scale Factor",
        description="Scale factor for imported objects",
        default=1.0,
        min=0.01,
        max=100.0
    )

    axis_forward: EnumProperty(
        name="Forward",
        items=[
            ('X', "X Forward", ""),
            ('Y', "Y Forward", ""),
            ('Z', "Z Forward", ""),
            ('-X', "-X Forward", ""),
            ('-Y', "-Y Forward", ""),
            ('-Z', "-Z Forward", ""),
        ],
        default='Y',
    )

    axis_up: EnumProperty(
        name="Up",
        items=[
            ('X', "X Up", ""),
            ('Y', "Y Up", ""),
            ('Z', "Z Up", ""),
            ('-X', "-X Up", ""),
            ('-Y', "-Y Up", ""),
            ('-Z', "-Z Up", ""),
        ],
        default='Z',
    )

    use_sphere: BoolProperty(
        name="Spherical Projection",
        description="Project data onto a sphere (useful for global/planetary data)",
        default=False
    )

    sphere_radius: FloatProperty(
        name="Sphere Radius",
        description="Radius of the sphere for projection",
        default=1.0,
        min=0.01,
        max=100.0
    )

    height_scale: FloatProperty(
        name="Height Scale",
        description="Scale factor for height values in spherical projection",
        default=0.01,
        min=0.0001,
        max=1.0,
        soft_min=0.001,
        soft_max=0.1
    )

    def execute(self, context):
        try:
            import netCDF4 as nc
            import numpy as np
            import mathutils
            
            dataset = nc.Dataset(self.filepath, 'r')
            
            if not self.variable_name:
                for var_name in dataset.variables:
                    if var_name not in dataset.dimensions:
                        var = dataset.variables[var_name]
                        if len(var.shape) >= 2:  
                            self.variable_name = var_name
                            break
            
            if self.variable_name not in dataset.variables:
                self.report({'ERROR'}, f"Variable '{self.variable_name}' not found")
                return {'CANCELLED'}
            
            variable = dataset.variables[self.variable_name]
            
            if len(variable.shape) < 2:
                self.report({'ERROR'}, f"Variable '{self.variable_name}' must have at least 2 dimensions")
                return {'CANCELLED'}
            
            spatial_dims = []
            for dim_name in variable.dimensions:
                if dim_name != self.time_dimension:
                    spatial_dims.append(dim_name)
            
            if len(spatial_dims) >= 2:
                spatial_sizes = [(dim, len(dataset.dimensions[dim])) for dim in spatial_dims]
                spatial_sizes.sort(key=lambda x: x[1], reverse=True)
                dim_y, dim_x = spatial_sizes[0][0], spatial_sizes[1][0]
            else:
                self.report({'ERROR'}, "Need at least 2 spatial dimensions")
                return {'CANCELLED'}
            
            coords = {}
            for dim_name in variable.dimensions:
                if dim_name in dataset.variables:
                    coords[dim_name] = dataset.variables[dim_name][:]
            
            has_time = self.time_dimension in dataset.dimensions and len(dataset.dimensions[self.time_dimension]) > 0
            if has_time:
                time_steps = len(dataset.dimensions[self.time_dimension])
                time_axis = variable.dimensions.index(self.time_dimension)
                if time_axis != 0:
                    variable_data = np.moveaxis(variable[:], time_axis, 0)
                else:
                    variable_data = variable[:]
            else:
                time_steps = 1
                variable_data = variable[:]
                variable_data = np.expand_dims(variable_data, 0)
            
            if has_time:
                context.scene.frame_start = 1
                context.scene.frame_end = time_steps
            
            material = self.create_material(variable_data, self.variable_name)
            
            for frame in range(time_steps):
                data = variable_data[frame]
                
                vertices = []
                faces = []
                
                spatial_dims = list(variable.dimensions)
                if has_time:
                    spatial_dims.remove(self.time_dimension)
                
                if len(spatial_dims) < 2:
                    self.report({'ERROR'}, "Need at least 2 spatial dimensions")
                    return {'CANCELLED'}
                
                dim_y, dim_x = spatial_dims[-2:]
                rows = len(dataset.dimensions[dim_y])
                cols = len(dataset.dimensions[dim_x])
                
                x_coords = coords.get(dim_x, np.arange(cols))
                y_coords = coords.get(dim_y, np.arange(rows))
                
                for i in range(rows):
                    for j in range(cols):
                        if self.use_sphere:
                            lon = float(x_coords[j])
                            lat = float(y_coords[i])
                            
                            lon_rad = math.radians(lon)
                            lat_rad = math.radians(lat)
                            
                            radius = self.sphere_radius * self.scale_factor
                            x = radius * math.cos(lat_rad) * math.cos(lon_rad)
                            y = radius * math.cos(lat_rad) * math.sin(lon_rad)
                            z = radius * math.sin(lat_rad)
                        else:
                            x = float(x_coords[j]) * self.scale_factor
                            y = float(y_coords[i]) * self.scale_factor
                            z = 0.0
                        
                        try:
                            value = data[i, j]
                            if np.isscalar(value):
                                height = float(value) if not np.isnan(value) else 0.0
                            else:
                                if isinstance(value, np.ndarray):
                                    if value.size > 0 and not np.all(np.isnan(value)):
                                        height = float(np.nanmean(value))
                                    else:
                                        height = 0.0
                                else:
                                    height = 0.0
                        except IndexError:
                            height = 0.0
                        
                        if self.use_sphere:
                            factor = 1.0 + (height * self.height_scale)
                            x *= factor
                            y *= factor
                            z *= factor
                        else:
                            z = height
                        
                        vertices.append((x, y, z))
                
                for i in range(rows - 1):
                    for j in range(cols - 1):
                        v0 = i * cols + j
                        v1 = v0 + 1
                        v2 = (i + 1) * cols + j + 1
                        v3 = (i + 1) * cols + j
                        faces.append([v0, v1, v2, v3])
                
                mesh_name = f"Frame_{frame+1}" if has_time else f"NetCDF_{self.variable_name}"
                mesh = bpy.data.meshes.new(mesh_name)
                obj = bpy.data.objects.new(mesh_name, mesh)
                
                mesh.from_pydata(vertices, [], faces)
                mesh.update()
                
                self.add_attributes(mesh, data, coords, dim_x, dim_y)
                
                context.collection.objects.link(obj)
                obj.data.materials.append(material)
                
                if has_time:
                    self.setup_animation(obj, frame, time_steps)
            
            dataset.close()
            self.report({'INFO'}, "Imported NetCDF data successfully")
            return {'FINISHED'}
        
        except Exception as e:
            self.report({'ERROR'}, f"Error importing file: {str(e)}")
            return {'CANCELLED'}

    def add_attributes(self, mesh, data, coords, dim_x, dim_y):
        attr = mesh.attributes.new(name=self.variable_name, type='FLOAT', domain='POINT')
        for i, value in enumerate(data.flatten()):
            attr.data[i].value = float(value) if not np.isnan(value) else 0.0
        
        if dim_x in coords:
            attr_x = mesh.attributes.new(name=f"coord_{dim_x}", type='FLOAT', domain='POINT')
            for i, x in enumerate(coords[dim_x]):
                attr_x.data[i].value = float(x)
        
        if dim_y in coords:
            attr_y = mesh.attributes.new(name=f"coord_{dim_y}", type='FLOAT', domain='POINT')
            for i, y in enumerate(coords[dim_y]):
                attr_y.data[i].value = float(y)

    def create_material(self, variable_data, variable_name):
        material = bpy.data.materials.new(name=f"NetCDF_{variable_name}_Material")
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        nodes.clear()

        attribute_node = nodes.new(type='ShaderNodeAttribute')
        attribute_node.attribute_name = variable_name

        map_range = nodes.new(type='ShaderNodeMapRange')
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        output = nodes.new(type='ShaderNodeOutputMaterial')

        try:
            data = np.asarray(variable_data)
            flat_data = data.ravel()
            valid_mask = np.logical_and(~np.isnan(flat_data), ~np.isinf(flat_data))
            
            if valid_mask.size > 0 and valid_mask.any():
                valid_data = flat_data[valid_mask]
                if valid_data.size > 0:
                    min_val = float(np.min(valid_data))
                    max_val = float(np.max(valid_data))
                else:
                    min_val = 0.0
                    max_val = 1.0
            else:
                min_val = 0.0
                max_val = 1.0
            
        except Exception as e:
            print(f"Error calculating min/max values: {e}")
            min_val = 0.0
            max_val = 1.0

        map_range.inputs['From Min'].default_value = min_val
        map_range.inputs['From Max'].default_value = max_val
        map_range.inputs['To Min'].default_value = 0.0
        map_range.inputs['To Max'].default_value = 1.0

        links.new(attribute_node.outputs['Fac'], map_range.inputs['Value'])
        links.new(map_range.outputs['Result'], color_ramp.inputs['Fac'])
        links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

        return material

    def setup_animation(self, obj, frame, time_steps):
        obj.hide_viewport = False
        obj.hide_render = False
        obj.keyframe_insert(data_path="hide_viewport", frame=frame+1)
        obj.keyframe_insert(data_path="hide_render", frame=frame+1)
        
        obj.hide_viewport = True
        obj.hide_render = True
        if frame > 0:
            obj.keyframe_insert(data_path="hide_viewport", frame=frame)
            obj.keyframe_insert(data_path="hide_render", frame=frame)
        if frame < time_steps - 1:
            obj.keyframe_insert(data_path="hide_viewport", frame=frame+2)
            obj.keyframe_insert(data_path="hide_render", frame=frame+2)

        if obj.animation_data and obj.animation_data.action:
            for fcurve in obj.animation_data.action.fcurves:
                for kf in fcurve.keyframe_points:
                    kf.interpolation = 'CONSTANT'
