import numpy as np
import pywavefront
from OpenGL.GL import *
from PIL import Image

class Model:
    def __init__(self, file_path):
        self.VAO = 0
        self.VBO = 0
        self.EBO = 0
        self.texture = 0
        self.num_vertices = 0
        self.num_indices = 0
        self.has_texture = False
        
        # Load the model
        self.load_model(file_path)
        
    def load_model(self, file_path):
        # Load OBJ file using PyWavefront
        scene = pywavefront.Wavefront(file_path, collect_faces=True, parse=True)
        
        # Extract vertices, normals, and texture coordinates
        vertices = []
        indices = []
        
        # Track unique vertices to build index buffer
        unique_vertices = {}
        index_count = 0
        
        # Process all meshes
        for name, material in scene.materials.items():
            for i, face in enumerate(material.faces):
                for vertex_i in face:
                    # Get vertex attributes
                    vertex = scene.vertices[vertex_i]
                    
                    # Default values for normal and texture coordinates
                    normal = [0.0, 0.0, 1.0]
                    tex_coord = [0.0, 0.0]
                    
                    # Extract position (always present)
                    position = vertex[0:3]
                    
                    # Check if normals are present
                    if len(vertex) >= 6:
                        normal = vertex[3:6]
                    
                    # Check if texture coordinates are present
                    if len(vertex) >= 8:
                        tex_coord = vertex[6:8]
                    
                    # Create a unique key for this vertex
                    vertex_key = tuple(position + normal + tex_coord)
                    
                    # Check if we've seen this vertex before
                    if vertex_key in unique_vertices:
                        # Reuse existing vertex
                        indices.append(unique_vertices[vertex_key])
                    else:
                        # Add new vertex
                        vertices.extend(position + normal + tex_coord)
                        unique_vertices[vertex_key] = index_count
                        indices.append(index_count)
                        index_count += 1
        
        # Convert to numpy arrays
        vertices = np.array(vertices, dtype=np.float32)
        indices = np.array(indices, dtype=np.uint32)
        
        self.num_vertices = len(vertices) // 8  # position (3) + normal (3) + texcoord (2)
        self.num_indices = len(indices)
        
        # Create VAO
        self.VAO = glGenVertexArrays(1)
        glBindVertexArray(self.VAO)
        
        # Create VBO
        self.VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        
        # Create EBO
        self.EBO = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
        
        # Set vertex attribute pointers
        # Position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(0))
        
        # Normal
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(3 * 4))
        
        # Texture coordinates
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(6 * 4))
        
        # Unbind VAO
        glBindVertexArray(0)
        
        # Check for texture files with the same name
        texture_path = file_path.rsplit('.', 1)[0] + '.png'
        try:
            self.load_texture(texture_path)
            self.has_texture = True
        except:
            # Try jpg if png fails
            try:
                texture_path = file_path.rsplit('.', 1)[0] + '.jpg'
                self.load_texture(texture_path)
                self.has_texture = True
            except:
                print(f"No texture found for {file_path}")
                self.has_texture = False
    
    def load_texture(self, texture_path):
        # Load texture using PIL
        image = Image.open(texture_path)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = np.array(list(image.getdata()), np.uint8)
        
        # Create texture
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        
        # Set texture parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        # Upload texture data
        if image.mode == 'RGB':
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
        elif image.mode == 'RGBA':
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        
        # Generate mipmaps
        glGenerateMipmap(GL_TEXTURE_2D)
        
        # Clean up
        glBindTexture(GL_TEXTURE_2D, 0)
    
    def draw(self, shader):
        # Bind texture if available
        if self.has_texture:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            shader.set_int("texture1", 0)
            shader.set_int("useTexture", 1)
        else:
            shader.set_int("useTexture", 0)
        
        # Draw mesh
        glBindVertexArray(self.VAO)
        glDrawElements(GL_TRIANGLES, self.num_indices, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        
        # Unbind texture
        glBindTexture(GL_TEXTURE_2D, 0)