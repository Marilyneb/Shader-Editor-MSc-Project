import numpy as np
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtCore import Signal
from OpenGL.GL import *
from shaders.shader_program import ShaderProgram
import time

class OpenGLWidget(QOpenGLWidget):
    shader_compiled = Signal(bool, str)

    def __init__(self):
        super().__init__()
        self.start_time = time.time()
        fmt = QSurfaceFormat()
        fmt.setVersion(2, 1)
        fmt.setProfile(QSurfaceFormat.CoreProfile)
        QSurfaceFormat.setDefaultFormat(fmt)
        self.shader_program = None
        self.texture = None
        self.vbo = None
        self.ebo = None
        self.texture_path = None
        self.is_3d = False
        self.cameraPos = np.array([0.0, 0.0, 5.0], dtype=np.float32)
        self.lightPos = np.array([5.0, 5.0, 5.0], dtype=np.float32)
        self.boilerplate_vertex = """
        #version 120
        attribute vec3 position;
        attribute vec2 texCoord;
        varying vec2 TexCoords;
        void main() {
            gl_Position = vec4(position, 1.0);
            TexCoords = texCoord;
        }
        """
        self.boilerplate_fragment = """
        #version 120
        varying vec2 TexCoords;
        uniform sampler2D texture1;
        void main() {
            gl_FragColor = texture2D(texture1, TexCoords);
        }
        """

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        self.shader_program = ShaderProgram(self.boilerplate_vertex, self.boilerplate_fragment)
        self.initialize_geometry()
        self.initialize_texture()
        self.update_uniforms()

    def compile_shaders(self, shader_source, is_3d=False):
        self.is_3d = is_3d
        shader_source = self.clean_shader_code(shader_source)
        print("Compiling shader with source:\n", shader_source)  # Debugging print
        try:
            self.shader_program.compile(self.boilerplate_vertex, shader_source)
            self.shader_program.use()
            self.update_uniforms()  # Update uniforms like resolution and time
            self.shader_compiled.emit(True, "Shader compiled successfully.")
            self.update()  # Trigger the OpenGL widget to repaint
            return True, "Shader compiled successfully."
        except RuntimeError as e:
            self.shader_compiled.emit(False, str(e))
            return False, str(e)



    def initialize_geometry(self):
        vertices = np.array([
            -1.0, -1.0, 0.0,  0.0, 0.0,
             1.0, -1.0, 0.0,  1.0, 0.0,
             1.0,  1.0, 0.0,  1.0, 1.0,
            -1.0,  1.0, 0.0,  0.0, 1.0
        ], dtype=np.float32)
        indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    def initialize_texture(self):
        if self.texture_path:
            self.texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.texture)

            image = QImage(self.texture_path)
            image = image.convertToFormat(QImage.Format_RGBA8888)
            width = image.width()
            height = image.height()
            image_data = image.bits().tobytes()

            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glBindTexture(GL_TEXTURE_2D, 0)
        else:
            self.texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            white_texture = np.array([255, 255, 255, 255], dtype=np.uint8)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 1, 1, 0, GL_RGBA, GL_UNSIGNED_BYTE, white_texture)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glBindTexture(GL_TEXTURE_2D, 0)

    def set_texture_path(self, path):
        self.texture_path = path
        self.initialize_texture()
        self.update()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.shader_program.use()

        if self.texture:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            texture_location = glGetUniformLocation(self.shader_program.program, "texture_sampler_4303718352")
            glUniform1i(texture_location, 0)  # Bind the uniform to texture unit 0

        self.update_uniforms()

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)

        position_location = glGetAttribLocation(self.shader_program.program, "position")
        texCoord_location = glGetAttribLocation(self.shader_program.program, "texCoord")

        glEnableVertexAttribArray(position_location)
        glVertexAttribPointer(position_location, 3, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(0))

        glEnableVertexAttribArray(texCoord_location)
        glVertexAttribPointer(texCoord_location, 2, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(3 * 4))

        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

        glDisableVertexAttribArray(position_location)
        glDisableVertexAttribArray(texCoord_location)
        glBindTexture(GL_TEXTURE_2D, 0)


    def clean_shader_code(self, shader_source):
        shader_source = shader_source.strip()

        if not shader_source.startswith("#version"):
            shader_source = "#version 120\n" + shader_source

        lines = shader_source.split('\n')
        cleaned_lines = [lines[0]]

        for line in lines[1:]:
            if not line.strip().startswith("#version"):
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def update_uniforms(self):
        self.shader_program.use()
        resolution_location = glGetUniformLocation(self.shader_program.program, "resolution")
        if resolution_location != -1:
            glUniform2f(resolution_location, self.width(), self.height())

        time_location = glGetUniformLocation(self.shader_program.program, "iTime")
        if time_location != -1:
            glUniform1f(time_location, time.time() - self.start_time)

        lightPosLoc = glGetUniformLocation(self.shader_program.program, "lightPos")
        cameraPosLoc = glGetUniformLocation(self.shader_program.program, "cameraPos")

        if lightPosLoc != -1:
            glUniform3fv(lightPosLoc, 1, self.lightPos)
        if cameraPosLoc != -1:
            glUniform3fv(cameraPosLoc, 1, self.cameraPos)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        self.update_uniforms()
