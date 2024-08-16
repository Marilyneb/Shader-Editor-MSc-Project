from PySide6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QMenuBar, QFileDialog, QSplitter, QPushButton
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from ui.opengl_widget import OpenGLWidget
from ui.code_editor import CodeEditor
from ui.node_editor import NodeEditorView
from ui.nodes.custom_nodes import TextureNode

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interactive Shader Editor")
        self.resize(1200, 800)

        self.opengl_widget = OpenGLWidget()

        self.node_editor_widget = NodeEditorView()
        self.node_editor_widget.node_selected.connect(self.update_code_editor)

        self.code_editor = CodeEditor()
        self.code_editor.textChanged.connect(self.compile_shader)  # Fix this line

        self.opengl_widget.shader_compiled.connect(self.on_shader_compiled)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.node_editor_widget, "Node Editor")
        self.tabs.addTab(self.code_editor, "Code Editor")

        self.status_label = QLabel("")

        self.compile_button = QPushButton("Compile")
        self.compile_button.clicked.connect(self.compile_shader)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.tabs)
        left_layout.addWidget(self.compile_button)
        left_layout.addWidget(self.status_label)

        left_container = QWidget()
        left_container.setLayout(left_layout)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_container)
        splitter.addWidget(self.opengl_widget)
        splitter.setSizes([600, 600])

        main_layout = QHBoxLayout()
        main_layout.addWidget(splitter)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.create_menu_bar()


    def create_menu_bar(self):
        menu_bar = QMenuBar(self)
        file_menu = menu_bar.addMenu("File")

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_shader)
        load_action = QAction("Load", self)
        load_action.triggered.connect(self.load_shader)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)

        example_action = QAction("Load Blue Shader Example", self)
        example_action.triggered.connect(self.load_example_shader)

        raymarch_example_action = QAction("Load Ray Marching Shader Example", self)
        raymarch_example_action.triggered.connect(self.load_raymarch_shader)

        file_menu.addAction(save_action)
        file_menu.addAction(load_action)
        file_menu.addAction(example_action)
        file_menu.addAction(raymarch_example_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        self.setMenuBar(menu_bar)

    def compile_shader(self):
        if self.tabs.currentWidget() == self.code_editor:
            fragment_shader_code = self.code_editor.get_code()
            print(f"Compiling from Code Editor: {fragment_shader_code}")
            self.opengl_widget.compile_shaders(fragment_shader_code)
        elif self.tabs.currentWidget() == self.node_editor_widget:
            # Generate GLSL code from the node editor
            glsl_code = self.node_editor_widget.generate_glsl_code()
            print(f"Compiling from Node Editor: {glsl_code}")

            # Ensure the generated code is valid
            if glsl_code.strip():  # Check if the generated code is non-empty
                self.opengl_widget.compile_shaders(glsl_code)
            else:
                print("No valid GLSL code generated, skipping shader compilation.")

    def compile_selected_node_shader(self):
        selected_nodes = self.node_editor_widget.node_graph.selected_nodes()
        if selected_nodes:
            selected_node = selected_nodes[0]
            if isinstance(selected_node, TextureNode):
                texture_path = selected_node.get_property('texture')
                print(f"Texture path set: {texture_path}")
                self.opengl_widget.set_texture_path(texture_path)
            glsl_code = self.node_editor_widget.generate_glsl_code_for_node(selected_node)
            self.opengl_widget.compile_shaders(glsl_code)

    def on_shader_compiled(self, success, message):
        self.status_label.setText(message)
        if success:
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setStyleSheet("color: red;")

    def save_shader(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Shader", "", "GLSL Files (*.glsl);;All Files (*)", options=options)
        if file_path:
            with open(file_path, 'w') as file:
                if self.tabs.currentWidget() ==  self.code_editor:
                    file.write(self.code_editor.get_code())
                elif self.tabs.currentWidget() == self.node_editor_widget:
                    glsl_code = self.node_editor_widget.generate_glsl_code()
                    file.write(glsl_code)

    def load_shader(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Shader", "", "GLSL Files (*.glsl);;All Files (*)", options=options)
        if file_path:
            with open(file_path, 'r') as file:
                shader_code = file.read()
                if self.tabs.currentWidget() == self.code_editor:
                    self.code_editor.set_code(shader_code)
                elif self.tabs.currentWidget() == self.node_editor_widget:
                    self.node_editor_widget.scene.parse_shader_code(shader_code)

    def load_example_shader(self):
        example_fragment_shader_code = """#version 120
        varying vec2 TexCoords;
        uniform sampler2D texture1;
        void main() {
            gl_FragColor = vec4(0.0, 0.0, 1.0, 1.0);  // Blue color
        }
        """
        self.code_editor.set_code(example_fragment_shader_code)
        self.tabs.setCurrentWidget(self.code_editor)
        self.compile_shader()

    def load_raymarch_shader(self):
        raymarch_shader_code = """#version 120

#define MAX_STEPS 100
#define MAX_DISTANCE 100.0
#define SURFACE_DISTANCE 0.01

uniform vec2 resolution;
uniform float iTime;

float sdSphere(vec3 _p, vec3 _pos, float _r)
{
    vec4 sphere = vec4(_pos, _r);
    return length(_p - sphere.xyz) - sphere.w;
}

float sdPlane(vec3 _p, float _y)
{
    return _p.y - _y;
}

float GetDistance(vec3 _p)
{
    float plane = sdPlane(_p, 0.0);
    float sphere = sdSphere(_p, vec3(0.0, 1.0, 6.0), 1.0);

    // Return distance of closest scene object
    return min(sphere, plane);
}

float RayMarch(vec3 _rayOrigin, vec3 _rayDirection)
{
    float originDistance = 0.0;
    for (int i = 0; i < MAX_STEPS; i++)
    {
        // Marching point
        vec3 p = _rayOrigin + (originDistance * _rayDirection);

        // Calculate distance from current point (p) to scene object
        float sceneDistance = GetDistance(p);
        originDistance += sceneDistance;

        // Scene has been hit, or surpassed MAX_DISTANCE
        if (sceneDistance < SURFACE_DISTANCE || originDistance > MAX_DISTANCE)
        {
            break;
        }
    }
    return originDistance;
}

vec3 GetNormal(vec3 _p)
{
    // Distance from point _p to surface
    float surfaceDistance = GetDistance(_p);

    // Distance to sample surrounding points
    vec2 threshold = vec2(0.01, 0.0);

    // Sample points
    vec3 normal = surfaceDistance - vec3(GetDistance(_p - vec3(threshold.x, threshold.y, threshold.y)),
                                         GetDistance(_p - vec3(threshold.y, threshold.x, threshold.y)),
                                         GetDistance(_p - vec3(threshold.y, threshold.y, threshold.x)));

    return normalize(normal);
}

float GetLight(vec3 _p)
{
    // Define light
    vec3 lightPosition = vec3(0.0, 5.0, 6.0);
    lightPosition.xz += vec2(sin(iTime), cos(iTime)) * 2.0;
    vec3 lightVector = normalize(lightPosition - _p);

    // Calculate normal of intersection point
    vec3 normal = GetNormal(_p);

    // Clamp diffuse value from -1 to 1, -> 0 to 1
    float diffuse = clamp(dot(normal, lightVector), 0.0, 1.0);

    // Calculate distance between _p and light source
    float lightDistance = RayMarch(_p + (normal * SURFACE_DISTANCE * 2.0), lightVector);

    // Hit something
    if (lightDistance < length(lightPosition - _p))
    {
        diffuse *= 0.1;
    }

    return diffuse;
}

vec3 GetColor(vec3 _p)
{
    // Get basic color for each type of object
    float planeDistance = GetDistance(_p) - sdPlane(_p, 0.0);
    float sphereDistance = GetDistance(_p) - sdSphere(_p, vec3(0.0, 1.0, 6.0), 1.0);

    if (abs(planeDistance) < SURFACE_DISTANCE)
    {
        return vec3(0.6, 0.6, 0.6); // Light grey color for plane
    }
    else if (abs(sphereDistance) < SURFACE_DISTANCE)
    {
        return vec3(1.0, 0.2, 0.2); // Red color for sphere
    }

    return vec3(0.0); // Default black color
}

void main()
{
    // Normalize pixel coordinates (from -0.5 to 0.5), flip y
    vec2 uv = (gl_FragCoord.xy / resolution) * 2.0 - 1.0;
    uv.x *= resolution.x / resolution.y; // Adjust aspect ratio

    // Default black
    vec3 colour = vec3(0.0);

    // Camera setup
    vec3 rayOrigin = vec3(0.0, 1.0, 0.0);
    vec3 rayDirection = normalize(vec3(uv.x, uv.y, 1.0));

    // Fire rays, return distance to intersection
    float rayDistance = RayMarch(rayOrigin, rayDirection);

    // Get point of intersection
    vec3 p = rayOrigin + (rayDirection * rayDistance);

    // Calculate lighting and shading
    vec3 objectColor = GetColor(p);
    float diffuse = GetLight(p);
    colour = objectColor * diffuse;

    gl_FragColor = vec4(colour, 1.0);
}
"""
        self.code_editor.set_code(raymarch_shader_code)
        self.tabs.setCurrentWidget(self.code_editor)
        self.compile_shader()

    def update_code_editor(self, code):
        self.code_editor.set_code(code)
        self.opengl_widget.compile_shaders(code)
