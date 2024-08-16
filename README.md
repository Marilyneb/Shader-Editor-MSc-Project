# Shader-Editor-MSc-Project


## Overview
The Interactive Shader Editor is a Python-based application that allows users to create and edit GLSL shaders using both a visual node-based editor and a text-based code editor. It uses PySide6 for the GUI and OpenGL for rendering the shaders in real-time.

## Features
- **Node-Based Shader Creation**: Create 2D shaders visually by connecting different nodes that represent various operations and inputs.
- **Code Editor**: Edit GLSL shader code directly with syntax highlighting and real-time error feedback. Create 2D and 3D shaders.
- **Real-Time Preview**: View the results of your shader in a dedicated OpenGL viewport.
- **Custom Node Implementation**: Extend functionality by implementing custom nodes that generate specific GLSL code.
- **Shader Compilation**: Compile shaders directly within the application and receive feedback on success or errors.

## Project Structure
- **`code_editor.py`**: Implements the code editor with syntax highlighting and error highlighting for GLSL code.
- **`custom_nodes.py`**: Contains custom nodes for the node editor, including color selection, shading models, and more.
- **`main_window.py`**: The main window of the application, integrating all components including the OpenGL viewport, node editor, and code editor.
- **`node_editor.py`**: Manages the visual node editor, allowing users to create and connect nodes to generate GLSL code.
- **`OpenGL_widget.py`**: Handles the OpenGL context and rendering of the shader in real-time. Also manages shader compilation and geometry setup.
- **`shader_program.py`**: Manages the creation, compilation, and use of GLSL shaders in OpenGL.
- **`shader_utils.py`**: Utility functions for loading shader sources from files.

## Getting Started

### Prerequisites
- Python 3.x
- PySide6
- PyOpenGL
- NodeGraphQt (for the node editor)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/shader-editor.git
   cd shader-editor
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
3. Run the application:
    ```bash
    python main_window.py
## Usage

- **Node Editor Tab**: Create and connect nodes to build a shader visually. Right-click to add new nodes. Press delete to delete nodes. 
- **Code Editor Tab**: Write GLSL code directly. Any changes will be reflected in the OpenGL preview.
- **Compile Button**: Click to compile the current shader and see the results in the OpenGL viewport.

### Loading Default Shaders
You can load two default example shaders included with the application:
1. **Load Example Shader**: Navigate to the File menu and select "Load Example Shader" to load a basic blue color shader or 3D scene
