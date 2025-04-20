# 3D OBJ Viewer

A Python-based 3D model viewer that supports loading and rendering OBJ files with features like rotation, scaling, and texture mapping.

## Features

- Load and display 3D OBJ files
- Support for textured models
- Interactive camera controls
- Material file (.mtl) support
- Custom shader support (vertex and fragment)
- Real-time model manipulation
- Multiple view modes and color schemes

## Prerequisites

- Python 3.x
- Pygame
- NumPy

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/3dviewerproject.git
cd 3dviewerproject
```

2. Install required dependencies:
```bash
pip install pygame numpy
```

## Usage

1. Run the viewer:
```bash
python main.py
```

2. Controls:
- Left Mouse Button: Rotate model
- Right Mouse Button: Pan camera
- Mouse Wheel: Zoom in/out
- Space: Toggle between different view modes
- C: Change background color
- V: Toggle vertex display
- E: Toggle edge display
- ESC: Exit viewer

3. Loading Models:
- Place your OBJ files in the project directory
- The viewer will automatically load available OBJ files
- Supported formats: .obj, .mtl (for materials)

## Project Structure

- `main.py`: Main application file
- `model_loader.py`: OBJ file loading and parsing
- `model_camera.py`: Camera and view controls
- `shader.py`: Shader implementation
- `shadersvertex.glsl.txt`: Vertex shader code
- `shadersfragment.glsl.txt`: Fragment shader code

## Supported File Formats

- OBJ files (.obj)
- Material files (.mtl)
- Texture files (various formats supported by Pygame)

## Customization

### Shaders
You can modify the shaders by editing:
- `shadersvertex.glsl.txt`
- `shadersfragment.glsl.txt`

### Colors and Display
Modify the following variables in `main.py`:
- Background colors
- Edge colors
- Vertex colors

## Troubleshooting

Common issues and solutions:
1. Model not loading: Ensure the OBJ file is in the correct directory
2. Textures not showing: Check if texture paths in MTL files are correct
3. Performance issues: Reduce model complexity or adjust view settings

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Pygame community
- OpenGL community
- Contributors and users of this project
