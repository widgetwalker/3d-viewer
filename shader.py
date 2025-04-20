from OpenGL.GL import *
import OpenGL.GL.shaders as shaders
import numpy as np

class Shader:
    def __init__(self, vertex_path, fragment_path):
        self.program = None
        
        # Read vertex shader code
        with open(vertex_path, 'r') as f:
            vertex_src = f.read()
            
        # Read fragment shader code
        with open(fragment_path, 'r') as f:
            fragment_src = f.read()
            
        # Compile shaders
        vertex_shader = shaders.compileShader(vertex_src, GL_VERTEX_SHADER)
        fragment_shader = shaders.compileShader(fragment_src, GL_FRAGMENT_SHADER)
        
        # Create shader program
        self.program = shaders.compileProgram(vertex_shader, fragment_shader)
        
    def use(self):
        glUseProgram(self.program)
        
    def set_bool(self, name, value):
        glUniform1i(glGetUniformLocation(self.program, name), int(value))
        
    def set_int(self, name, value):
        glUniform1i(glGetUniformLocation(self.program, name), value)
        
    def set_float(self, name, value):
        glUniform1f(glGetUniformLocation(self.program, name), value)
        
    def set_vec2(self, name, value):
        glUniform2fv(glGetUniformLocation(self.program, name), 1, value)
        
    def set_vec3(self, name, value):
        glUniform3fv(glGetUniformLocation(self.program, name), 1, value)
        
    def set_vec4(self, name, value):
        glUniform4fv(glGetUniformLocation(self.program, name), 1, value)
        
    def set_mat4(self, name, value):
        glUniformMatrix4fv(glGetUniformLocation(self.program, name), 1, GL_FALSE, value)