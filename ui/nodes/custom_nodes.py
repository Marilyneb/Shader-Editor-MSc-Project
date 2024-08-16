from NodeGraphQt import BaseNode, NodeBaseWidget
from PySide6.QtWidgets import QPushButton, QWidget, QColorDialog, QComboBox, QVBoxLayout, QLabel, QSlider, QDoubleSpinBox, QFileDialog, QHBoxLayout
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, Signal


class ColorButtonWidget(NodeBaseWidget):
    def __init__(self, parent=None, name='', label=''):
        super(ColorButtonWidget, self).__init__(parent)
        self._name = name
        self._color_button = QPushButton('Pick Color')
        self._color_button.setStyleSheet('background-color: rgb(128, 128, 128)')
        self._color_button.clicked.connect(self.open_color_picker)
        self._color = (128 / 255.0, 128 / 255.0, 128 / 255.0)

        layout = QVBoxLayout()
        if label:
            layout.addWidget(QLabel(label))
        layout.addWidget(self._color_button)
        container = QWidget()
        container.setLayout(layout)
        self.set_custom_widget(container)

    def open_color_picker(self):
        initial_color = QColor(self._color[0] * 255, self._color[1] * 255, self._color[2] * 255)
        color = QColorDialog.getColor(initial_color)
        if color.isValid():
            r, g, b = color.red(), color.green(), color.blue()
            self._color = (r / 255.0, g / 255.0, b / 255.0)
            self._color_button.setStyleSheet(f'background-color: rgb({r}, {g}, {b})')
            self.value_changed.emit(self._name, self._color)

    def get_value(self):
        return self._color

    def set_value(self, color):
        self._color = color
        r, g, b = int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)
        self._color_button.setStyleSheet(f'background-color: rgb({r}, {g}, {b})')

    def get_name(self):
        return self._name


class ShadingModelWidget(NodeBaseWidget):
    def __init__(self, parent=None, name='', label=''):
        super(ShadingModelWidget, self).__init__(parent)
        self._name = name
        self._combo_box = QComboBox()
        self._combo_box.addItems(['Lambert', 'Phong'])
        self._combo_box.currentTextChanged.connect(self._on_value_changed)

        # Apply stylesheet for better visibility
        self._combo_box.setStyleSheet("""
            QComboBox {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #444444;
                padding: 15px;
                border-radius: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: #2b2b2b;
                selection-background-color: #444444;
                color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)

        layout = QVBoxLayout()
        if label:
            layout.addWidget(QLabel(label))
        layout.addWidget(self._combo_box)
        container = QWidget()
        container.setLayout(layout)
        self.set_custom_widget(container)

    def _on_value_changed(self):
        self.value_changed.emit(self._name, self.get_value())

    def get_value(self):
        return self._combo_box.currentText()

    def set_value(self, value):
        self._combo_box.setCurrentText(value)

    def get_name(self):
        return self._name


class DoubleSpinBoxWidget(NodeBaseWidget):
    def __init__(self, parent=None, name='', label='', value=0.0, min_val=0.0, max_val=100.0):
        super(DoubleSpinBoxWidget, self).__init__(parent)
        self._name = name
        self._spin_box = QDoubleSpinBox()
        self._spin_box.setRange(min_val, max_val)
        self._spin_box.setValue(value)
        self._spin_box.valueChanged.connect(self._on_value_changed)

        layout = QVBoxLayout()
        if label:
            layout.addWidget(QLabel(label))
        layout.addWidget(self._spin_box)
        container = QWidget()
        container.setLayout(layout)
        self.set_custom_widget(container)

    def _on_value_changed(self):
        self.value_changed.emit(self._name, self.get_value())

    def get_value(self):
        return self._spin_box.value()

    def set_value(self, value):
        self._spin_box.setValue(value)

    def get_name(self):
        return self._name


class SliderWidget(NodeBaseWidget):
    def __init__(self, parent=None, name='', label='', min_val=0, max_val=100, default_val=50):
        super(SliderWidget, self).__init__(parent)
        self._name = name
        self._slider = QSlider(Qt.Horizontal)
        self._slider.setMinimum(min_val)
        self._slider.setMaximum(max_val)
        self._slider.setValue(default_val)
        self._slider.valueChanged.connect(self._on_value_changed)

        layout = QVBoxLayout()
        if label:
            layout.addWidget(QLabel(label))
        layout.addWidget(self._slider)
        container = QWidget()
        container.setLayout(layout)
        self.set_custom_widget(container)

    def _on_value_changed(self, value):
        self.value_changed.emit(self._name, self.get_value())

    def get_value(self):
        return self._slider.value() / 100.0

    def set_value(self, value):
        self._slider.setValue(int(value * 100))

    def get_name(self):
        return self._name


class MaterialNode(BaseNode):
    __identifier__ = 'nodes'
    NODE_NAME = 'Material'

    def __init__(self):
        super(MaterialNode, self).__init__()
        self.add_input('Color')
        self.add_output('Output')

        self.shading_model_widget = ShadingModelWidget(self.view, 'shading_model', 'Shading Model')
        self.shading_model_widget.value_changed.connect(self._on_property_changed)
        self.add_custom_widget(self.shading_model_widget, 'shading_model', 'Shading Model')

        self.base_color_widget = ColorButtonWidget(self.view, 'node_color', 'Base Color')
        self.base_color_widget.value_changed.connect(self._on_property_changed)
        self.add_custom_widget(self.base_color_widget, 'node_color', 'Base Color')

        self.specular_color_widget = ColorButtonWidget(self.view, 'specular_color', 'Specular Color')
        self.specular_color_widget.value_changed.connect(self._on_property_changed)
        self.add_custom_widget(self.specular_color_widget, 'specular_color', 'Specular Color')

        self.specular_intensity_widget = DoubleSpinBoxWidget(self.view, 'specular_intensity', 'Specular Intensity', value=1.0, min_val=0.0, max_val=10.0)
        self.specular_intensity_widget.value_changed.connect(self._on_property_changed)
        self.add_custom_widget(self.specular_intensity_widget, 'specular_intensity', 'Specular Intensity')

        self.shininess_widget = DoubleSpinBoxWidget(self.view, 'shininess', 'Shininess', value=32.0, min_val=1.0, max_val=128.0)
        self.shininess_widget.value_changed.connect(self._on_property_changed)
        self.add_custom_widget(self.shininess_widget, 'shininess', 'Shininess')

        self.set_node_color(255, 150, 150)

    def generate_glsl(self, generated_code, used_vars):
        node_id = id(self)
        shading_model = self.get_property('shading_model')
        color_var = self.get_input_var_name('Color', generated_code, used_vars)
        var_name = f"material_{node_id}"
        if var_name in used_vars:
            return var_name
        used_vars.add(var_name)

        spec_color = self.get_property('specular_color')
        spec_intensity = self.get_property('specular_intensity')
        shininess = self.get_property('shininess')

        generated_code.append(f"// Begin Material Node {node_id} ({self.NODE_NAME})")
        if shading_model == 'Lambert':
            generated_code.append(f"""
    vec3 lightDir = normalize(vec3(0.0, 0.0, 1.0)); // Light coming straight down
    vec3 normal = normalize(vec3(0.0, 0.0, 1.0)); // Surface normal
    vec4 {var_name} = vec4({color_var}.rgb * max(dot(normal, lightDir), 0.0), 1.0);
    """)
        elif shading_model == 'Phong':
            generated_code.append(f"""
    vec3 normal = normalize(vec3(0.0, 0.0, 1.0)); // Surface normal
    vec3 lightDir = normalize(vec3(0.0, 0.0, 1.0)); // Light coming straight down
    vec3 viewDir = normalize(vec3(0.0, 0.0, 1.0)); // View direction
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = {spec_intensity} * pow(max(dot(viewDir, reflectDir), {shininess}), 32.0);
    vec4 {var_name} = vec4({color_var}.rgb * max(dot(normal, lightDir), 0.0) + vec3({spec_color[0]}, {spec_color[1]}, {spec_color[2]}) * spec, 1.0);
    """)
        return var_name

    def get_input_var_name(self, input_name, generated_code, used_vars):
        input_port = self.get_input(input_name)
        if input_port and input_port.connected_ports():
            connected_port = input_port.connected_ports()[0]
            connected_node = connected_port.node()
            if hasattr(connected_node, 'generate_glsl'):
                var_name = connected_node.generate_glsl(generated_code, used_vars)
                return var_name
        # Use the node's base color if no connection is found
        base_color = self.get_property('node_color')
        var_name = f"base_color_{id(self)}"
        generated_code.append(f"vec3 {var_name} = vec3({base_color[0]}, {base_color[1]}, {base_color[2]});")
        return var_name

    def set_node_color(self, r, g, b):
        self.base_color_widget.set_value((r / 255.0, g / 255.0, b / 255.0))

    def _on_property_changed(self, name, value):
        self.set_property(name, value)
        self.update()
        self.graph.node_double_clicked.emit(self)

class ColorNode(BaseNode):
    __identifier__ = 'nodes'
    NODE_NAME = 'Color'

    def __init__(self):
        super(ColorNode, self).__init__()
        self.add_output('Color')

        self.color_button_widget = ColorButtonWidget(self.view, 'node_color', 'Pick Color')
        self.color_button_widget.value_changed.connect(self._on_color_changed)
        self.add_custom_widget(self.color_button_widget, 'node_color', 'Pick Color')

        self.set_node_color(150, 255, 150)

    def generate_glsl(self, generated_code, used_vars):
        node_id = id(self)
        color = self.get_property('node_color')
        var_name = f"color_{node_id}"
        if var_name in used_vars:
            return var_name
        used_vars.add(var_name)
        generated_code.append(f"// Begin Color Node {node_id} ({self.NODE_NAME})")
        generated_code.append(f"vec4 {var_name} = vec4({color[0]}, {color[1]}, {color[2]}, 1.0);")
        generated_code.append(f"// End Color Node {node_id} ({self.NODE_NAME})")
        return var_name

    def set_node_color(self, r, g, b):
        color = (r / 255.0, g / 255.0, b / 255.0)
        self.color_button_widget.set_value(color)

    def _on_color_changed(self, name, value):
        self.set_property(name, value)
        self.update()
        self.graph.node_double_clicked.emit(self)



class BlendModeWidget(NodeBaseWidget):
    def __init__(self, parent=None, name='', label=''):
        super(BlendModeWidget, self).__init__(parent)
        self._name = name
        self._combo_box = QComboBox()
        self._combo_box.addItems(['Multiply', 'Screen', 'Overlay'])
        self._combo_box.currentTextChanged.connect(self._on_value_changed)
        self._combo_box.setStyleSheet("""
            QComboBox {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #444444;
                padding: 5px;
                border-radius: 5px;
                min-width: 100px; /* Minimum width for better visibility */
            }
            QComboBox QAbstractItemView {
                background-color: #2b2b2b;
                selection-background-color: #444444;
                color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(noimg);
                width: 0;
                height: 0;
            }
            QComboBox::down-arrow:pressed, QComboBox::down-arrow:hover {
                image: url(noimg);
                width: 0;
                height: 0;
            }
            QComboBox::item {
                height: 25px; /* Increase height for better visibility */
            }
        """)

        layout = QVBoxLayout()
        if label:
            layout.addWidget(QLabel(label))
        layout.addWidget(self._combo_box)
        container = QWidget()
        container.setLayout(layout)
        self.set_custom_widget(container)

    def _on_value_changed(self):
        self.value_changed.emit(self._name, self.get_value())

    def get_value(self):
        return self._combo_box.currentText()

    def set_value(self, value):
        self._combo_box.setCurrentText(value)

    def get_name(self):
        return self._name


class BlendNode(BaseNode):
    __identifier__ = 'nodes'
    NODE_NAME = 'Blend'

    def __init__(self):
        super(BlendNode, self).__init__()
        self.add_input('Color A')
        self.add_input('Color B')
        self.add_output('Output')

        self.blend_mode_widget = BlendModeWidget(self.view, 'blend_mode', 'Blend Mode')
        self.blend_mode_widget.value_changed.connect(self._on_property_changed)
        self.add_custom_widget(self.blend_mode_widget, 'blend_mode', 'Blend Mode')

    def generate_glsl(self, generated_code, used_vars):
        node_id = id(self)
        color_a_var = self.get_input_var_name('Color A', generated_code, used_vars)
        color_b_var = self.get_input_var_name('Color B', generated_code, used_vars)
        var_name = f"blend_{node_id}"
        if var_name in used_vars:
            return var_name
        used_vars.add(var_name)

        blend_mode = self.get_property('blend_mode')
        generated_code.append(f"// Begin Blend Node {node_id} ({self.NODE_NAME})")

        if blend_mode == 'Multiply':
            generated_code.append(f"vec4 {var_name} = vec4({color_a_var}.rgb * {color_b_var}.rgb, 1.0);")
        elif blend_mode == 'Screen':
            generated_code.append(f"vec4 {var_name} = vec4(1.0 - (1.0 - {color_a_var}.rgb) * (1.0 - {color_b_var}.rgb), 1.0);")
        elif blend_mode == 'Overlay':
            generated_code.append(f"vec4 {var_name} = vec4("
                        f"({color_a_var}.r < 0.5) ? (2.0 * {color_a_var}.r * {color_b_var}.r) : (1.0 - 2.0 * (1.0 - {color_a_var}.r) * (1.0 - {color_b_var}.r)), "
                        f"({color_a_var}.g < 0.5) ? (2.0 * {color_a_var}.g * {color_b_var}.g) : (1.0 - 2.0 * (1.0 - {color_a_var}.g) * (1.0 - {color_b_var}.g)), "
                        f"({color_a_var}.b < 0.5) ? (2.0 * {color_a_var}.b * {color_b_var}.b) : (1.0 - 2.0 * (1.0 - {color_a_var}.b) * (1.0 - {color_b_var}.b)), 1.0);")
        return var_name

    def get_input_var_name(self, input_name, generated_code, used_vars):
        input_port = self.get_input(input_name)
        if input_port and input_port.connected_ports():
            connected_port = input_port.connected_ports()[0]
            connected_node = connected_port.node()
            if hasattr(connected_node, 'generate_glsl'):
                var_name = connected_node.generate_glsl(generated_code, used_vars)
                return var_name
        return "vec3(1.0)"  # Default to white if no input

    def _on_property_changed(self, name, value):
        self.set_property(name, value)
        self.update()
        self.graph.node_double_clicked.emit(self)

class TextureWidget(NodeBaseWidget):
    value_changed = Signal(str, str)

    def __init__(self, parent=None, name='', label=''):
        super(TextureWidget, self).__init__(parent)
        self._name = name
        self._texture_button = QPushButton('Select Texture')
        self._texture_button.clicked.connect(self.open_texture_dialog)
        self._texture_path = ""

        layout = QVBoxLayout()
        if label:
            layout.addWidget(QLabel(label))
        layout.addWidget(self._texture_button)
        container = QWidget()
        container.setLayout(layout)
        self.set_custom_widget(container)

    def open_texture_dialog(self):
        file_dialog = QFileDialog()
        texture_path, _ = file_dialog.getOpenFileName(caption='Select Texture', filter='Image Files (*.png *.jpg *.bmp)')
        if texture_path:
            self._texture_path = texture_path
            self._texture_button.setText(texture_path.split('/')[-1])
            self.value_changed.emit(self._name, self._texture_path)

    def generate_glsl(self, generated_code, used_vars):
        node_id = id(self)
        uv_var = self.get_input_var_name('UV', generated_code, used_vars) or 'vec2(0.0, 0.0)'
        var_name = f"texture_{node_id}"
        if var_name in used_vars:
            return var_name
        used_vars.add(var_name)

        texture_uniform_name = f"texture_sampler_{node_id}"
        generated_code.append(f"// Begin Texture Node {node_id} ({self.NODE_NAME})")
        generated_code.append(f"uniform sampler2D {texture_uniform_name};")
        generated_code.append(f"vec4 {var_name} = texture2D({texture_uniform_name}, {uv_var});")
        generated_code.append(f"// End Texture Node {node_id} ({self.NODE_NAME})")
        return var_name

    def get_value(self):
        return self._texture_path

    def set_value(self, value):
        self._texture_path = value
        self._texture_button.setText(value.split('/')[-1])

    def get_name(self):
        return self._name

class TextureNode(BaseNode):
    __identifier__ = 'nodes'
    NODE_NAME = 'Texture'

    def __init__(self):
        super(TextureNode, self).__init__()
        self.add_input('UV')
        self.add_output('Color')

        self.texture_widget = TextureWidget(self.view, 'texture', 'Texture')
        self.texture_widget.value_changed.connect(self._on_property_changed)
        self.add_custom_widget(self.texture_widget, 'texture', 'Texture')

    def generate_glsl(self, generated_code, used_vars):
        node_id = id(self)
        uv_var = self.get_input_var_name('UV', generated_code, used_vars)
        var_name = f"texture_{node_id}"
        if var_name in used_vars:
            return var_name
        used_vars.add(var_name)

        texture_uniform_name = f"texture_sampler_{node_id}"
        generated_code.append(f"// Begin Texture Node {node_id} ({self.NODE_NAME})")
        generated_code.append(f"uniform sampler2D {texture_uniform_name};")
        generated_code.append(f"vec4 {var_name} = texture2D({texture_uniform_name}, {uv_var});")
        generated_code.append(f"// End Texture Node {node_id} ({self.NODE_NAME})")
        return var_name

    def _on_property_changed(self, name, value):
        self.set_property(name, value)
        self.update()
        self.graph.node_double_clicked.emit(self)

    def get_input_var_name(self, input_name, generated_code, used_vars):
        input_port = self.get_input(input_name)
        if input_port and input_port.connected_ports():
            connected_port = input_port.connected_ports()[0]
            connected_node = connected_port.node()
            if hasattr(connected_node, 'generate_glsl'):
                var_name = connected_node.generate_glsl(generated_code, used_vars)
                return var_name
        var_name = "default_uv"
        if var_name not in used_vars:
            generated_code.append(f"vec2 {var_name} = vec2(0.0, 0.0);")
        return var_name


class UVNode(BaseNode):
    __identifier__ = 'nodes'
    NODE_NAME = 'UV'

    def __init__(self):
        super(UVNode, self).__init__()
        self.add_output('UV')

    def generate_glsl(self, generated_code, used_vars):
        node_id = id(self)
        var_name = f"uv_{node_id}"
        if var_name in used_vars:
            return var_name
        used_vars.add(var_name)

        generated_code.append(f"// Begin UV Node {node_id} ({self.NODE_NAME})")
        generated_code.append(f"uniform vec2 resolution;")
        generated_code.append(f"vec2 {var_name} = gl_FragCoord.xy / resolution;")
        generated_code.append(f"// End UV Node {node_id} ({self.NODE_NAME})")
        return var_name


class GradientNode(BaseNode):
    __identifier__ = 'nodes'
    NODE_NAME = 'Gradient'

    def __init__(self):
        super(GradientNode, self).__init__()
        self.add_input('UV')
        self.add_output('Color')

        # Initial gradient values (example)
        self.gradient = [255, 128, 64, 128, 255]

    def generate_glsl(self, generated_code, used_vars):
        node_id = id(self)
        uv_var = self.get_input_var_name('UV', generated_code, used_vars)
        var_name = f"gradient_{node_id}"
        if var_name in used_vars:
            return var_name
        used_vars.add(var_name)

        generated_code.append(f"// Begin Gradient Node {node_id} ({self.NODE_NAME})")
        generated_code.append(f"vec3 {var_name} = mix(vec3(1.0, 0.0, 0.0), vec3(0.0, 0.0, 1.0), {uv_var}.y);")
        generated_code.append(f"// End Gradient Node {node_id} ({self.NODE_NAME})")
        return var_name

    def get_input_var_name(self, input_name, generated_code, used_vars):
        input_port = self.get_input(input_name)
        if input_port and input_port.connected_ports():
            connected_port = input_port.connected_ports()[0]
            connected_node = connected_port.node()
            if hasattr(connected_node, 'generate_glsl'):
                var_name = connected_node.generate_glsl(generated_code, used_vars)
                return var_name
        var_name = "default_uv"
        if var_name not in used_vars:
            generated_code.append(f"vec2 {var_name} = vec2(0.0, 0.0);")
        return var_name

    def _on_gradient_changed(self, gradient):
        self.gradient = gradient
        self.update()
        self.graph.node_double_clicked.emit(self)

class AddNode(BaseNode):
    __identifier__ = 'nodes'
    NODE_NAME = 'Add'

    def __init__(self):
        super(AddNode, self).__init__()
        self.add_input('A')
        self.add_input('B')
        self.add_output('Output')

    def generate_glsl(self, generated_code, used_vars):
        node_id = id(self)
        input_a = self.get_input_var_name('A', generated_code, used_vars)
        input_b = self.get_input_var_name('B', generated_code, used_vars)
        var_name = f"add_{node_id}"
        if var_name in used_vars:
            return var_name
        used_vars.add(var_name)

        generated_code.append(f"// Begin Add Node {node_id} ({self.NODE_NAME})")
        generated_code.append(f"vec4 {var_name} = {input_a} + {input_b};")
        generated_code.append(f"// End Add Node {node_id} ({self.NODE_NAME})")
        return var_name

    def get_input_var_name(self, input_name, generated_code, used_vars):
        input_port = self.get_input(input_name)
        if input_port and input_port.connected_ports():
            connected_port = input_port.connected_ports()[0]
            connected_node = connected_port.node()
            if hasattr(connected_node, 'generate_glsl'):
                var_name = connected_node.generate_glsl(generated_code, used_vars)
                return var_name
        # Default value if no input is connected
        var_name = f"default_{input_name}_{id(self)}"
        if var_name not in used_vars:
            generated_code.append(f"vec4 {var_name} = vec4(0.0, 0.0, 0.0, 1.0);")
            used_vars.add(var_name)
        return var_name
