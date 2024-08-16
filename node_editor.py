from NodeGraphQt.widgets.viewer import NodeViewer
from PySide6 import QtWidgets, QtGui, QtCore
from NodeGraphQt import NodeGraph
from ui.nodes.custom_nodes import MaterialNode, ColorNode, BlendNode, TextureNode, UVNode, GradientNode, AddNode
from PySide6.QtGui import QCursor, QKeyEvent
from ui.custom_viewer import CustomNodeViewer

class NodeEditorView(QtWidgets.QWidget):
    node_selected = QtCore.Signal(str)

    def __init__(self):
        super(NodeEditorView, self).__init__()
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)

        self.node_graph = NodeGraph(viewer=CustomNodeViewer())
        self.node_graph_widget = self.node_graph.widget
        layout.addWidget(self.node_graph_widget)

        self.node_graph_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.node_graph_widget.customContextMenuRequested.connect(self.open_context_menu)

        self.node_graph.node_double_clicked.connect(self.on_node_double_clicked)
        self.node_graph.node_selected.connect(self.on_node_selected)

        self.selected_node = None

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace):
            self.delete_selected_node()
        else:
            super(NodeEditorView, self).keyPressEvent(event)

    def open_context_menu(self, position):
        menu = QtWidgets.QMenu(self)
        pos = QCursor.pos()

        add_material_action = menu.addAction("Add Material Node")
        add_color_action = menu.addAction("Add Color Node")
        add_blend_action = menu.addAction("Add Blend Node")
        add_texture_action = menu.addAction("Add Texture Node")
        add_uv_action = menu.addAction("Add UV Node")
        add_gradient_action = menu.addAction("Add Gradient Node")
        add_add_action = menu.addAction("Add Add Node")

        action = menu.exec_(self.node_graph_widget.mapToGlobal(position))

        if action == add_material_action:
            self.add_node(MaterialNode, "Material Node", position)
        elif action == add_color_action:
            self.add_node(ColorNode, "Color Node", position)
        elif action == add_blend_action:
            self.add_node(BlendNode, "Blend Node", position)
        elif action == add_texture_action:
            self.add_node(TextureNode, "Texture Node", position)
        elif action == add_uv_action:
            self.add_node(UVNode, "UV Node", position)
        elif action == add_gradient_action:
            self.add_node(GradientNode, "Gradient Node", position)
        elif action == add_add_action:
            self.add_node(AddNode, "Add Node", position)

    def add_node(self, node_class, name, pos, **kwargs):
        node = node_class()
        node.set_name(name)
        self.node_graph.add_node(node)
        node.set_pos(pos.x(), pos.y())
        self.update_code_editor()
        return node

    def delete_selected_node(self):
        if self.selected_node:
            self.node_graph.remove_node(self.selected_node)
            self.selected_node = None
            self.update_code_editor()
        else:
            QtWidgets.QMessageBox.warning(self, "No Node Selected", "Please select a node to delete.")

    def generate_glsl_code(self):
        generated_code = []
        used_vars = set()
        final_output_var = None

        for node in self.node_graph.all_nodes():
            if hasattr(node, 'generate_glsl'):
                var_name = node.generate_glsl(generated_code, used_vars)
                final_output_var = var_name

        # Construct the final GLSL code
        if final_output_var:
            # Ensure the final output variable is a vec3 before using it in a vec4 context
            final_code = f"""#version 120
    {self.format_glsl_code(generated_code)}

    void main() {{
        vec3 color = {final_output_var}.rgb;  // Ensure it's a vec3
        gl_FragColor = vec4(color, 1.0);  // Convert to vec4 with alpha 1.0
    }}
    """
        else:
            final_code = """#version 120
    void main() {
        gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);  // Default to black if no output
    }
    """

        # Output for debugging purposes
        print(f"Generated GLSL code:\n{final_code}")
        return final_code

    def format_glsl_code(self, code_lines):
        formatted_code = ""
        indent = "    "
        for line in code_lines:
            if line.strip().startswith("//"):
                formatted_code += f"{line}\n"
            else:
                formatted_code += f"{indent}{line}\n"
        return formatted_code

    def on_node_double_clicked(self, node):
        self.selected_node = node
        self.update_code_editor(node)

    def on_node_selected(self, node):
        self.selected_node = node
        self.update_code_editor(node)

    def update_code_editor(self, selected_node=None):
        if selected_node and isinstance(selected_node, (GradientNode, UVNode)):
            return

        if selected_node:
            glsl_code = self.generate_glsl_code_for_node(selected_node)
        else:
            glsl_code = self.generate_glsl_code()
        self.node_selected.emit(glsl_code)

    def generate_glsl_code_for_node(self, node):
        generated_code = []
        used_vars = set()

        if hasattr(node, 'generate_glsl'):
            var_name = node.generate_glsl(generated_code, used_vars)
            final_output_var = var_name

        final_code = f"""
    #version 120
    {self.format_glsl_code(generated_code)}

    void main() {{
        gl_FragColor = vec4(vec3({final_output_var}), 1.0);
    }}
    """
        print(f"Generated GLSL code for node:\n{final_code}")
        return final_code
