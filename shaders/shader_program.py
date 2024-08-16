# shader_program.py
from OpenGL.GL import *

class ShaderProgram:
    def __init__(self, vertex_shader_source, fragment_shader_source):
        self.vertex_shader_source = vertex_shader_source
        self.fragment_shader_source = fragment_shader_source
        self.program = None
        self.compile(self.vertex_shader_source, self.fragment_shader_source)

    def compile(self, vertex_shader_source, fragment_shader_source):
        if self.program:
            glDeleteProgram(self.program)
        self.program = glCreateProgram()
        vertex_shader = self.compile_shader(GL_VERTEX_SHADER, vertex_shader_source)
        fragment_shader = self.compile_shader(GL_FRAGMENT_SHADER, fragment_shader_source)
        glAttachShader(self.program, vertex_shader)
        glAttachShader(self.program, fragment_shader)
        glBindAttribLocation(self.program, 0, "position")
        glBindAttribLocation(self.program, 1, "texCoord")
        glLinkProgram(self.program)
        if not glGetProgramiv(self.program, GL_LINK_STATUS):
            log = glGetProgramInfoLog(self.program)
            print("Shader linking failed:", log)
            raise RuntimeError('Shader linking failed: ' + log.decode('utf-8'))

    def compile_shader(self, shader_type, source):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            log = glGetShaderInfoLog(shader)
            print("Shader compilation failed:", log)
            raise RuntimeError('Shader compilation failed: ' + log.decode('utf-8'))
        return shader

    def use(self):
        if self.program:
            glUseProgram(self.program)
        else:
            print("Shader program is not compiled properly.")
