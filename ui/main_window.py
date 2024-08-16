from PySide6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QMenuBar, QFileDialog, QSplitter, QPushButton
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from ui.opengl_widget import OpenGLWidget
from ui.code_editor import CodeEditor
from ui.node_editor import NodeEditorView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interactive Shader Editor")
        self.resize(1200, 800)

        self.opengl_widget = OpenGLWidget()

        self.node_editor_widget = NodeEditorView()
        self.node_editor_widget.node_selected.connect(self.update_code_editor)

        self.code_editor = CodeEditor()
        self.code_editor.editor.textChanged.connect(self.compile_shader)

        self.opengl_widget.shader_compiled.connect(self.on_shader_compiled)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.node_editor_widget, "Node Editor")
        self.tabs.addTab(self.code_editor, "Code Editor")

        self.status_label = QLabel("")

        self.compile_button = QPushButton("Compile")
        self.compile_button.clicked.connect(self.compile_selected_node_shader)

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

        example_action = QAction("Load Example Shader", self)
        example_action.triggered.connect(self.load_example_shader)

        file_menu.addAction(save_action)
        file_menu.addAction(load_action)
        file_menu.addAction(example_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        self.setMenuBar(menu_bar)

    def compile_shader(self):
        if self.tabs.currentWidget() == self.code_editor:
            fragment_shader_code = self.code_editor.get_code()
            self.opengl_widget.compile_shaders(fragment_shader_code)
        elif self.tabs.currentWidget() == self.node_editor_widget:
            glsl_code = self.node_editor_widget.generate_glsl_code()
            self.opengl_widget.compile_shaders(glsl_code)

    def compile_selected_node_shader(self):
        selected_nodes = self.node_editor_widget.node_graph.selected_nodes()
        if selected_nodes:
            selected_node = selected_nodes[0]
            if isinstance(selected_node, TextureNode):
                texture_path = selected_node.get_property('texture')
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
                if self.tabs.currentWidget() == self.code_editor:
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

    def update_code_editor(self, code):
        self.code_editor.set_code(code)
        self.opengl_widget.compile_shaders(code)
