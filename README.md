# SciBlend: Advanced Scientific Visualization for Blender v.2.1.0

SciBlend AdvancedCore is a powerful add-on for Blender 4.2+ that represents a significant evolution from its predecessor, [SciBlend-Core](https://github.com/josemarinfarina/SciBlend-Core). This advanced version is characterized by its requirement for a more complex setup process, primarily due to the need to install VTK (Visualization Toolkit) within Blender's Python environment.

SciBlend bridges the gap between scientific data processing and high-quality 3D visualization. By integrating VTK, VTU and PVTU capabilities directly into Blender, SciBlend allows researchers and scientists to create stunning, photorealistic visualizations of complex scientific data.

Unlike SciBlend-Core, which primarily focused on importing data from Paraview, this advanced version offers deeper integration with scientific data formats through VTK, VTU and PVTU, allowing for more sophisticated data manipulations and visualizations directly within Blender.

## Table of Contents

1. [Features](#features)
2. [Requirements](#requirements)
3. [Installation](#installation)
   - [VTK Installation](#vtk-installation)
   - [SciBlend Addon Installation](#sciblend-addon-installation)
4. [Usage](#usage)
5. [Advanced Features](#advanced-features)
6. [Contributing](#contributing)
7. [Support](#support)

## Features

- **Comprehensive Format Support**: 
  - Import VTK (.vtk) files with legacy format support
  - Full support for XML UnstructuredGrid Format (.vtu)
  - Support for Parallel XML UnstructuredGrid Format (.pvtu)
  - Preserves complex scientific data structures and attributes

- **Advanced Cell Type Support**:
  - Basic Elements: Vertex, Line, Pixel, Triangle Strip, Quad, Polygon
  - 3D Elements: Tetrahedron, Hexahedron, Wedge, Pyramid, Voxel
  - Advanced Elements: Hexagonal Prism, Pentagonal Prism, Polyhedron
  - Linear Elements: Polyline, Poly-Vertex

- **Data Attribute Processing**:
  - Automatic conversion of cell data to point data
  - Vector component separation (Magnitude, X, Y, Z)
  - Independent visualization of each data component
  - Automatic material generation for each attribute

- **Advanced Animation Support**: Create smooth animations from time-series data with automatic keyframing.
- **Dynamic Material Management**: Automatically generate and apply materials based on data attributes.
- **Geometry Organization**: Efficiently organize imported geometry into collections for better scene management.
- **Boolean Operations**: Perform advanced boolean operations for data analysis and visualization.
- **Customizable Import Settings**: Fine-tune import parameters such as scale, axis orientation, and frame range.

## Requirements

- Blender 4.2 or higher

- Python 3.11 (bundled with Blender 4.2+)

- VTK 9.3.0 (installation instructions provided)


## Installation

### VTK Installation

Installing VTK within Blender's Python environment is a crucial step. Follow these instructions carefully:

#### 1. Verify the Python Version in Blender:
First, ensure that Blender is using Python 3.11. Open Blender's Python Console and type:

```python
import sys
print(sys.version)
```

You should see an output like `Python 3.11.x`.

#### 2. Access Blender’s Python Environment:
Blender includes its own Python environment, so we need to install VTK within that specific environment.

In your system’s terminal (not Blender's console), navigate to where Blender is installed.

##### On Linux/macOS:
```bash
cd /path_to_blender/blender-4.2.1-linux-x64/4.2/python/bin
```

##### On Windows (Run in CMD or PowerShell):
```powershell
cd C:\path_to_blender\blender-4.2.1-windows64\4.2\python\bin
```

#### 3. Install VTK:

Once in the correct directory, you can install VTK using `pip`. Ensure that you’re installing a compatible version of VTK for Python 3.11.

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



### SciBlend Addon Installation

1. Download the SciBlend zip file from the releases page.
2. In Blender, go to Edit > Preferences > Add-ons.
3. Click "Install" and select the downloaded zip file.
4. Enable the SciBlend addon by checking the box next to it.

## Usage

1. Open the SciBlend panel in the 3D Viewport sidebar.
2. Use the "Import VTK Animation" option to import your files:
   - For .vtk files (Legacy VTK format): Select your .vtk files in your sequence.
   - For .vtu files (XML UnstructuredGrid format): Select ALL .vtu files in your sequence.
   - For .pvtu files (Parallel XML UnstructuredGrid format): Select ALL .pvtu files in your sequence.
3. Click "Import VTK/VTU/PVTU Animation" to start the import process.
4. Adjust import settings as needed (scale, axis orientation, frame range).
5. Use the various tools provided to organize, manipulate, and visualize your data.

### Importing Animation Sequences

When working with animation sequences:
- For .vtu files: Select all the files in your time series (e.g., time_0.vtu, time_1.vtu, time_2.vtu, etc.)
- For .pvtu files: Select all the parallel files in your sequence
- The addon will automatically create keyframes and handle the animation timing
- Files will be imported in alphabetical order, so ensure your files are properly numbered

Note: The import process may take some time depending on the size and number of files in your sequence.

## Advanced Features

- **Automatic Material Generation**: SciBlend creates materials based on VTK data attributes, allowing for immediate visualization of scalar fields.
- **Frame-by-Frame Geometry Management**: Imported geometries are organized into frame-specific collections for easy management of time-series data.
- **Dynamic Boolean Operations**: Perform real-time boolean operations on your data for advanced analysis and visualization techniques.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve this project.

## Support

For questions, issues, or feature requests, please use the GitHub issue tracker or contact the maintainer at info@sciblend.com.
