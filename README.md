# SciBlend Advanced Core


[![Blender 4.5.1+](https://img.shields.io/badge/Blender-4.5.1%2B-orange?logo=blender)](https://www.blender.org)
[![License: GPL-3.0-or-later](https://img.shields.io/badge/License-GPL--3.0--or--later-blue.svg)](LICENSE)

![SciBlend Banner](images/banner.png)


SciBlend Advanced Core bridges the gap between scientific data processing and high-quality 3D visualization. By integrating VTK, VTU, PVTU, NetCDF, and Shapefile capabilities directly into Blender, allowing researchers and scientists to create stunning, photorealistic visualizations of complex scientific and geospatial data.











## Download v.4.0.0

- [![Linux x64](https://img.shields.io/badge/Download-Linux%20x64-2ea44f?logo=linux)](https://github.com/OWNER/REPO/releases/latest/download/sciblend_advanced_core-4.0.0-linux_x64.zip)
- [![Windows x64](https://img.shields.io/badge/Download-Windows%20x64-2ea44f?logo=windows)](https://github.com/OWNER/REPO/releases/latest/download/sciblend_advanced_core-4.0.0-windows_x64.zip)
- [![macOS x64](https://img.shields.io/badge/Download-macOS%20x64-2ea44f?logo=apple)](https://github.com/OWNER/REPO/releases/latest/download/sciblend_advanced_core-4.0.0-macos_x64.zip)
- [![macOS arm64](https://img.shields.io/badge/Download-macOS%20arm64-2ea44f?logo=apple)](https://github.com/OWNER/REPO/releases/latest/download/sciblend_advanced_core-4.0.0-macos_arm64.zip)

Tip: If the direct links don’t match your release tag/file names, go to Releases and download the ZIP for your platform. The extension contains all required Python wheels and works fully offline.


## What is it?
SciBlend Advanced Core boosts Blender with scientific data workflows:
- VTK/VTU/PVTU import (polydata and unstructured grids), with robust VTK modules integration
- NetCDF import (time-series, spherical projection, per-point attributes)
- Shapefile import (DBF attributes, optional extrusion, Delaunay tools)
- X3D import (static/animated)
- Utilities: scene setup, grouping, shared materials

## Requirements
- Blender 4.5.1+

## Install (2 steps)
1) Download the ZIP for your platform (see buttons above)
2) In Blender: Edit → Preferences → Extensions → Install From Disk… → select the ZIP → Enable

CLI (optional):
```bash
/path/to/blender --command extension install-file -r user_default -e /path/to/sciblend_advanced_core-4.0.0-<platform>.zip
```

## Usage
- Open the panel: Viewport → Sidebar → “SciBlend Advanced Core”
- Importers:
  - “Import VTK/VTU/PVTU Animation” (multi-file animation or single frame)
  - “Import NetCDF Animation” (time-series supported)
  - “Import Shapefile” (attributes and extrusion)
  - “Import Static/Animation X3D”
- For single-file VTK imports the object is visible immediately; for sequences, frame visibility is keyframed.

## Gallery

![Aorta Visualization](images/AORTA_RENDER.png)
*Illustrative frame from the Aorta Dataset. A semitransparent render of the aorta wall containing flow streamlines and velocity glyphs. Shader is encoded by velocity magnitude [m/s] using a black–blue–white colourmap. Visualizations were rendered with Cycles Render and imported using SciBlend Advanced Core*

![Global Temperature Visualization](images/NC_RENDER6.jpg)
*Climate data from Copernicus Dataset imported from NetCDF format via SciBlend Advanced Core with the Spherical Projection feature and rendered with Cycles.*

![Terrain Visualization](images/shapefile_figure_blackBG.png)
*Three-dimensional rendering of topographic data from a Shapefile file. Colour intensity on the contour lines corresponds to elevation magnitude [m], mapped via a black-blue-white colourmap. The underlying spatial connectivity is represented by a Delaunay triangulation of the vertices achieved with SciBlend Advanced Core module, shown in black lines.*


## 📜 Citing SciBlend

If SciBlend or its components are used in research or publications, please include the following citations:

1.  **The SciBlend Paper:**

```
@article{marin2025,
title = {SciBlend: Advanced data visualization workflows within Blender},
journal = {Computers & Graphics},
volume = {130},
pages = {104264},
year = {2025},
issn = {0097-8493},
doi = {https://doi.org/10.1016/j.cag.2025.104264},
url = {https://www.sciencedirect.com/science/article/pii/S0097849325001050},
author = {José Marín and Tiffany M.G. Baptiste and Cristobal Rodero and Steven E. Williams and Steven A. Niederer and Ignacio García-Fernández},
keywords = {Scientific visualisation, Blender, Paraview, Data rendering, Visual storytelling, Scientific communication}
}
```

3.  **The Software Suite:**
```
@software{sciblend2025,
doi = {10.5281/ZENODO.15420392},
url = {https://zenodo.org/doi/10.5281/zenodo.15420392},
author = {José Marín},
title = {SciBlend: Advanced Data Visualization Workflows within Blender - Software},
publisher = {Zenodo},
year = {2025},
copyright = {Creative Commons Attribution 4.0 International}
}
```


(Source code: https://github.com/SciBlend/SciBlend)



## Support
For questions, issues, or feature requests, please use the GitHub issue tracker or contact the maintainer at info@sciblend.com.

## Contribution

Contributions are welcome! Feel free to open issues or submit pull requests to improve this project.

## License
- GPL-3.0-or-later. See LICENSE.

