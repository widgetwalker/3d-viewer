import numpy as np
import glfw
import math
from pyrr import matrix44, Vector3

class Camera:
    def __init__(self, window, position=None, target=None):
        self.window = window
        
        # Default camera position and target
        self.position = position if position is not None else np.array([0.0, 0.0, 5.0], dtype=np.float32)
        self.target = target if target is not None else np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        
        # Camera parameters
        self.zoom = 45.0
        self.sensitivity = 0.1
        self.speed = 2.5
        
        # Mouse tracking
        self.last_x = 0
        self.last_y = 0
        self.first_mouse = True
        
        # Orbital camera parameters
        self.radius = np.linalg.norm(self.position - self.target)
        self.yaw = -90.0  # In degrees
        self.pitch = 0.0  # In degrees
        
        # Set callbacks
        glfw.set_cursor_pos_callback(self.window, self.mouse_callback)
        glfw.set_scroll_callback(self.window, self.scroll_callback)
        
        # Update camera vectors
        self.update_camera_vectors()
    
    def get_view_matrix(self):
        return matrix44.create_look_at(self.position, self.target, self.up)
    
    def process_keyboard(self, delta_time):
        speed = self.speed * delta_time
        
        # Pan camera with WASD keys
        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS:
            self.target[1] += speed
            self.update_camera_position()
        if glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS:
            self.target[1] -= speed
            self.update_camera_position()
        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS:
            self.target[0] -= speed
            self.update_camera_position()
        if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS:
            self.target[0] += speed
            self.update_camera_position()
            
        # Reset view with R key
        if glfw.get_key(self.window, glfw.KEY_R) == glfw.PRESS:
            self.reset()
    
    def mouse_callback(self, window, xpos, ypos):
        if self.first_mouse:
            self.last_x = xpos
            self.last_y = ypos
            self.first_mouse = False
        
        x_offset = xpos - self.last_x
        y_offset = self.last_y - ypos  # Reversed (y-coordinates go from bottom to top)
        
        self.last_x = xpos
        self.last_y = ypos
        
        # Only rotate when right mouse button is pressed
        if glfw.get_mouse_button(self.window, glfw.MOUSE_BUTTON_RIGHT) == glfw.PRESS:
            x_offset *= self.sensitivity
            y_offset *= self.sensitivity
            
            self.yaw += x_offset
            self.pitch += y_offset
            
            # Constrain pitch to avoid flips
            if self.pitch > 89.0:
                self.pitch = 89.0
            if self.pitch < -89.0:
                self.pitch = -89.0
                
            self.update_camera_position()
    
    def scroll_callback(self, window, xoffset, yoffset):
        # Zoom in/out with scroll wheel
        self.radius -= yoffset * 0.5
        
        # Constrain zoom
        if self.radius < 1.0:
            self.radius = 1.0
        if self.radius > 100.0:
            self.radius = 100.0
            
        self.update_camera_position()
    
    def update_camera_position(self):
        # Convert spherical coordinates to Cartesian
        x = self.radius * math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        y = self.radius * math.sin(math.radians(self.pitch))
        z = self.radius * math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        
        # Update camera position
        self.position = self.target + np.array([x, y, z], dtype=np.float32)
        
        # Update camera vectors
        self.update_camera_vectors()
    
    def update_camera_vectors(self):
        # Calculate front vector
        front = np.array([
            math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)),
            math.sin(math.radians(self.pitch)),
            math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        ], dtype=np.float32)
        
        # Normalize vectors
        front = front / np.linalg.norm(front)
        
        # Re-calculate camera right and up vectors
        right = np.cross(front, np.array([0.0, 1.0, 0.0]))
        right = right / np.linalg.norm(right)
        
        self.up = np.cross(right, front)
        self.up = self.up / np.linalg.norm(self.up)
    
    def reset(self):
        # Reset to default values
        self.target = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.radius = 5.0
        self.yaw = -90.0
        self.pitch = 0.0
        self.update_camera_position()