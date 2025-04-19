# SciBlend: Advanced Scientific Visualization for Blender v.3.1.0

![SciBlend Banner](images/banner.png)
*A sequence of heart models from simulation data, including electrical activation and mechanical contraction, rendered in Blender's Cycles engine using the SciBlend toolkit. The colour scale and legend indicate displacement magnitude. SciBlend Advanced Core supports import into Blender various computational file formats (e.g., VTK, netCDF, SHP) for both static and animated data and visualization in real-time*

SciBlend Advanced Core v.3.1.0 is a powerful add-on for Blender 4.2+ that represents a significant evolution from its predecessor, [SciBlend-Core](https://github.com/josemarinfarina/SciBlend-Core). This advanced version is characterized by its requirement for a more complex setup process, primarily due to the need to install VTK (Visualization Toolkit), netCDF4, and additional geospatial libraries within Blender's Python environment.

SciBlend bridges the gap between scientific data processing and high-quality 3D visualization. By integrating VTK, VTU, PVTU, NetCDF, and Shapefile capabilities directly into Blender, SciBlend allows researchers and scientists to create stunning, photorealistic visualizations of complex scientific and geospatial data.

Unlike SciBlend-Core, which primarily focused on importing data from Paraview, this advanced version offers deeper integration with scientific data formats through VTK, VTU, PVTU, NetCDF, and Shapefiles, allowing for more sophisticated data manipulations and visualizations directly within Blender. The addition of advanced geospatial features like Delaunay triangulation and terrain modeling makes it particularly powerful for working with geographic and topographic data.

## What's New in Version 3.0.0


- **New Export Options**: 
  - **Universal Export Macro**: The new `export_macro.py` is a comprehensive solution for exporting data from Paraview in multiple formats:
    * Supports a wide range of formats (CSV, PLY, VTK, VTP, X3D, STL, VTM, CGNS)
    * Intelligently detects and optimizes export based on data type
    * Handles both static and time-series data
    * Provides fallback options for better export reliability
  - **GoB/GoP Bridge**: Specialized tool for real-time VTK data transfer between Paraview and Blender
    * Focused on live visualization and interactive workflows
    * Optimized for VTK format specifically
    * Ideal for iterative visualization adjustments
- **Scene Overwrite Control**: New option to control whether imports overwrite existing scene objects or add to the current scene.
- **Improved VTK Compatibility**: Enhanced compatibility with VTK 9.2.x and 9.3.x.
- **Robustness Improvements**: Better error handling and compatibility across different operating systems.


## Table of Contents

1. [Features](#features)
2. [Requirements](#requirements)
3. [Installation](#installation)
   - [VTK and netCDF4 Installation](#vtk-and-netcdf4-installation)
   - [SciBlend Addon Installation](#sciblend-addon-installation)
   - [Paraview Addons Installation](#paraview-addons-installation)
4. [Usage](#usage)
   - [Exporting from Paraview](#exporting-from-paraview)
     * [Using GoB/GoP Bridge](#using-gob/gop-bridge)
     * [Using the Export Macro](#using-the-export-macro)
   - [Importing in Blender](#importing-in-blender)
     * [VTK/VTU/PVTU Files](#importing-vtk/vtu/pvtu-files)
     * [NetCDF Files](#importing-netcdf-files)
     * [Shapefile (.shp) Files](#importing-shapefile-shp-files)
5. [Advanced Features](#advanced-features)
6. [Contributing](#contributing)
7. [Support](#support)

## Features

- **Comprehensive Format Support**: 
  - Import VTK (.vtk) files with legacy format support
  - Full support for XML UnstructuredGrid Format (.vtu)
  - Support for Parallel XML UnstructuredGrid Format (.pvtu)
  - Support for NetCDF (.nc) and NetCDF4 (.nc4) files
  - Support for Shapefiles (.shp) with advanced processing capabilities
  - Preserves complex scientific data structures and attributes

- **Advanced Cell Type Support**:
  - Basic Elements: Vertex, Line, Pixel, Triangle Strip, Quad, Polygon
  - 3D Elements: Tetrahedron, Hexahedron, Wedge, Pyramid, Voxel
  - Advanced Elements: Hexagonal Prism, Pentagonal Prism, Polyhedron
  - Linear Elements: Polyline, Poly-Vertex
  - Shapefile Elements: Points, Lines, Polygons with Delaunay triangulation

- **Data Attribute Processing**:
  - Automatic conversion of cell data to point data
  - Vector component separation (Magnitude, X, Y, Z)
  - Independent visualization of each data component
  - Automatic material generation for each attribute
  - Delaunay triangulation for terrain point clouds

- **Scene Management Options**:
  - Control whether imports overwrite existing objects or add to the current scene
  - Organize geometry into hierarchical collections for better scene organization

- **GoB/GoP Paraview Bridge**:
  - Direct connection between Blender and Paraview
  - Realtime data transfer and visualization
  - Compatible with Paraview 5.10+ running the GoP macro

- **Advanced Animation Support**: Create smooth animations from time-series data with automatic keyframing.
- **Dynamic Material Management**: Automatically generate and apply materials based on data attributes.
- **Geometry Organization**: Efficiently organize imported geometry into collections for better scene management.
- **Boolean Operations**: Perform advanced boolean operations for data analysis and visualization.
- **Customizable Import Settings**: Fine-tune import parameters such as scale, axis orientation, and frame range.
- **Advanced Visualization Options**:
  - Spherical Projection for global/planetary data when importing NetCDF files.
  - Adjustable sphere radius and height scaling
  - Support for both planar and spherical data representation
  - Automatic handling of latitude/longitude coordinates

## Requirements

- Blender 4.2 or higher

- Python 3.11 (bundled with Blender 4.2+)

- VTK 9.2.6 or 9.3.0 (installation instructions provided)

- netCDF4 (installation instructions provided)


## Installation

### VTK and netCDF4 Installation

Installing VTK and netCDF4 within Blender's Python environment is a crucial step. Follow these instructions carefully:

#### 1. Verify the Python Version in Blender:
First, ensure that Blender is using Python 3.11. Open Blender's Python Console and type:

```python
import sys
print(sys.version)
```

You should see an output like `Python 3.11.x`.

#### 2. Access Blender's Python Environment:
Blender includes its own Python environment, so we need to install VTK within that specific environment.

In your system's terminal (not Blender's console), navigate to where Blender is installed.

##### On Linux/macOS:
```bash
cd /path_to_blender/blender-4.2.1-linux-x64/4.2/python/bin
```

##### On Windows (Run in CMD or PowerShell):
```powershell
cd C:\path_to_blender\blender-4.2.1-windows64\4.2\python\bin
```

#### 3. Install VTK:

Once in the correct directory, you can install VTK using `pip`. Ensure that you're installing a compatible version of VTK for Python 3.11.

##### Run the following command to install VTK:

```bash
./python3.11 -m pip install vtk==9.3.0
```

For Windows, the command will be:

```powershell
python3.11 -m pip install vtk==9.3.0
```

#### 4. Optional: Modify VTK Files to Fix Compatibility (In case of issues related to VTK Installation, very common if you have installed matplotlib in the Blender Python environment before):

After installing VTK, there may be some compatibility issues with certain imports that need to be addressed. We will modify some VTK Python files.

##### Edit `vtk.py`:

1. Open the `vtk.py` file located in Blender's Python environment:

   - On Linux/macOS:
     ```bash
     nano /path_to_blender/blender-4.2.1-linux-x64/4.2/python/lib/python3.11/site-packages/vtk.py
     ```

   - On Windows:
     Open the file at `C:\path_to_blender\blender-4.2.1-windows64\4.2\python\lib\python3.11\site-packages\vtk.py` using a text editor like Notepad.

2. Find the line that says:

   ```python
   from vtkmodules.vtkRenderingMatplotlib import *
   ```

3. Comment out this line by adding a `#` at the beginning:

   ```python
   # from vtkmodules.vtkRenderingMatplotlib import *
   ```

4. Save and close the file.

##### Edit `all.py`:

1. Similarly, open the `all.py` file located in the same directory:

   - On Linux/macOS:
     ```bash
     nano /path_to_blender/blender-4.2.1-linux-x64/4.2/python/lib/python3.11/site-packages/vtkmodules/all.py
     ```

   - On Windows:
     Open the file at `C:\path_to_blender\blender-4.2.1-windows64\4.2\python\lib\python3.11\site-packages\vtkmodules\all.py`.

2. Comment out the same line as before:

   ```python
   # from vtkmodules.vtkRenderingMatplotlib import *
   ```

3. Save and close the file.

#### 5. Install netCDF4:

After installing VTK, install netCDF4 using pip in the Blender Python environment:

##### On Linux/macOS:
```bash
  ./python3.11 -m pip install netCDF4
```

##### On Windows:
```powershell
python3.11 -m pip install netCDF4
```

#### 6. Install required dependencies for shapefile support:

After installing VTK and netCDF4, install the following packages using pip in the Blender Python environment:

##### On Linux/macOS:
```bash
./python3.11 -m pip install geopandas
./python3.11 -m pip install pytz
./python3.11 -m pip install shapely
./python3.11 -m pip install fiona
```

##### On Windows:
```powershell
python3.11 -m pip install geopandas
python3.11 -m pip install pytz
python3.11 -m pip install shapely
python3.11 -m pip install fiona
```


### SciBlend Addon Installation

1. Download the SciBlend zip file from the releases page.
2. In Blender, go to Edit > Preferences > Add-ons.
3. Click "Install" and select the downloaded zip file.
4. Enable the SciBlend addon by checking the box next to it.

### Paraview Addons Installation

#### Installing GoP (GoParaview)
1. Locate the `GoP.py` macro file in the Paraview Macros folder of your SciBlend installation
2. In Paraview, go to Tools > Manage Plugins/Macros > Macros > Add
3. Select the GoP macro file
4. The macro will be available in the Macros menu

#### Installing Export Macro
1. Locate the `export_macro.py` file in the Paraview Macros folder
2. In Paraview, go to Tools > Manage Plugins/Macros > Macros > Add
3. Select the `export_macro.py` file
4. The macro will appear as "PARAVIEW MULTI-FORMAT EXPORTER" in the Macros menu

## Usage

![Aorta Visualization](images/AORTA_RENDER.png)
*Illustrative frame from the Aorta Dataset. A semitransparent render of the aorta wall containing flow streamlines and velocity glyphs. Shader is encoded by velocity magnitude [m/s] using a black–blue–white colourmap. Visualizations were rendered with Cycles Render and imported using SciBlend Advanced Core*

### Exporting from Paraview

#### Using GoB/GoP Bridge

SciBlend Advanced Core 3.1.0 introduces a new feature: a port between Blender and Paraview called GoB (GoBlender) and GoP (GoParaview), inspired by GoZ (Zbrush).

##### Using GoP in Paraview:
1. Select the object you want to dynamically export to Blender
2. Click "GoP" in the Macros menu
3. The macro will start a server on port 9998 (default)

##### Connecting from Blender:
1. In Blender, go to the SciBlend panel
2. Scroll down to the "GoB - Paraview Bridge" section
3. Configure connection settings:
   - Host: The IP address of the computer running Paraview (use "localhost" if on the same machine)
   - Port: The port number (default: 9998)
4. Click "Connect to Paraview"
5. Once connected, you'll see "Refresh" and "Disconnect" buttons

##### Using the Connection:
1. In Paraview, make your visualization selections and setup
2. Any changes in Paraview will be automatically sent to Blender
3. Use the "Refresh" button in Blender to request the latest data from Paraview
4. Use the "Disconnect" button when finished

##### Benefits:
- Live connection between the two applications
- Direct transfer of mesh data with attributes
- No need to export intermediate files
- Allows for iterative workflow between Paraview and Blender

Note: For reliable operation, ensure both Blender and Paraview are running on machines with good network connectivity.

#### Using the Export Macro

The `export_macro.py` provides a more comprehensive solution for exporting data from Paraview in various formats, ideal for when you need specific file formats or want to preserve your data for later use.

1. Load the macro in Paraview:
   - Go to Tools > Manage Macros
   - Click "Add" and select `export_macro.py` from the Paraview Macros folder
   - The macro will appear as "PARAVIEW MULTI-FORMAT EXPORTER"

2. Using the exporter:
   - Select the object you want to export in the Pipeline Browser
   - Run the macro
   - The macro will automatically detect your data type and offer appropriate format options:
     * For point clouds: CSV, PLY, VTK, VTP, X3D
     * For meshes: VTK, PLY, STL, VTP, X3D
     * For multiblock data: VTM, CGNS
   - Choose your preferred format
   - Specify the save location
   - For animations, you can select specific frame ranges to export

3. Advanced Features:
   - Automatic data type detection optimizes the export process
   - Format-specific optimizations ensure best quality exports
   - Automatic fallback to VTK format if the primary format fails
   - Detailed progress tracking and user feedback
   - Support for both single frames and time-series data
   - Handles missing data and provides error recovery

4. Best Practices:
   - Use CSV for simple point cloud data when you need human-readable format
   - Choose PLY or VTP for point clouds with additional attributes
   - Use STL for simple mesh exports, especially for 3D printing
   - Select VTK/VTP for preserving all data attributes
   - Use VTM for complex multiblock datasets
   - Enable the fallback option for critical exports

### Importing in Blender

#### Importing VTK/VTU/PVTU Files

When working with VTK files:
1. Use the "Import VTK Animation" option in the SciBlend panel
2. Select your file(s):
   - For .vtk files: Select your legacy VTK files
   - For .vtu files: Select all XML UnstructuredGrid files
   - For .pvtu files: Select all Parallel XML UnstructuredGrid files
3. Configure import settings:
   - Set frame range for animations
   - Adjust scale factor if needed
   - Configure axis orientation
   - Set up material options
   - Choose whether to overwrite the scene or add to it

For animation sequences:
1. Select all files in your time series (e.g., time_0.vtu, time_1.vtu, time_2.vtu)
2. Ensure files are properly numbered for correct sequence order
3. The addon will automatically:
   - Create keyframes for animation
   - Handle timing between frames
   - Organize files in sequential order

The data will be automatically:
- Converted to appropriate mesh formats
- Mapped to materials based on data attributes
- Organized into frame collections for time-series data
- Handled for missing or invalid data

![Global Temperature Visualization](images/NC_RENDER6.jpg)
*Climate data from Copernicus Dataset imported from NetCDF format via SciBlend Advanced Core with the Spherical Projection feature and rendered with Cycles.*

#### Importing NetCDF Files

When working with NetCDF files:
1. Use the "Import NetCDF Animation" option in the SciBlend panel
2. Select your .nc or .nc4 file
3. Configure import settings:
   - Choose the variable to visualize
   - Set time dimension name (default: "time")
   - Adjust scale factor if needed
   - Configure axis orientation
   - Choose whether to overwrite the scene or add to it

For global or planetary data visualization:
1. Enable "Spherical Projection" in the import settings
2. Adjust "Sphere Radius" to set the base size of the sphere (default: 1.0)
3. Use "Height Scale" to control the intensity of elevation changes (default: 0.01)
   - Lower values (0.001-0.01) for subtle elevation changes
   - Higher values (0.01-0.1) for more pronounced elevation differences

The data will be automatically:
- Mapped to colors using a customizable color ramp
- Organized into frame collections for time-series data
- Projected onto a sphere when using spherical projection
- Handled for missing values (NaN) and invalid data

Note: When using spherical projection, latitude/longitude coordinates will be automatically converted to 3D coordinates on the sphere's surface.

Note: The import process may take some time depending on the size 
and number of files in your sequence.

#### Importing Shapefile (.shp) Files

When working with Shapefile (.shp) data:
1. Use the "Import Shapefile" option in the SciBlend panel
2. Select your .shp file
3. Configure import settings:
   - Adjust scale factor if needed
   - Configure axis orientation
   - Set up material options
   - Choose whether to overwrite the scene or add to it

For terrain and point cloud data:
1. Select the imported mesh object(s)
2. Use the "Apply Delaunay" option to create a triangulated surface
3. The addon will automatically:
   - Process and remove duplicate points
   - Handle z-colinear points
   - Create a TIN (Triangulated Irregular Network) mesh
   - Preserve original materials and attributes

The Delaunay triangulation feature supports:
- Native Blender CDT (Constrained Delaunay Triangulation) when available
- Custom triangulation algorithm as fallback
- Automatic handling of duplicate vertices
- Material transfer from source objects

![Terrain Visualization](images/shapefile_figure_blackBG.png)
*Three-dimensional rendering of topographic data from a Shapefile file. Colour intensity on the contour lines corresponds to elevation magnitude [m], mapped via a black-blue-white colourmap. The underlying spatial connectivity is represented by a Delaunay triangulation of the vertices achieved with SciBlend Advanced Core module, shown in black lines.*

## Advanced Features

- **Automatic Material Generation**: SciBlend creates materials based on VTK data attributes, allowing for immediate visualization of scalar fields.
- **Frame-by-Frame Geometry Management**: Imported geometries are organized into frame-specific collections for easy management of time-series data.
- **Dynamic Boolean Operations**: Perform real-time boolean operations on your data for advanced analysis and visualization techniques.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve this project.

## Support

For questions, issues, or feature requests, please use the GitHub issue tracker or contact the maintainer at info@sciblend.com.

